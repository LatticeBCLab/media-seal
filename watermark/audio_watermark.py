from pathlib import Path
from typing import Literal

import librosa
import numpy as np
import pywt
import soundfile as sf
from rich.console import Console
from rich.progress import track
from scipy.fft import dct, idct

console = Console()


class AudioWatermark:
    """音频数字水印处理类 - 基于频域变换的符号编码水印算法"""

    def __init__(self):
        self.supported_formats = [".wav", ".flac", ".ogg", ".mp3", ".m4a", ".aac"]
        self.supported_methods = ["dct", "dwt"]

    def _validate_input_path(self, input_path: Path) -> bool:
        """验证输入文件路径"""
        if not input_path.exists():
            console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
            return False

        if input_path.suffix.lower() not in self.supported_formats:
            console.print(f"[red]错误：不支持的音频格式: {input_path.suffix}[/red]")
            console.print(
                f"[yellow]支持的格式: {', '.join(self.supported_formats)}[/yellow]"
            )
            return False

        return True

    def _validate_method(self, method: str) -> bool:
        """验证水印方法"""
        if method not in self.supported_methods:
            console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
            return False
        return True

    def _text_to_bits(self, text: str) -> str:
        """字符串转二进制"""
        return "".join(format(ord(c), "08b") for c in text)

    def _bits_to_text(self, bits: str) -> str:
        """二进制转字符串"""
        chars = [bits[i : i + 8] for i in range(0, len(bits), 8)]
        return "".join(chr(int(c, 2)) for c in chars if len(c) == 8)

    def _load_audio(self, file_path: Path) -> tuple[np.ndarray, int]:
        """加载任意格式音频，返回numpy数组和采样率"""
        try:
            samples, sample_rate = librosa.load(str(file_path), sr=None, mono=True)
            console.print(f"[cyan]音频加载成功: {file_path.name}[/cyan]")
            return samples, sample_rate
        except Exception as e:
            console.print(f"[red]加载音频文件失败: {str(e)}[/red]")
            raise

    def _save_audio(self, samples: np.ndarray, sample_rate: int, file_path: Path) -> None:
        """保存numpy数组为音频文件"""
        try:
            samples = np.clip(samples, -1.0, 1.0)
            sf.write(str(file_path), samples, sample_rate)
            console.print(f"[cyan]音频保存成功: {file_path.name}[/cyan]")
        except Exception as e:
            console.print(f"[red]保存音频文件失败: {str(e)}[/red]")
            raise

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dct", "dwt"] = "dwt",
    ) -> bool:
        """
        嵌入音频水印 - 使用频域变换的符号编码方法

        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            watermark: 水印内容（字符串）
            method: 水印算法 (dct: 离散余弦变换, dwt: 离散小波变换)

        Returns:
            bool: 是否成功
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not self._validate_input_path(input_path):
                return False
            if not self._validate_method(method):
                return False

            output_path.parent.mkdir(parents=True, exist_ok=True)

            return self._embed_watermark(input_path, output_path, watermark, method)

        except Exception as e:
            console.print(f"[red]嵌入音频水印时发生错误: {str(e)}[/red]")
            return False

    def _embed_watermark(
        self, input_path: Path, output_path: Path, watermark: str, method: str
    ) -> bool:
        """业务逻辑：嵌入水印"""
        samples, sample_rate = self._load_audio(input_path)
        console.print(
            f"[blue]加载音频: 长度={len(samples)}, 采样率={sample_rate}Hz[/blue]"
        )

        if method == "dct":
            watermarked_samples = self._embed_watermark_dct(samples, watermark)
        elif method == "dwt":
            watermarked_samples = self._embed_watermark_dwt(samples, watermark)
        else:
            console.print(f"[red]不支持的方法: {method}[/red]")
            return False

        self._save_audio(watermarked_samples, sample_rate, output_path)
        console.print(f"[green]成功嵌入音频水印到: {output_path}[/green]")
        return True

    def extract(
        self,
        input_path: str | Path,
        watermark_length: int,
        method: Literal["dct", "dwt"] = "dwt",
    ) -> str | None:
        """
        提取音频水印 - 基于频域变换的符号解码方法

        Args:
            input_path: 输入音频路径
            watermark_length: 水印长度（字符数）
            method: 水印算法 (dct: 离散余弦变换, dwt: 离散小波变换)

        Returns:
            str: 提取的水印内容
        """
        try:
            input_path = Path(input_path)

            if not self._validate_input_path(input_path):
                return None
            if not self._validate_method(method):
                return None

            return self._extract_watermark(input_path, method, watermark_length)

        except Exception as e:
            console.print(f"[red]提取音频水印时发生错误: {str(e)}[/red]")
            return None

    def _extract_watermark(
        self, input_path: Path, method: str, watermark_length: int
    ) -> str | None:
        """业务逻辑：提取水印"""
        samples, sample_rate = self._load_audio(input_path)
        console.print(
            f"[blue]加载音频: 长度={len(samples)}, 采样率={sample_rate}Hz[/blue]"
        )

        if method == "dct":
            watermark = self._extract_watermark_dct(samples, watermark_length)
        elif method == "dwt":
            watermark = self._extract_watermark_dwt(samples, watermark_length)
        else:
            console.print(f"[red]不支持的方法: {method}[/red]")
            return None

        console.print(f"[green]成功提取音频水印: {watermark}[/green]")
        return watermark

    def _embed_watermark_dwt(self, samples: np.ndarray, watermark: str) -> np.ndarray:
        """
        使用离散小波变换(DWT)域嵌入水印

        算法原理：
        1. 对音频信号进行Haar小波2级分解，得到低频近似系数ca2
        2. 将水印文本转换为二进制位序列
        3. 通过修改ca2系数的符号来编码水印：正值表示'1'，负值表示'0'
        4. 重构信号获得含水印的音频

        优势：频域嵌入具有较好的抗压缩性和隐蔽性
        """
        console.print(f"[blue]DWT嵌入水印: '{watermark}'[/blue]")
        watermark_bits = self._text_to_bits(watermark)

        coeffs = pywt.wavedec(samples, "haar", level=2)
        ca2, cd2, cd1 = coeffs
        console.print(
            f"[blue]小波分解完成，ca2长度={len(ca2)}, 水印长度={len(watermark_bits)}位[/blue]"
        )

        if len(watermark_bits) > len(ca2):
            raise ValueError(
                f"水印过大，无法嵌入。水印需要{len(watermark_bits)}位，但只有{len(ca2)}个系数"
            )

        # 修改低频近似系数ca2 - 使用符号编码
        ca2_modified = ca2.copy()
        modification_strength = 0.01  # 修改强度

        for i, bit in enumerate(watermark_bits):
            original_coeff = ca2_modified[i]

            if bit == "1":
                # 水印位为1：确保系数为正值
                if original_coeff >= 0:
                    ca2_modified[i] = abs(original_coeff) + modification_strength
                else:
                    ca2_modified[i] = modification_strength
            else:
                # 水印位为0：确保系数为负值
                if original_coeff > modification_strength:
                    ca2_modified[i] = -(abs(original_coeff))
                else:
                    ca2_modified[i] = -modification_strength

        # 重构信号
        coeffs_modified = [ca2_modified, cd2, cd1]
        watermarked_samples = pywt.waverec(coeffs_modified, "haar")

        # 确保长度一致
        if len(watermarked_samples) != len(samples):
            watermarked_samples = watermarked_samples[: len(samples)]

        console.print(
            f"[blue]DWT水印嵌入完成，修改了{len(watermark_bits)}个系数[/blue]"
        )
        return watermarked_samples.astype(np.float32)

    def _extract_watermark_dwt(self, samples: np.ndarray, length: int) -> str:
        """
        从离散小波变换(DWT)域提取水印

        算法原理：
        1. 对含水印音频进行相同的Haar小波2级分解
        2. 提取低频近似系数ca2
        3. 根据系数符号解码水印：正值解码为'1'，负值解码为'0'
        4. 将二进制位序列转换回文本
        """
        console.print(
            f"[blue]DWT提取水印，期望长度: {length}字符({length * 8}位)[/blue]"
        )
        total_bits = length * 8

        coeffs = pywt.wavedec(samples, "haar", level=2)
        ca2, _, _ = coeffs

        if total_bits > len(ca2):
            console.print(
                f"[yellow]警告: 需要{total_bits}位，但只有{len(ca2)}个系数，将提取所有可用位[/yellow]"
            )
            total_bits = len(ca2)

        # 提取水印位 - 基于系数符号
        bits = []
        for i in range(total_bits):
            coeff = ca2[i]
            # 正值表示水印位1，负值表示水印位0
            bit = "1" if coeff > 0 else "0"
            bits.append(bit)

        bits_str = "".join(bits)

        try:
            watermark = self._bits_to_text(bits_str)
            console.print(f"[blue]DWT水印提取完成: '{watermark}'[/blue]")
            return watermark
        except Exception as e:
            console.print(f"[yellow]解码失败: {str(e)}，返回二进制字符串[/yellow]")
            return bits_str

    def _embed_watermark_dct(self, samples: np.ndarray, watermark: str) -> np.ndarray:
        """
        使用离散余弦变换(DCT)域嵌入水印

        算法原理：
        1. 对音频信号进行DCT变换，得到频域系数
        2. 将水印文本转换为二进制位序列
        3. 通过修改DCT系数的符号来编码水印：正值表示'1'，负值表示'0'
        4. 进行逆DCT变换重构含水印的音频信号

        优势：DCT域嵌入对音频质量影响小，水印提取稳定
        """
        console.print(f"[blue]DCT嵌入水印: '{watermark}'[/blue]")

        watermark_bits = self._text_to_bits(watermark)

        # DCT变换
        dct_coeffs = dct(samples, norm="ortho")

        console.print(
            f"[blue]DCT变换完成，系数长度={len(dct_coeffs)}, 水印长度={len(watermark_bits)}位[/blue]"
        )

        if len(watermark_bits) > len(dct_coeffs):
            raise ValueError(
                f"水印过大，无法嵌入。水印需要{len(watermark_bits)}位，但只有{len(dct_coeffs)}个系数"
            )

        # 修改DCT系数 - 使用符号编码
        dct_modified = dct_coeffs.copy()
        modification_strength = 0.01  # 修改强度

        for i, bit in enumerate(watermark_bits):
            original_coeff = dct_modified[i]

            if bit == "1":
                # 水印位为1：确保系数为正值
                if original_coeff >= 0:
                    dct_modified[i] = abs(original_coeff) + modification_strength
                else:
                    dct_modified[i] = modification_strength
            else:
                # 水印位为0：确保系数为负值
                if original_coeff > modification_strength:
                    dct_modified[i] = -(abs(original_coeff))
                else:
                    dct_modified[i] = -modification_strength

        # 逆DCT变换
        watermarked_samples = idct(dct_modified, norm="ortho")

        console.print(
            f"[blue]DCT水印嵌入完成，修改了{len(watermark_bits)}个系数[/blue]"
        )
        return watermarked_samples.astype(np.float32)

    def _extract_watermark_dct(self, samples: np.ndarray, length: int) -> str:
        """
        从离散余弦变换(DCT)域提取水印

        算法原理：
        1. 对含水印音频进行DCT变换
        2. 提取DCT系数
        3. 根据系数符号解码水印：正值解码为'1'，负值解码为'0'
        4. 将二进制位序列转换回文本
        """
        console.print(
            f"[blue]DCT提取水印，期望长度: {length}字符({length * 8}位)[/blue]"
        )

        total_bits = length * 8

        # DCT变换
        dct_coeffs = dct(samples, norm="ortho")

        if total_bits > len(dct_coeffs):
            console.print(
                f"[yellow]警告: 需要{total_bits}位，但只有{len(dct_coeffs)}个系数，将提取所有可用位[/yellow]"
            )
            total_bits = len(dct_coeffs)

        # 提取水印位 - 基于系数符号
        bits = []
        for i in range(total_bits):
            coeff = dct_coeffs[i]
            # 正值表示水印位1，负值表示水印位0
            bit = "1" if coeff > 0 else "0"
            bits.append(bit)

        bits_str = "".join(bits)

        try:
            watermark = self._bits_to_text(bits_str)
            console.print(f"[blue]DCT水印提取完成: '{watermark}'[/blue]")
            return watermark
        except Exception as e:
            console.print(f"[yellow]解码失败: {str(e)}，返回二进制字符串[/yellow]")
            return bits_str

    def batch_embed(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        watermark: str,
        method: Literal["dct", "dwt"] = "dwt",
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
            console.print(
                f"[yellow]警告：在 {input_dir} 中未找到支持的音频文件[/yellow]"
            )
            return 0

        success_count = 0
        for audio_file in track(audio_files, description="批量处理音频..."):
            output_file = output_dir / audio_file.name
            if self.embed(audio_file, output_file, watermark, method):
                success_count += 1

        console.print(
            f"[green]批量处理完成：成功处理 {success_count}/{len(audio_files)} 个文件[/green]"
        )
        return success_count
