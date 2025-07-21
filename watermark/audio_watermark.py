"""
音频数字水印模块
基于DCT和DWT频域变换实现音频水印
"""

from pathlib import Path
from typing import Literal

import librosa
import numpy as np
import soundfile as sf
from rich.console import Console
from rich.progress import track
from scipy.fft import dct, idct

try:
    import pywt

    PYWT_AVAILABLE = True
except ImportError:
    PYWT_AVAILABLE = False

console = Console()


class AudioWatermark:
    """音频数字水印处理类"""

    def __init__(self):
        # 只支持soundfile原生支持的格式，不需要ffmpeg
        self.supported_formats = [".wav", ".flac", ".ogg"]
        self.sample_rate = 22050  # 默认采样率
        self.frame_length = 2048  # 帧长度
        self.hop_length = 512  # 跳跃长度

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dct", "dwt", "spectrogram"] = "dct",
        alpha: float = 0.1,
        password: int = 42,
    ) -> bool:
        """
        嵌入音频水印

        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            watermark: 水印内容（字符串）
            method: 水印算法 (dct, dwt, spectrogram)
            alpha: 水印强度
            password: 用于生成伪随机序列的种子

        Returns:
            bool: 是否成功
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not input_path.exists():
                console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
                return False

            if input_path.suffix.lower() not in self.supported_formats:
                console.print(f"[red]错误：不支持的音频格式: {input_path.suffix}[/red]")
                console.print(
                    f"[yellow]支持的格式: {', '.join(self.supported_formats)}[/yellow]"
                )
                return False

            # 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 加载音频
            y, sr = librosa.load(str(input_path), sr=self.sample_rate)

            # 将水印转换为二进制
            watermark_binary = self._string_to_binary(watermark)

            # 根据方法嵌入水印
            if method == "dct":
                watermarked_audio = self._embed_dct_watermark(
                    y, watermark_binary, alpha, password
                )
            elif method == "dwt":
                watermarked_audio = self._embed_dwt_watermark(
                    y, watermark_binary, alpha, password
                )
            elif method == "spectrogram":
                watermarked_audio = self._embed_spectrogram_watermark(
                    y, watermark_binary, alpha, password
                )
            else:
                console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
                return False

            # 保存音频
            self._save_audio(watermarked_audio, output_path, sr)
            console.print(f"[green]成功嵌入音频水印到: {output_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]嵌入音频水印时发生错误: {str(e)}[/red]")
            return False

    def extract(
        self,
        input_path: str | Path,
        method: Literal["dct", "dwt", "spectrogram"] = "dct",
        watermark_length: int = 32,
        password: int = 42,
    ) -> str | None:
        """
        提取音频水印

        Args:
            input_path: 输入音频路径
            method: 水印算法
            watermark_length: 水印长度（字符数）
            password: 用于生成伪随机序列的种子

        Returns:
            str: 提取的水印内容
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
                return None

            # 加载音频
            y, sr = librosa.load(str(input_path), sr=self.sample_rate)

            # 根据方法提取水印
            if method == "dct":
                watermark_binary = self._extract_dct_watermark(
                    y, watermark_length * 8, password
                )
            elif method == "dwt":
                watermark_binary = self._extract_dwt_watermark(
                    y, watermark_length * 8, password
                )
            elif method == "spectrogram":
                watermark_binary = self._extract_spectrogram_watermark(
                    y, watermark_length * 8, password
                )
            else:
                console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
                return None

            # 将二进制转换为字符串
            watermark = self._binary_to_string(watermark_binary)
            console.print(f"[green]成功提取音频水印: {watermark}[/green]")
            return watermark

        except Exception as e:
            console.print(f"[red]提取音频水印时发生错误: {str(e)}[/red]")
            return None

    def _string_to_binary(self, text: str) -> np.ndarray:
        """将字符串转换为二进制数组"""
        binary_str = "".join(format(ord(char), "08b") for char in text)
        return np.array([int(bit) for bit in binary_str])

    def _binary_to_string(self, binary: np.ndarray) -> str:
        """将二进制数组转换为字符串"""
        binary_str = "".join(str(int(bit)) for bit in binary)
        # 确保长度是8的倍数
        binary_str = binary_str[: len(binary_str) - len(binary_str) % 8]
        chars = []
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i : i + 8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars)

    def _generate_pseudorandom_sequence(self, length: int, seed: int) -> np.ndarray:
        """生成伪随机序列"""
        np.random.seed(seed)
        return np.random.randn(length)

    def _embed_dct_watermark(
        self, audio: np.ndarray, watermark: np.ndarray, alpha: float, password: int
    ) -> np.ndarray:
        """使用DCT域嵌入水印"""
        # 分帧处理
        frames = librosa.util.frame(
            audio, frame_length=self.frame_length, hop_length=self.hop_length
        )
        watermarked_frames = frames.copy()

        # 生成伪随机序列
        pn_sequence = self._generate_pseudorandom_sequence(len(watermark), password)

        # 在每帧的DCT系数中嵌入水印
        watermark_idx = 0
        for i in range(frames.shape[1]):
            if watermark_idx >= len(watermark):
                break

            frame = frames[:, i]
            dct_coeffs = dct(frame)

            # 在中频系数中嵌入水印（避免低频和高频）
            mid_freq_start = len(dct_coeffs) // 4
            mid_freq_end = 3 * len(dct_coeffs) // 4

            for j in range(
                mid_freq_start,
                min(mid_freq_end, mid_freq_start + len(watermark) - watermark_idx),
            ):
                if watermark_idx < len(watermark):
                    # 使用扩频技术嵌入水印
                    if watermark[watermark_idx] == 1:
                        dct_coeffs[j] += (
                            alpha * abs(dct_coeffs[j]) * pn_sequence[watermark_idx]
                        )
                    else:
                        dct_coeffs[j] -= (
                            alpha * abs(dct_coeffs[j]) * pn_sequence[watermark_idx]
                        )
                    watermark_idx += 1

            watermarked_frames[:, i] = idct(dct_coeffs)

        # 重构音频信号
        watermarked_audio = np.zeros_like(audio)
        for i in range(frames.shape[1]):
            start = i * self.hop_length
            end = start + self.frame_length
            if end <= len(watermarked_audio):
                watermarked_audio[start:end] += watermarked_frames[:, i]
            else:
                watermarked_audio[start:] += watermarked_frames[
                    : len(watermarked_audio) - start, i
                ]

        return watermarked_audio

    def _extract_dct_watermark(
        self, audio: np.ndarray, watermark_length: int, password: int
    ) -> np.ndarray:
        """从DCT域提取水印"""
        # 分帧处理
        frames = librosa.util.frame(
            audio, frame_length=self.frame_length, hop_length=self.hop_length
        )

        # 生成伪随机序列
        pn_sequence = self._generate_pseudorandom_sequence(watermark_length, password)

        extracted_watermark = np.zeros(watermark_length)
        watermark_idx = 0

        for i in range(frames.shape[1]):
            if watermark_idx >= watermark_length:
                break

            frame = frames[:, i]
            dct_coeffs = dct(frame)

            # 从中频系数中提取水印
            mid_freq_start = len(dct_coeffs) // 4
            mid_freq_end = 3 * len(dct_coeffs) // 4

            for j in range(
                mid_freq_start,
                min(mid_freq_end, mid_freq_start + watermark_length - watermark_idx),
            ):
                if watermark_idx < watermark_length:
                    # 使用相关检测提取水印
                    correlation = dct_coeffs[j] * pn_sequence[watermark_idx]
                    extracted_watermark[watermark_idx] = 1 if correlation > 0 else 0
                    watermark_idx += 1

        return extracted_watermark

    def _embed_dwt_watermark(
        self, audio: np.ndarray, watermark: np.ndarray, alpha: float, password: int
    ) -> np.ndarray:
        """使用DWT域嵌入水印"""
        if not PYWT_AVAILABLE:
            console.print("[yellow]警告：PyWavelets未安装，使用DCT方法[/yellow]")
            return self._embed_dct_watermark(audio, watermark, alpha, password)

        # 小波变换
        coeffs = pywt.wavedec(audio, "db4", level=4)

        # 在详细系数中嵌入水印
        detail_coeffs = coeffs[1]  # 第一层详细系数
        pn_sequence = self._generate_pseudorandom_sequence(len(watermark), password)

        # 嵌入水印
        for i in range(min(len(watermark), len(detail_coeffs))):
            if watermark[i] == 1:
                detail_coeffs[i] += alpha * abs(detail_coeffs[i]) * pn_sequence[i]
            else:
                detail_coeffs[i] -= alpha * abs(detail_coeffs[i]) * pn_sequence[i]

        coeffs[1] = detail_coeffs

        # 逆小波变换
        watermarked_audio = pywt.waverec(coeffs, "db4")

        # 确保长度一致
        if len(watermarked_audio) > len(audio):
            watermarked_audio = watermarked_audio[: len(audio)]
        elif len(watermarked_audio) < len(audio):
            watermarked_audio = np.pad(
                watermarked_audio, (0, len(audio) - len(watermarked_audio))
            )

        return watermarked_audio

    def _extract_dwt_watermark(
        self, audio: np.ndarray, watermark_length: int, password: int
    ) -> np.ndarray:
        """从DWT域提取水印"""
        if not PYWT_AVAILABLE:
            console.print("[yellow]警告：PyWavelets未安装，使用DCT方法[/yellow]")
            return self._extract_dct_watermark(audio, watermark_length, password)

        # 小波变换
        coeffs = pywt.wavedec(audio, "db4", level=4)
        detail_coeffs = coeffs[1]

        # 生成伪随机序列
        pn_sequence = self._generate_pseudorandom_sequence(watermark_length, password)

        # 提取水印
        extracted_watermark = np.zeros(watermark_length)
        for i in range(min(watermark_length, len(detail_coeffs))):
            correlation = detail_coeffs[i] * pn_sequence[i]
            extracted_watermark[i] = 1 if correlation > 0 else 0

        return extracted_watermark

    def _embed_spectrogram_watermark(
        self, audio: np.ndarray, watermark: np.ndarray, alpha: float, password: int
    ) -> np.ndarray:
        """使用频谱图嵌入水印"""
        # 计算短时傅里叶变换
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # 生成伪随机序列
        pn_sequence = self._generate_pseudorandom_sequence(len(watermark), password)

        # 在幅度谱中嵌入水印
        watermark_idx = 0
        for t in range(magnitude.shape[1]):
            if watermark_idx >= len(watermark):
                break
            # 在中频区域嵌入
            freq_start = magnitude.shape[0] // 4
            freq_end = 3 * magnitude.shape[0] // 4

            for f in range(
                freq_start, min(freq_end, freq_start + len(watermark) - watermark_idx)
            ):
                if watermark_idx < len(watermark):
                    if watermark[watermark_idx] == 1:
                        magnitude[f, t] *= 1 + alpha * pn_sequence[watermark_idx]
                    else:
                        magnitude[f, t] *= 1 - alpha * pn_sequence[watermark_idx]
                    watermark_idx += 1

        # 重构音频
        watermarked_stft = magnitude * np.exp(1j * phase)
        watermarked_audio = librosa.istft(watermarked_stft, hop_length=self.hop_length)

        return watermarked_audio

    def _extract_spectrogram_watermark(
        self, audio: np.ndarray, watermark_length: int, password: int
    ) -> np.ndarray:
        """从频谱图提取水印"""
        # 计算短时傅里叶变换
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        magnitude = np.abs(stft)

        # 生成伪随机序列
        pn_sequence = self._generate_pseudorandom_sequence(watermark_length, password)

        # 提取水印
        extracted_watermark = np.zeros(watermark_length)
        watermark_idx = 0

        for t in range(magnitude.shape[1]):
            if watermark_idx >= watermark_length:
                break
            freq_start = magnitude.shape[0] // 4
            freq_end = 3 * magnitude.shape[0] // 4

            for f in range(
                freq_start, min(freq_end, freq_start + watermark_length - watermark_idx)
            ):
                if watermark_idx < watermark_length:
                    # 使用相关检测
                    correlation = magnitude[f, t] * pn_sequence[watermark_idx]
                    extracted_watermark[watermark_idx] = (
                        1 if correlation > np.mean(magnitude[f, :]) else 0
                    )
                    watermark_idx += 1

        return extracted_watermark

    def _save_audio(self, audio: np.ndarray, output_path: Path, sample_rate: int):
        """保存音频文件（使用soundfile，无需外部依赖）"""
        try:
            # 确保音频数据在有效范围内
            audio = np.clip(audio, -1.0, 1.0)

            # 直接使用soundfile保存，支持多种格式且无需外部依赖
            sf.write(str(output_path), audio, sample_rate)

        except Exception as e:
            console.print(f"[red]保存音频文件失败: {str(e)}[/red]")
            raise

    def batch_embed(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        watermark: str,
        method: Literal["dct", "dwt", "spectrogram"] = "dct",
        alpha: float = 0.1,
        password: int = 42,
    ) -> int:
        """
        批量嵌入音频水印

        Returns:
            int: 成功处理的文件数量
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            console.print(f"[red]错误：输入目录不存在: {input_dir}[/red]")
            return 0

        # 获取所有音频文件
        audio_files = []
        for ext in self.supported_formats:
            audio_files.extend(input_dir.glob(f"*{ext}"))
            audio_files.extend(input_dir.glob(f"*{ext.upper()}"))

        if not audio_files:
            console.print(f"[yellow]警告：在 {input_dir} 中未找到支持的音频文件[/yellow]")
            return 0

        success_count = 0
        for audio_file in track(audio_files, description="批量处理音频..."):
            output_file = output_dir / audio_file.name
            if self.embed(audio_file, output_file, watermark, method, alpha, password):
                success_count += 1

        console.print(f"[green]批量处理完成：成功处理 {success_count}/{len(audio_files)} 个文件[/green]")
        return success_count
