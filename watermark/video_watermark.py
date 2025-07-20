"""
视频数字水印模块
基于逐帧图像水印处理实现视频水印
"""

import os
import tempfile
from pathlib import Path
from typing import Literal

import cv2
from moviepy.editor import VideoFileClip
from rich.console import Console
from rich.progress import track

try:
    from .image_watermark import ImageWatermark
except ImportError:
    from image_watermark import ImageWatermark

console = Console()

class VideoWatermark:
    """视频数字水印处理类"""

    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        self.image_watermark = ImageWatermark()

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1,
        frame_interval: int = 1,
        max_frames: int | None = None
    ) -> bool:
        """
        嵌入视频水印
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            watermark: 水印内容
            method: 水印算法
            password_img: 图片密码（用于blind方法）
            password_wm: 水印密码（用于blind方法）
            frame_interval: 帧间隔（每隔多少帧嵌入一次水印）
            max_frames: 最大处理帧数（用于测试）
            
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
                console.print(f"[red]错误：不支持的视频格式: {input_path.suffix}[/red]")
                return False

            # 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 使用临时目录处理
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # 提取音频（如果有）
                audio_path = None
                try:
                    video_clip = VideoFileClip(str(input_path))
                    if video_clip.audio is not None:
                        audio_path = temp_dir / "audio.wav"
                        video_clip.audio.write_audiofile(str(audio_path), verbose=False, logger=None)
                    video_clip.close()
                except Exception as e:
                    console.print(f"[yellow]警告：无法提取音频: {str(e)}[/yellow]")

                # 读取视频
                cap = cv2.VideoCapture(str(input_path))
                if not cap.isOpened():
                    console.print(f"[red]错误：无法打开视频文件: {input_path}[/red]")
                    return False

                # 获取视频属性
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                if max_frames:
                    total_frames = min(total_frames, max_frames)

                console.print(f"视频信息：{width}x{height}, {fps}FPS, {total_frames}帧")

                # 创建输出视频写入器
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(temp_dir / "temp_video.mp4"), fourcc, fps, (width, height))

                if not out.isOpened():
                    console.print("[red]错误：无法创建输出视频[/red]")
                    cap.release()
                    return False

                frame_count = 0
                watermarked_count = 0

                # 逐帧处理
                with console.status("[bold green]处理视频帧..."):
                    for frame_idx in track(range(total_frames), description="处理帧"):
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # 根据帧间隔决定是否嵌入水印
                        if frame_idx % frame_interval == 0:
                            # 保存当前帧到临时文件
                            temp_frame_path = temp_dir / f"frame_{frame_idx}.png"
                            temp_watermarked_path = temp_dir / f"watermarked_{frame_idx}.png"

                            cv2.imwrite(str(temp_frame_path), frame)

                            # 嵌入水印
                            if self.image_watermark.embed(
                                temp_frame_path,
                                temp_watermarked_path,
                                watermark,
                                method,
                                password_img,
                                password_wm
                            ):
                                # 读取水印帧
                                watermarked_frame = cv2.imread(str(temp_watermarked_path))
                                if watermarked_frame is not None:
                                    out.write(watermarked_frame)
                                    watermarked_count += 1
                                else:
                                    out.write(frame)
                            else:
                                out.write(frame)

                            # 清理临时文件
                            temp_frame_path.unlink(missing_ok=True)
                            temp_watermarked_path.unlink(missing_ok=True)
                        else:
                            # 直接写入原帧
                            out.write(frame)

                        frame_count += 1

                        if max_frames and frame_count >= max_frames:
                            break

                cap.release()
                out.release()

                # 合并音频和视频
                temp_video_path = temp_dir / "temp_video.mp4"
                if audio_path and audio_path.exists():
                    try:
                        # 使用moviepy合并音视频
                        video_clip = VideoFileClip(str(temp_video_path))
                        audio_clip = video_clip.audio
                        if audio_clip is None:
                            # 如果原视频没有音频，添加提取的音频
                            from moviepy.editor import AudioFileClip
                            audio_clip = AudioFileClip(str(audio_path))
                            final_clip = video_clip.set_audio(audio_clip)
                        else:
                            final_clip = video_clip

                        final_clip.write_videofile(
                            str(output_path),
                            codec='libx264',
                            audio_codec='aac',
                            verbose=False,
                            logger=None
                        )
                        final_clip.close()

                    except Exception as e:
                        console.print(f"[yellow]警告：音频合并失败，保存无音频版本: {str(e)}[/yellow]")
                        os.rename(str(temp_video_path), str(output_path))
                else:
                    # 没有音频，直接移动文件
                    os.rename(str(temp_video_path), str(output_path))

                console.print(f"[green]成功处理 {frame_count} 帧，其中 {watermarked_count} 帧嵌入了水印[/green]")
                console.print(f"[green]视频水印嵌入完成: {output_path}[/green]")
                return True

        except Exception as e:
            console.print(f"[red]嵌入视频水印时发生错误: {str(e)}[/red]")
            return False

    def extract(
        self,
        input_path: str | Path,
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1,
        frame_interval: int = 1,
        sample_frames: int = 10,
        wm_shape: tuple | None = None,
        output_wm_dir: str | Path | None = None
    ) -> str | None:
        """
        提取视频水印
        
        Args:
            input_path: 输入视频路径
            method: 水印算法
            password_img: 图片密码（用于blind方法）
            password_wm: 水印密码（用于blind方法）
            frame_interval: 帧间隔
            sample_frames: 采样帧数（用于提取验证）
            wm_shape: 水印形状（用于blind方法提取图像水印）
            output_wm_dir: 输出水印目录（用于blind方法提取图像水印）
            
        Returns:
            str: 提取的水印内容（多数投票结果）
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
                return None

            # 使用临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # 读取视频
                cap = cv2.VideoCapture(str(input_path))
                if not cap.isOpened():
                    console.print(f"[red]错误：无法打开视频文件: {input_path}[/red]")
                    return None

                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                # 选择要提取的帧
                frame_indices = list(range(0, min(total_frames, sample_frames * frame_interval), frame_interval))
                extracted_watermarks = []

                console.print(f"从 {len(frame_indices)} 帧中提取水印...")

                for frame_idx in track(frame_indices, description="提取帧水印"):
                    # 跳转到指定帧
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()

                    if not ret:
                        continue

                    # 保存帧到临时文件
                    temp_frame_path = temp_dir / f"extract_frame_{frame_idx}.png"
                    cv2.imwrite(str(temp_frame_path), frame)

                    # 提取水印
                    if output_wm_dir and wm_shape:
                        # 提取图像水印
                        output_wm_path = Path(output_wm_dir) / f"watermark_frame_{frame_idx}.png"
                        watermark = self.image_watermark.extract(
                            temp_frame_path,
                            method,
                            password_img,
                            password_wm,
                            wm_shape,
                            output_wm_path
                        )
                    else:
                        # 提取文字水印
                        watermark = self.image_watermark.extract(
                            temp_frame_path,
                            method,
                            password_img,
                            password_wm
                        )

                    if watermark:
                        extracted_watermarks.append(watermark)

                    # 清理临时文件
                    temp_frame_path.unlink(missing_ok=True)

                cap.release()

                if not extracted_watermarks:
                    console.print("[yellow]警告：未能从任何帧中提取到水印[/yellow]")
                    return None

                # 使用多数投票确定最终水印
                if output_wm_dir and wm_shape:
                    # 对于图像水印，返回提取的文件路径
                    console.print(f"[green]成功从 {len(extracted_watermarks)} 帧中提取图像水印[/green]")
                    return str(output_wm_dir)
                else:
                    # 对于文字水印，使用多数投票
                    from collections import Counter
                    watermark_counts = Counter(extracted_watermarks)
                    most_common_watermark = watermark_counts.most_common(1)[0][0]
                    confidence = watermark_counts[most_common_watermark] / len(extracted_watermarks)

                    console.print(f"[green]水印提取结果: {most_common_watermark} (置信度: {confidence:.2f})[/green]")
                    console.print(f"[blue]从 {len(extracted_watermarks)} 帧中提取，其中 {watermark_counts[most_common_watermark]} 帧一致[/blue]")

                    return most_common_watermark

        except Exception as e:
            console.print(f"[red]提取视频水印时发生错误: {str(e)}[/red]")
            return None

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
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1,
        frame_interval: int = 1
    ) -> int:
        """
        批量嵌入视频水印
        
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
            if self.embed(video_file, output_file, watermark, method, password_img, password_wm, frame_interval):
                success_count += 1

        console.print(f"[green]批量处理完成：成功处理 {success_count}/{len(video_files)} 个文件[/green]")
        return success_count
