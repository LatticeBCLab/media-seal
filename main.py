"""
数字水印工具 - CLI主程序
支持图像、音频、视频的数字水印嵌入和提取
"""

from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

console = Console()

# 尝试导入水印模块，如果失败则给出提示
try:
    from watermark import AudioWatermark, ImageWatermark, VideoWatermark

    WATERMARK_AVAILABLE = True
except ImportError as e:
    console.print(f"[yellow]警告：水印模块导入失败: {str(e)}[/yellow]")
    WATERMARK_AVAILABLE = False
    ImageWatermark = AudioWatermark = VideoWatermark = None

# 创建主应用和子应用
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


# 图像水印命令
@image_app.command("embed")
def image_embed(
    input_path: Path = typer.Argument(..., help="输入图片路径"),
    output_path: Path = typer.Argument(..., help="输出图片路径"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
):
    """嵌入图像水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    if method not in ["dwtDct", "dwtDctSvd", "rivaGan", "blind"]:
        console.print(f"[red]错误：不支持的方法: {method}[/red]")
        raise typer.Exit(1)

    watermarker = ImageWatermark()
    success = watermarker.embed(
        input_path, output_path, watermark, method, password_img, password_wm
    )
    if not success:
        raise typer.Exit(1)


@image_app.command("extract")
def image_extract(
    input_path: Path = typer.Argument(..., help="输入图片路径"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
    wm_shape: str | None = typer.Option(
        None, "--wm-shape", help="水印形状（如：128,128，用于blind方法提取图像水印）"
    ),
    output_wm_path: Path | None = typer.Option(
        None, "--output-wm", help="输出水印路径（用于blind方法提取图像水印）"
    ),
):
    """提取图像水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = ImageWatermark()

    # 解析水印形状
    wm_shape_tuple = None
    if wm_shape:
        try:
            wm_shape_tuple = tuple(map(int, wm_shape.split(",")))
        except ValueError:
            console.print("[red]错误：水印形状格式错误，应为 '宽,高' 格式[/red]")
            raise typer.Exit(1)

    result = watermarker.extract(
        input_path, method, password_img, password_wm, wm_shape_tuple, output_wm_path
    )
    if result is None:
        raise typer.Exit(1)


@image_app.command("batch-embed")
def image_batch_embed(
    input_dir: Path = typer.Argument(..., help="输入目录"),
    output_dir: Path = typer.Argument(..., help="输出目录"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
):
    """批量嵌入图像水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = ImageWatermark()
    success_count = watermarker.batch_embed(
        input_dir, output_dir, watermark, method, password_img, password_wm
    )
    if success_count == 0:
        raise typer.Exit(1)


# 音频水印命令
@audio_app.command("embed")
def audio_embed(
    input_path: Path = typer.Argument(..., help="输入音频路径"),
    output_path: Path = typer.Argument(..., help="输出音频路径"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dct", "--method", "-m", help="水印算法: dct, dwt, spectrogram"
    ),
    alpha: float = typer.Option(0.1, "--alpha", "-a", help="水印强度 (0.01-1.0)"),
    password: int = typer.Option(42, "--password", "-p", help="密码种子"),
):
    """嵌入音频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    if not (0.01 <= alpha <= 1.0):
        console.print("[red]错误：水印强度应在 0.01-1.0 范围内[/red]")
        raise typer.Exit(1)

    if method not in ["dct", "dwt", "spectrogram"]:
        console.print(f"[red]错误：不支持的方法: {method}[/red]")
        raise typer.Exit(1)

    watermarker = AudioWatermark()
    success = watermarker.embed(
        input_path, output_path, watermark, method, alpha, password
    )
    if not success:
        raise typer.Exit(1)


@audio_app.command("extract")
def audio_extract(
    input_path: Path = typer.Argument(..., help="输入音频路径"),
    method: str = typer.Option(
        "dct", "--method", "-m", help="水印算法: dct, dwt, spectrogram"
    ),
    watermark_length: int = typer.Option(
        32, "--length", "-l", help="水印长度（字符数）"
    ),
    password: int = typer.Option(42, "--password", "-p", help="密码种子"),
):
    """提取音频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = AudioWatermark()
    result = watermarker.extract(input_path, method, watermark_length, password)
    if result is None:
        raise typer.Exit(1)


@audio_app.command("batch-embed")
def audio_batch_embed(
    input_dir: Path = typer.Argument(..., help="输入目录"),
    output_dir: Path = typer.Argument(..., help="输出目录"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dct", "--method", "-m", help="水印算法: dct, dwt, spectrogram"
    ),
    alpha: float = typer.Option(0.1, "--alpha", "-a", help="水印强度"),
    password: int = typer.Option(42, "--password", "-p", help="密码种子"),
):
    """批量嵌入音频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = AudioWatermark()
    success_count = watermarker.batch_embed(
        input_dir, output_dir, watermark, method, alpha, password
    )
    if success_count == 0:
        raise typer.Exit(1)


# 视频水印命令
@video_app.command("embed")
def video_embed(
    input_path: Path = typer.Argument(..., help="输入视频路径"),
    output_path: Path = typer.Argument(..., help="输出视频路径"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
    frame_interval: int = typer.Option(
        1, "--frame-interval", help="帧间隔（每隔多少帧嵌入一次）"
    ),
    max_frames: int | None = typer.Option(
        None, "--max-frames", help="最大处理帧数（用于测试）"
    ),
):
    """嵌入视频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = VideoWatermark()
    success = watermarker.embed(
        input_path,
        output_path,
        watermark,
        method,
        password_img,
        password_wm,
        frame_interval,
        max_frames,
    )
    if not success:
        raise typer.Exit(1)


@video_app.command("extract")
def video_extract(
    input_path: Path = typer.Argument(..., help="输入视频路径"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
    frame_interval: int = typer.Option(1, "--frame-interval", help="帧间隔"),
    sample_frames: int = typer.Option(10, "--sample-frames", help="采样帧数"),
    wm_shape: str | None = typer.Option(
        None, "--wm-shape", help="水印形状（如：128,128）"
    ),
    output_wm_dir: Path | None = typer.Option(
        None, "--output-wm-dir", help="输出水印目录"
    ),
):
    """提取视频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = VideoWatermark()

    # 解析水印形状
    wm_shape_tuple = None
    if wm_shape:
        try:
            wm_shape_tuple = tuple(map(int, wm_shape.split(",")))
        except ValueError:
            console.print("[red]错误：水印形状格式错误，应为 '宽,高' 格式[/red]")
            raise typer.Exit(1)

    result = watermarker.extract(
        input_path,
        method,
        password_img,
        password_wm,
        frame_interval,
        sample_frames,
        wm_shape_tuple,
        output_wm_dir,
    )
    if result is None:
        raise typer.Exit(1)


@video_app.command("info")
def video_info(video_path: Path = typer.Argument(..., help="视频路径")):
    """显示视频信息"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

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
def video_extract_frames(
    video_path: Path = typer.Argument(..., help="视频路径"),
    output_dir: Path = typer.Argument(..., help="输出目录"),
    frame_interval: int = typer.Option(30, "--interval", help="帧间隔"),
    max_frames: int | None = typer.Option(None, "--max-frames", help="最大提取帧数"),
):
    """提取视频帧"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = VideoWatermark()
    count = watermarker.extract_frames(
        video_path, output_dir, frame_interval, max_frames
    )
    if count == 0:
        raise typer.Exit(1)


@video_app.command("batch-embed")
def video_batch_embed(
    input_dir: Path = typer.Argument(..., help="输入目录"),
    output_dir: Path = typer.Argument(..., help="输出目录"),
    watermark: str = typer.Argument(..., help="水印内容"),
    method: str = typer.Option(
        "dwtDct", "--method", "-m", help="水印算法: dwtDct, dwtDctSvd, rivaGan, blind"
    ),
    password_img: int = typer.Option(1, "--password-img", help="图片密码（blind方法）"),
    password_wm: int = typer.Option(1, "--password-wm", help="水印密码（blind方法）"),
    frame_interval: int = typer.Option(1, "--frame-interval", help="帧间隔"),
):
    """批量嵌入视频水印"""
    if not WATERMARK_AVAILABLE:
        console.print("[red]错误：水印模块不可用，请安装必要的依赖[/red]")
        raise typer.Exit(1)

    watermarker = VideoWatermark()
    success_count = watermarker.batch_embed(
        input_dir,
        output_dir,
        watermark,
        method,
        password_img,
        password_wm,
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
    rprint("  - 音频: .wav, .mp3, .flac, .ogg, .m4a")
    rprint("  - 视频: .mp4, .avi, .mov, .mkv, .flv, .wmv")

    if WATERMARK_AVAILABLE:
        rprint("[green]✓ 水印模块已加载[/green]")
    else:
        rprint("[red]✗ 水印模块未加载，请安装必要的依赖[/red]")


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
    image_table.add_row("rivaGan", "基于深度学习的水印", "很高", "慢")
    image_table.add_row("blind", "盲水印（DWT+DCT+SVD）", "高", "中等")

    console.print(image_table)

    # 音频水印算法
    audio_table = Table(title="音频水印算法")
    audio_table.add_column("算法", style="cyan")
    audio_table.add_column("特点", style="green")
    audio_table.add_column("鲁棒性", style="yellow")

    audio_table.add_row("dct", "DCT域扩频水印", "中等")
    audio_table.add_row("dwt", "小波域水印", "高")
    audio_table.add_row("spectrogram", "频谱图域水印", "中等")

    console.print(audio_table)


@app.command("benchmark")
def benchmark(
    test_dir: Path = typer.Argument(..., help="测试文件目录"),
    watermark: str = typer.Option("TestWatermark", "--watermark", help="测试水印内容"),
):
    """性能基准测试"""
    console.print("[bold blue]开始性能基准测试...[/bold blue]")

    # TODO: 实现基准测试功能
    # 测试不同算法的嵌入和提取速度
    # 测试鲁棒性（对各种攻击的抵抗能力）
    console.print("[yellow]基准测试功能待实现[/yellow]")

if __name__ == "__main__":
    app()
