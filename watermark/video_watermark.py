import tempfile
from pathlib import Path
from typing import Literal

import cv2
import imageio
from rich.console import Console
from rich.progress import track

from .image_watermark import ImageWatermark

console = Console()


class VideoWatermark:
    """视频数字水印处理类"""

    def __init__(self):
        self.supported_formats = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
        self.supported_methods = ["dwtDct", "dwtDctSvd"]
        self.image_watermark = ImageWatermark()

    def _validate_input_path(self, input_path: Path) -> bool:
        """验证输入文件路径"""
        if not input_path.exists():
            console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
            return False

        if input_path.suffix.lower() not in self.supported_formats:
            console.print(f"[red]错误：不支持的视频格式: {input_path.suffix}[/red]")
            return False

        return True

    def _validate_method(self, method: str) -> bool:
        """验证水印方法"""
        if method not in self.supported_methods:
            console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
            return False
        return True

    def _validate_embed_params(
        self,
        input_path: Path,
        watermark: str,
        method: str,
        frame_interval: int,
    ) -> bool:
        """验证嵌入参数"""
        if not self._validate_input_path(input_path):
            return False
        if not self._validate_method(method):
            return False
        if not watermark.strip():
            console.print("[red]错误：水印内容不能为空[/red]")
            return False
        if frame_interval < 1:
            console.print("[red]错误：帧间隔必须大于0[/red]")
            return False
        return True

    def _validate_extract_params(
        self,
        input_path: Path,
        extract_length: int,
        method: str,
        frame_interval: int,
        sample_frames: int,
    ) -> bool:
        """验证提取参数"""
        if not self._validate_input_path(input_path):
            return False
        if not self._validate_method(method):
            return False
        if extract_length < 1:
            console.print("[red]错误：提取长度必须大于0[/red]")
            return False
        if frame_interval < 1:
            console.print("[red]错误：帧间隔必须大于0[/red]")
            return False
        if sample_frames < 1:
            console.print("[red]错误：采样帧数必须大于0[/red]")
            return False
        return True

    def _initialize_video_reader(self, input_path: Path):
        """初始化视频读取器"""
        try:
            reader = imageio.get_reader(str(input_path))
            meta = reader.get_meta_data()
            fps = meta.get("fps", 30)

            first_frame = reader.get_data(0)
            height, width = first_frame.shape[:2]

            try:
                total_frames = reader.count_frames()
            except (RuntimeError, OSError, AttributeError):
                duration = meta.get("duration", 10)
                total_frames = int(duration * fps)

            return reader, fps, width, height, total_frames

        except Exception as e:
            console.print(f"[red]错误：无法读取视频文件: {str(e)}[/red]")
            return None, None, None, None, None

    def _create_video_writer(self, temp_video_path: Path, fps: float):
        """创建视频写入器"""
        try:
            writer = imageio.get_writer(
                str(temp_video_path),
                fps=fps,
                codec="libx264",
                quality=8,
                macro_block_size=1,
            )
            return writer
        except Exception as e:
            console.print(f"[red]错误：无法创建输出视频写入器: {str(e)}[/red]")
            return None

    def _process_video_frames(
        self,
        reader,
        writer,
        temp_dir: Path,
        watermark: str,
        method: str,
        frame_interval: int,
        total_frames: int,
    ) -> tuple[int, int]:
        """处理视频帧并嵌入水印"""
        frame_count = 0
        watermarked_count = 0

        for frame_idx in track(range(total_frames), description="处理帧"):
            try:
                frame = reader.get_data(frame_idx)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception as e:
                console.print(
                    f"[yellow]警告：无法读取第{frame_idx}帧: {str(e)}[/yellow]"
                )
                break

            if frame_idx % frame_interval == 0:
                temp_frame_path = temp_dir / f"frame_{frame_idx}.png"
                temp_watermarked_path = temp_dir / f"watermarked_{frame_idx}.png"

                cv2.imwrite(str(temp_frame_path), frame_bgr)

                if self.image_watermark.embed(
                    temp_frame_path, temp_watermarked_path, watermark, method
                ):
                    watermarked_frame = cv2.imread(str(temp_watermarked_path))
                    if watermarked_frame is not None:
                        watermarked_frame_rgb = cv2.cvtColor(
                            watermarked_frame, cv2.COLOR_BGR2RGB
                        )
                        writer.append_data(watermarked_frame_rgb)
                        watermarked_count += 1
                    else:
                        writer.append_data(frame)
                else:
                    writer.append_data(frame)

                temp_frame_path.unlink(missing_ok=True)
                temp_watermarked_path.unlink(missing_ok=True)
            else:
                writer.append_data(frame)

            frame_count += 1

        return frame_count, watermarked_count

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
        frame_interval: int = 1,
        max_frames: int | None = None,
    ) -> bool:
        """
        嵌入视频水印

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            watermark: 水印内容
            method: 水印算法
            frame_interval: 帧间隔（每隔多少帧嵌入一次水印）
            max_frames: 最大处理帧数（用于测试）

        Returns:
            bool: 是否成功
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not self._validate_embed_params(
                input_path, watermark, method, frame_interval
            ):
                return False

            output_path.parent.mkdir(parents=True, exist_ok=True)

            return self._embed_watermark(
                input_path, output_path, watermark, method, frame_interval, max_frames
            )

        except Exception as e:
            console.print(f"[red]嵌入视频水印时发生错误: {str(e)}[/red]")
            return False

    def _embed_watermark(
        self,
        input_path: Path,
        output_path: Path,
        watermark: str,
        method: str,
        frame_interval: int,
        max_frames: int | None,
    ) -> bool:
        """执行水印嵌入的核心逻辑"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            reader, fps, width, height, total_frames = self._initialize_video_reader(
                input_path
            )
            if reader is None:
                return False

            if max_frames:
                total_frames = min(total_frames, max_frames)

            console.print(f"视频信息：{width}x{height}, {fps}FPS, {total_frames}帧")

            temp_video_path = temp_dir / "temp_video.mp4"
            writer = self._create_video_writer(temp_video_path, fps)
            if writer is None:
                reader.close()
                return False

            try:
                with console.status("[bold green]处理视频帧..."):
                    frame_count, watermarked_count = self._process_video_frames(
                        reader,
                        writer,
                        temp_dir,
                        watermark,
                        method,
                        frame_interval,
                        total_frames,
                    )
            finally:
                reader.close()
                writer.close()

            if temp_video_path.exists():
                success = self._merge_audio_video(
                    input_path, temp_video_path, output_path
                )
                if success:
                    console.print(f"[green]成功嵌入视频水印到: {output_path}[/green]")
                    console.print(
                        f"[blue]处理了 {frame_count} 帧，其中 {watermarked_count} 帧嵌入了水印[/blue]"
                    )
                    return True
                else:
                    console.print("[red]错误：音频合并失败[/red]")
                    return False
            else:
                console.print("[red]错误：临时视频文件未生成[/red]")
                return False

    def _merge_audio_video(
        self, original_video: Path, watermarked_video: Path, output_path: Path
    ) -> bool:
        """合并原视频的音频和水印视频"""
        try:
            # 方案1：使用imageio内置的ffmpeg
            try:
                import subprocess

                import imageio_ffmpeg as ffmpeg

                ffmpeg_path = ffmpeg.get_ffmpeg_exe()

                # 使用ffmpeg合并音视频
                cmd = [
                    ffmpeg_path,
                    "-i",
                    str(watermarked_video),  # 水印视频（无音频）
                    "-i",
                    str(original_video),  # 原视频（有音频）
                    "-c:v",
                    "copy",  # 复制视频流
                    "-c:a",
                    "aac",  # 音频编码为aac
                    "-map",
                    "0:v:0",  # 使用第一个输入的视频
                    "-map",
                    "1:a:0",  # 使用第二个输入的音频
                    "-shortest",  # 以最短流为准
                    "-y",  # 覆盖输出文件
                    str(output_path),
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    console.print("[green]音频合并成功[/green]")
                    return True
                else:
                    console.print(f"[yellow]ffmpeg合并失败: {result.stderr}[/yellow]")

            except (ImportError, Exception) as e:
                console.print(f"[yellow]ffmpeg方案失败: {str(e)}[/yellow]")

            # 方案2：降级处理 - 直接复制无音频的视频
            console.print("[yellow]警告：无法合并音频，输出视频将没有声音[/yellow]")
            import shutil

            shutil.move(str(watermarked_video), str(output_path))
            return True

        except Exception as e:
            console.print(f"[red]音频合并过程发生错误: {str(e)}[/red]")
            return False

    def _extract_frame_watermarks(
        self, cap, temp_dir: Path, frame_indices: list, extract_length: int, method: str
    ) -> list[str]:
        """从指定帧中提取水印"""
        extracted_watermarks = []

        for frame_idx in track(frame_indices, description="提取帧水印"):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                continue

            temp_frame_path = temp_dir / f"extract_frame_{frame_idx}.png"
            cv2.imwrite(str(temp_frame_path), frame)

            watermark = self.image_watermark.extract(
                temp_frame_path, extract_length, method
            )

            if watermark:
                extracted_watermarks.append(watermark)

            temp_frame_path.unlink(missing_ok=True)

        return extracted_watermarks

    def _calculate_majority_vote(
        self, extracted_watermarks: list[str]
    ) -> tuple[str, float]:
        """使用多数投票确定最终水印"""
        from collections import Counter

        watermark_counts = Counter(extracted_watermarks)
        most_common_watermark = watermark_counts.most_common(1)[0][0]
        confidence = watermark_counts[most_common_watermark] / len(extracted_watermarks)

        console.print(
            f"[green]水印提取结果: {most_common_watermark} (置信度: {confidence:.2f})[/green]"
        )
        console.print(
            f"[blue]从 {len(extracted_watermarks)} 帧中提取，其中 {watermark_counts[most_common_watermark]} 帧一致[/blue]"
        )

        return most_common_watermark, confidence

    def extract(
        self,
        input_path: str | Path,
        extract_length: int,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
        frame_interval: int = 1,
        sample_frames: int = 10,
    ) -> str | None:
        """
        提取视频水印

        Args:
            input_path: 输入视频路径
            extract_length: 提取水印长度（字节数）
            method: 水印算法
            frame_interval: 帧间隔
            sample_frames: 采样帧数（用于提取验证）

        Returns:
            str: 提取的水印内容（多数投票结果）
        """
        try:
            input_path = Path(input_path)

            if not self._validate_extract_params(
                input_path, extract_length, method, frame_interval, sample_frames
            ):
                return None

            return self._extract_watermark_from_video(
                input_path, extract_length, method, frame_interval, sample_frames
            )

        except Exception as e:
            console.print(f"[red]提取视频水印时发生错误: {str(e)}[/red]")
            return None

    def _extract_watermark_from_video(
        self,
        input_path: Path,
        extract_length: int,
        method: str,
        frame_interval: int,
        sample_frames: int,
    ) -> str | None:
        """从视频中提取水印的核心逻辑"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                console.print(f"[red]错误：无法打开视频文件: {input_path}[/red]")
                return None

            try:
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                frame_indices = list(
                    range(
                        0,
                        min(total_frames, sample_frames * frame_interval),
                        frame_interval,
                    )
                )
                console.print(f"从 {len(frame_indices)} 帧中提取水印...")

                extracted_watermarks = self._extract_frame_watermarks(
                    cap, temp_dir, frame_indices, extract_length, method
                )

                if not extracted_watermarks:
                    console.print("[yellow]警告：未能从任何帧中提取到水印[/yellow]")
                    return None

                most_common_watermark, _ = self._calculate_majority_vote(
                    extracted_watermarks
                )
                return most_common_watermark

            finally:
                cap.release()

    def get_video_info(self, video_path: str | Path) -> dict | None:
        """获取视频信息"""
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                return None

            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return None

            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(cap.get(cv2.CAP_PROP_FPS)),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / int(cap.get(cv2.CAP_PROP_FPS))
            }

            cap.release()
            return info

        except Exception:
            return None

    def extract_frames(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        frame_interval: int = 30,
        max_frames: int | None = None
    ) -> int:
        """
        提取视频帧到指定目录

        Args:
            video_path: 视频路径
            output_dir: 输出目录
            frame_interval: 帧间隔
            max_frames: 最大提取帧数

        Returns:
            int: 实际提取的帧数
        """
        try:
            video_path = Path(video_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                console.print(f"[red]错误：无法打开视频文件: {video_path}[/red]")
                return 0

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            extracted_count = 0

            for frame_idx in range(0, total_frames, frame_interval):
                if max_frames and extracted_count >= max_frames:
                    break

                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    break

                frame_filename = output_dir / f"frame_{frame_idx:06d}.png"
                cv2.imwrite(str(frame_filename), frame)
                extracted_count += 1

            cap.release()
            console.print(f"[green]成功提取 {extracted_count} 帧到 {output_dir}[/green]")
            return extracted_count

        except Exception as e:
            console.print(f"[red]提取视频帧时发生错误: {str(e)}[/red]")
            return 0

    def batch_embed(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
        frame_interval: int = 1,
    ) -> int:
        """
        批量嵌入视频水印

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            watermark: 水印内容
            method: 水印算法
            frame_interval: 帧间隔

        Returns:
            int: 成功处理的文件数量
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            console.print(f"[red]错误：输入目录不存在: {input_dir}[/red]")
            return 0

        # 获取所有视频文件
        video_files = []
        for ext in self.supported_formats:
            video_files.extend(input_dir.glob(f"*{ext}"))
            video_files.extend(input_dir.glob(f"*{ext.upper()}"))

        if not video_files:
            console.print(f"[yellow]警告：在 {input_dir} 中未找到支持的视频文件[/yellow]")
            return 0

        success_count = 0
        for video_file in track(video_files, description="批量处理视频..."):
            output_file = output_dir / video_file.name
            if self.embed(video_file, output_file, watermark, method, frame_interval):
                success_count += 1

        console.print(f"[green]批量处理完成：成功处理 {success_count}/{len(video_files)} 个文件[/green]")
        return success_count
