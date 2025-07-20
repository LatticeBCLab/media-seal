#!/usr/bin/env python3
"""
Media Seal 演示脚本
展示图像、音频、视频水印的基本使用方法
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from watermark import AudioWatermark, ImageWatermark, VideoWatermark

console = Console()

def create_sample_files():
    """创建示例文件"""
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    console.print("[blue]正在创建示例文件...[/blue]")

    # 创建示例图片（纯色图片）
    try:
        import cv2
        import numpy as np

        # 创建一个简单的彩色图片
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:200, :, :] = [255, 0, 0]  # 红色上半部分
        img[200:, :, :] = [0, 255, 0]  # 绿色下半部分

        cv2.imwrite(str(samples_dir / "sample_image.png"), img)
        console.print("✓ 创建示例图片: samples/sample_image.png")

    except ImportError:
        console.print("[yellow]警告：无法创建示例图片，请手动放置图片文件[/yellow]")

    # 创建示例音频（正弦波）
    try:
        import numpy as np
        import soundfile as sf

        duration = 3  # 3秒
        sample_rate = 22050
        t = np.linspace(0, duration, sample_rate * duration)

        # 生成440Hz的正弦波（A4音符）
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        sf.write(str(samples_dir / "sample_audio.wav"), audio, sample_rate)
        console.print("✓ 创建示例音频: samples/sample_audio.wav")

    except ImportError:
        console.print("[yellow]警告：无法创建示例音频，请手动放置音频文件[/yellow]")

    return samples_dir

def demo_image_watermark():
    """演示图像水印功能"""
    console.print("\n[bold green]图像水印演示[/bold green]")

    samples_dir = Path("samples")
    input_image = samples_dir / "sample_image.png"

    if not input_image.exists():
        console.print("[red]错误：找不到示例图片文件[/red]")
        return

    watermarker = ImageWatermark()
    watermark_text = "Media Seal Demo"

    # 测试不同的水印方法
    methods = ["dwtDct", "blind"]

    for method in methods:
        output_image = samples_dir / f"watermarked_image_{method}.png"

        console.print(f"使用 {method} 方法嵌入水印...")
        success = watermarker.embed(
            input_image,
            output_image,
            watermark_text,
            method
        )

        if success:
            # 提取水印进行验证
            extracted = watermarker.extract(output_image, method)
            if extracted:
                console.print(f"✓ {method} 方法成功 - 提取结果: {extracted}")
            else:
                console.print(f"✗ {method} 方法失败 - 无法提取水印")
        else:
            console.print(f"✗ {method} 方法嵌入失败")

def demo_audio_watermark():
    """演示音频水印功能"""
    console.print("\n[bold green]音频水印演示[/bold green]")

    samples_dir = Path("samples")
    input_audio = samples_dir / "sample_audio.wav"

    if not input_audio.exists():
        console.print("[red]错误：找不到示例音频文件[/red]")
        return

    watermarker = AudioWatermark()
    watermark_text = "AudioSeal"

    # 测试不同的水印方法
    methods = ["dct", "dwt"]

    for method in methods:
        output_audio = samples_dir / f"watermarked_audio_{method}.wav"

        console.print(f"使用 {method} 方法嵌入音频水印...")
        success = watermarker.embed(
            input_audio,
            output_audio,
            watermark_text,
            method,
            alpha=0.1
        )

        if success:
            # 提取水印进行验证
            extracted = watermarker.extract(
                output_audio,
                method,
                watermark_length=len(watermark_text)
            )
            if extracted:
                console.print(f"✓ {method} 方法成功 - 提取结果: {extracted}")
            else:
                console.print(f"✗ {method} 方法失败 - 无法提取水印")
        else:
            console.print(f"✗ {method} 方法嵌入失败")

def demo_video_watermark():
    """演示视频水印功能"""
    console.print("\n[bold green]视频水印演示[/bold green]")

    samples_dir = Path("samples")

    # 首先创建一个简单的测试视频
    try:
        import cv2
        import numpy as np

        # 创建测试视频
        video_path = samples_dir / "sample_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 10.0, (400, 300))

        for i in range(50):  # 50帧，5秒视频
            # 创建渐变色彩的帧
            frame = np.zeros((300, 400, 3), dtype=np.uint8)
            frame[:, :, 0] = (i * 5) % 255  # 红色通道
            frame[:, :, 1] = (i * 3) % 255  # 绿色通道
            frame[:, :, 2] = (i * 7) % 255  # 蓝色通道

            out.write(frame)

        out.release()
        console.print("✓ 创建示例视频: samples/sample_video.mp4")

        # 演示视频水印
        watermarker = VideoWatermark()
        watermark_text = "VideoSeal"

        output_video = samples_dir / "watermarked_video.mp4"

        console.print("嵌入视频水印（处理前10帧）...")
        success = watermarker.embed(
            video_path,
            output_video,
            watermark_text,
            method="dwtDct",
            frame_interval=5,  # 每5帧嵌入一次
            max_frames=10      # 只处理前10帧用于演示
        )

        if success:
            console.print("✓ 视频水印嵌入成功")

            # 提取水印进行验证
            extracted = watermarker.extract(
                output_video,
                method="dwtDct",
                sample_frames=3
            )
            if extracted:
                console.print(f"✓ 视频水印提取成功: {extracted}")
            else:
                console.print("✗ 视频水印提取失败")
        else:
            console.print("✗ 视频水印嵌入失败")

    except ImportError as e:
        console.print(f"[yellow]警告：无法创建示例视频 - {str(e)}[/yellow]")

def show_cli_examples():
    """展示命令行使用示例"""
    console.print("\n[bold blue]命令行使用示例[/bold blue]")

    examples_table = Table(title="CLI 使用示例")
    examples_table.add_column("功能", style="cyan")
    examples_table.add_column("命令", style="green")

    examples_table.add_row(
        "图像水印嵌入",
        "media-seal image embed input.jpg output.jpg 'My Watermark'"
    )
    examples_table.add_row(
        "图像水印提取",
        "media-seal image extract watermarked.jpg"
    )
    examples_table.add_row(
        "音频水印嵌入",
        "media-seal audio embed input.wav output.wav 'AudioMark' --method dct"
    )
    examples_table.add_row(
        "音频水印提取",
        "media-seal audio extract watermarked.wav --length 9"
    )
    examples_table.add_row(
        "视频水印嵌入",
        "media-seal video embed input.mp4 output.mp4 'VideoMark' --frame-interval 10"
    )
    examples_table.add_row(
        "视频信息查看",
        "media-seal video info video.mp4"
    )
    examples_table.add_row(
        "批量处理图片",
        "media-seal image batch-embed input_dir/ output_dir/ 'BatchMark'"
    )
    examples_table.add_row(
        "算法帮助",
        "media-seal help-algorithms"
    )

    console.print(examples_table)

def main():
    """主函数"""
    console.print("[bold blue]Media Seal 数字水印工具演示[/bold blue]")
    console.print("本演示将展示图像、音频、视频水印的基本功能\n")

    # 创建示例文件
    samples_dir = create_sample_files()

    # 演示各种水印功能
    try:
        demo_image_watermark()
    except Exception as e:
        console.print(f"[red]图像水印演示失败: {str(e)}[/red]")

    try:
        demo_audio_watermark()
    except Exception as e:
        console.print(f"[red]音频水印演示失败: {str(e)}[/red]")

    try:
        demo_video_watermark()
    except Exception as e:
        console.print(f"[red]视频水印演示失败: {str(e)}[/red]")

    # 展示CLI使用示例
    show_cli_examples()

    console.print(f"\n[green]演示完成！示例文件保存在: {samples_dir.absolute()}[/green]")
    console.print("[blue]使用 'python main.py --help' 查看完整的CLI帮助[/blue]")

if __name__ == "__main__":
    main()
