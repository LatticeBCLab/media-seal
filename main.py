import functools
import time
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from watermark import AudioWatermark, ImageWatermark, VideoWatermark

console = Console()

def timing_decorator(operation_name: str):
    """时间统计装饰器"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            console.print(f"[blue]开始{operation_name}...[/blue]")

            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed = end_time - start_time

                console.print(f"[green]✓ {operation_name}完成[/green]")
                console.print(f"[yellow]耗时: {elapsed:.2f} 秒[/yellow]")
                return result
            except Exception:
                end_time = time.time()
                elapsed = end_time - start_time
                console.print(
                    f"[red]✗ {operation_name}失败 (耗时: {elapsed:.2f} 秒)[/red]"
                )
                raise

        return wrapper

    return decorator


app = typer.Typer(
    name="media-seal",
    help="数字水印工具 - 支持图像、音频、视频的版权保护",
    rich_markup_mode="rich",
)

image_app = typer.Typer(name="image", help="图像水印功能")
audio_app = typer.Typer(name="audio", help="音频水印功能")
video_app = typer.Typer(name="video", help="视频水印功能")

app.add_typer(image_app)
app.add_typer(audio_app)
app.add_typer(video_app)


@image_app.command("embed")
@timing_decorator("图像水印嵌入")
def image_embed(
    input_path: Annotated[Path, typer.Argument(help="输入图片路径")],
    output_path: Annotated[Path, typer.Argument(help="输出图片路径")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
):
    """嵌入图像水印"""
    watermarker = ImageWatermark()
    success = watermarker.embed(input_path, output_path, watermark, method)
    if not success:
        raise typer.Exit(1)


@image_app.command("extract")
@timing_decorator("图像水印提取")
def image_extract(
    input_path: Annotated[Path, typer.Argument(help="输入图片路径")],
    extract_length: Annotated[int, typer.Argument(help="提取水印长度（字节数）")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
):
    """提取图像水印"""
    watermarker = ImageWatermark()
    result = watermarker.extract(input_path, extract_length, method)
    if result is None:
        raise typer.Exit(1)


@image_app.command("batch-embed")
@timing_decorator("批量图像水印嵌入")
def image_batch_embed(
    input_dir: Annotated[Path, typer.Argument(help="输入目录")],
    output_dir: Annotated[Path, typer.Argument(help="输出目录")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
):
    """批量嵌入图像水印"""
    watermarker = ImageWatermark()
    success_count = watermarker.batch_embed(input_dir, output_dir, watermark, method)
    if success_count == 0:
        raise typer.Exit(1)


# 音频水印命令
@audio_app.command("embed")
@timing_decorator("音频水印嵌入")
def audio_embed(
    input_path: Annotated[Path, typer.Argument(help="输入音频路径")],
    output_path: Annotated[Path, typer.Argument(help="输出音频路径")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option("dct", "--method", "-m", help="水印算法: dct, dwt"),
):
    """嵌入音频水印"""
    watermarker = AudioWatermark()
    success = watermarker.embed(input_path, output_path, watermark, method)
    if not success:
        raise typer.Exit(1)


@audio_app.command("extract")
@timing_decorator("音频水印提取")
def audio_extract(
    input_path: Annotated[Path, typer.Argument(help="输入音频路径")],
    watermark_length: Annotated[int, typer.Argument(help="提取水印长度（字符数）")],
    method: str = typer.Option("dct", "--method", "-m", help="水印算法: dct, dwt"),
):
    """提取音频水印"""
    watermarker = AudioWatermark()
    result = watermarker.extract(input_path, watermark_length, method)
    if result is None:
        raise typer.Exit(1)


@audio_app.command("batch-embed")
@timing_decorator("批量音频水印嵌入")
def audio_batch_embed(
    input_dir: Annotated[Path, typer.Argument(help="输入目录")],
    output_dir: Annotated[Path, typer.Argument(help="输出目录")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option("dct", "--method", "-m", help="水印算法: dct, dwt"),
):
    """批量嵌入音频水印"""
    watermarker = AudioWatermark()
    success_count = watermarker.batch_embed(input_dir, output_dir, watermark, method)
    if success_count == 0:
        raise typer.Exit(1)


# 视频水印命令
@video_app.command("embed")
@timing_decorator("视频水印嵌入")
def video_embed(
    input_path: Annotated[Path, typer.Argument(help="输入视频路径")],
    output_path: Annotated[Path, typer.Argument(help="输出视频路径")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
    frame_interval: int = typer.Option(
        1, "--frame-interval", help="帧间隔（每隔多少帧嵌入一次）"
    ),
    max_frames: int | None = typer.Option(
        None, "--max-frames", help="最大处理帧数（用于测试）"
    ),
):
    """嵌入视频水印"""
    watermarker = VideoWatermark()
    success = watermarker.embed(
        input_path,
        output_path,
        watermark,
        method,
        frame_interval,
        max_frames,
    )
    if not success:
        raise typer.Exit(1)


@video_app.command("extract")
@timing_decorator("视频水印提取")
def video_extract(
    input_path: Annotated[Path, typer.Argument(help="输入视频路径")],
    extract_length: Annotated[int, typer.Argument(help="提取水印长度（字节数）")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
    frame_interval: int = typer.Option(1, "--frame-interval", help="帧间隔"),
    sample_frames: int = typer.Option(10, "--sample-frames", help="采样帧数"),
):
    """提取视频水印"""
    watermarker = VideoWatermark()
    result = watermarker.extract(
        input_path,
        extract_length,
        method,
        frame_interval,
        sample_frames,
    )
    if result is None:
        raise typer.Exit(1)


@video_app.command("info")
def video_info(video_path: Annotated[Path, typer.Argument(help="视频路径")]):
    """显示视频信息"""
    watermarker = VideoWatermark()
    info = watermarker.get_video_info(video_path)

    if info is None:
        console.print("[red]错误：无法读取视频信息[/red]")
        raise typer.Exit(1)

    table = Table(title=f"视频信息: {video_path.name}")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="magenta")

    table.add_row("分辨率", f"{info['width']} x {info['height']}")
    table.add_row("帧率", f"{info['fps']} FPS")
    table.add_row("总帧数", str(info["frame_count"]))
    table.add_row("时长", f"{info['duration']:.2f} 秒")

    console.print(table)


@video_app.command("extract-frames")
@timing_decorator("视频帧提取")
def video_extract_frames(
    video_path: Annotated[Path, typer.Argument(help="视频路径")],
    output_dir: Annotated[Path, typer.Argument(help="输出目录")],
    frame_interval: int = typer.Option(30, "--interval", help="帧间隔"),
    max_frames: int | None = typer.Option(None, "--max-frames", help="最大提取帧数"),
):
    """提取视频帧"""
    watermarker = VideoWatermark()
    count = watermarker.extract_frames(
        video_path, output_dir, frame_interval, max_frames
    )
    if count == 0:
        raise typer.Exit(1)


@video_app.command("batch-embed")
@timing_decorator("批量视频水印嵌入")
def video_batch_embed(
    input_dir: Annotated[Path, typer.Argument(help="输入目录")],
    output_dir: Annotated[Path, typer.Argument(help="输出目录")],
    watermark: Annotated[str, typer.Argument(help="水印内容")],
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd"
    ),
    frame_interval: int = typer.Option(1, "--frame-interval", help="帧间隔"),
):
    """批量嵌入视频水印"""
    watermarker = VideoWatermark()
    success_count = watermarker.batch_embed(
        input_dir,
        output_dir,
        watermark,
        method,
        frame_interval,
    )
    if success_count == 0:
        raise typer.Exit(1)


# 通用命令
@app.command("version")
def version():
    """显示版本信息"""
    rprint("[bold blue]Media Seal - 数字水印工具[/bold blue]")
    rprint("[green]版本: 0.1.0[/green]")
    rprint("[yellow]支持格式:[/yellow]")
    rprint("  - 图像: .jpg, .jpeg, .png, .bmp, .tiff")
    rprint("  - 音频: .wav, .flac, .ogg (无需外部依赖)")
    rprint("  - 视频: .mp4, .avi, .mov, .mkv, .flv, .wmv")


@app.command("help-algorithms")
def help_algorithms():
    """显示水印算法说明"""
    console.print("\n[bold blue]水印算法说明[/bold blue]\n")

    # 图像水印算法
    image_table = Table(title="图像水印算法")
    image_table.add_column("算法", style="cyan")
    image_table.add_column("特点", style="green")
    image_table.add_column("鲁棒性", style="yellow")
    image_table.add_column("速度", style="magenta")

    image_table.add_row("dwtDct", "DWT+DCT域水印", "中等", "快")
    image_table.add_row("dwtDctSvd", "DWT+DCT+SVD域水印", "高", "中等")

    console.print(image_table)

    # 音频水印算法
    audio_table = Table(title="音频水印算法")
    audio_table.add_column("算法", style="cyan")
    audio_table.add_column("特点", style="green")
    audio_table.add_column("鲁棒性", style="yellow")

    audio_table.add_row("dct", "DCT域量化调制水印", "中等")
    audio_table.add_row("dwt", "小波域系数修改水印", "高")

    console.print(audio_table)

    # 视频水印算法
    video_table = Table(title="视频水印算法")
    video_table.add_column("算法", style="cyan")
    video_table.add_column("特点", style="green")
    video_table.add_column("鲁棒性", style="yellow")
    video_table.add_column("速度", style="magenta")

    video_table.add_row("dwtDct", "基于帧的DWT+DCT域水印", "中等", "快")
    video_table.add_row("dwtDctSvd", "基于帧的DWT+DCT+SVD域水印", "高", "中等")

    console.print(video_table)


if __name__ == "__main__":
    app()
