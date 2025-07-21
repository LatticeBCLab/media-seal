from pathlib import Path
from typing import Literal

import cv2
from imwatermark import WatermarkDecoder, WatermarkEncoder
from rich.console import Console
from rich.progress import track

console = Console()


class ImageWatermark:
    """图像数字水印处理类"""

    def __init__(self):
        self.supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
        self.supported_methods = ["dwtDct", "dwtDctSvd"]

    def _validate_input_path(self, input_path: Path) -> bool:
        """验证输入文件路径"""
        if not input_path.exists():
            console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
            return False

        if input_path.suffix.lower() not in self.supported_formats:
            console.print(f"[red]错误：不支持的图片格式: {input_path.suffix}[/red]")
            return False

        return True

    def _validate_method(self, method: str) -> bool:
        """验证水印方法"""
        if method not in self.supported_methods:
            console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
            return False
        return True

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
    ) -> bool:
        """
        嵌入图像水印

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            watermark: 水印内容（字符串或图片路径）
            method: 水印算法

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
            console.print(f"[red]嵌入水印时发生错误: {str(e)}[/red]")
            return False

    def _embed_watermark(
        self, input_path: Path, output_path: Path, watermark: str, method: str
    ) -> bool:
        """使用invisible-watermark库嵌入水印"""
        bgr = cv2.imread(str(input_path))
        if bgr is None:
            console.print(f"[red]错误：无法读取图片: {input_path}[/red]")
            return False

        encoder = WatermarkEncoder()
        encoder.set_watermark("bytes", watermark.encode("utf-8"))
        bgr_encoded = encoder.encode(bgr, method)

        success = cv2.imwrite(str(output_path), bgr_encoded)
        if success:
            console.print(f"[green]成功嵌入水印到: {output_path}[/green]")
        return success

    def extract(
        self,
        input_path: str | Path,
        extract_length: int,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
    ) -> str | None:
        """
        提取图像水印

        Args:
            input_path: 输入图片路径
            extract_length: 提取水印长度，单位byte
            method: 水印算法

        Returns:
            str: 提取的水印内容，如果是图像水印则返回输出路径
        """
        try:
            input_path = Path(input_path)

            # 参数验证
            if not self._validate_input_path(input_path):
                return None

            if not self._validate_method(method):
                return None

            # 执行业务逻辑
            return self._extract_watermark(input_path, method, extract_length)

        except Exception as e:
            console.print(f"[red]提取水印时发生错误: {str(e)}[/red]")
            return None

    def _extract_watermark(
        self, input_path: Path, method: str, extract_length: int
    ) -> str | None:
        """使用invisible-watermark库提取水印"""
        bgr = cv2.imread(str(input_path))
        if bgr is None:
            console.print(f"[red]错误：无法读取图片: {input_path}[/red]")
            return None

        decoder = WatermarkDecoder("bytes", extract_length * 8)
        watermark_bytes = decoder.decode(bgr, method)

        try:
            watermark = watermark_bytes.decode("utf-8")
            console.print(f"[green]成功提取水印: {watermark}[/green]")
            return watermark
        except UnicodeDecodeError:
            console.print("[yellow]警告：无法解码水印为UTF-8文本[/yellow]")
            return watermark_bytes.hex()

    def batch_embed(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd"] = "dwtDct",
    ) -> int:
        """
        批量嵌入图像水印

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            watermark: 水印内容
            method: 水印算法

        Returns:
            int: 成功处理的文件数量
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            console.print(f"[red]错误：输入目录不存在: {input_dir}[/red]")
            return 0

        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_dir.glob(f"*{ext}"))
            image_files.extend(input_dir.glob(f"*{ext.upper()}"))

        if not image_files:
            console.print(f"[yellow]警告：在 {input_dir} 中未找到支持的图片文件[/yellow]")
            return 0

        success_count = 0
        for img_file in track(image_files, description="批量处理图片..."):
            output_file = output_dir / img_file.name
            if self.embed(img_file, output_file, watermark, method):
                success_count += 1

        console.print(f"[green]批量处理完成：成功处理 {success_count}/{len(image_files)} 个文件[/green]")
        return success_count

def test():
    wm = "Copyright 2025 Made by ZKJG"
    image_watermark = ImageWatermark()
    image_watermark.embed(
        input_path="/Users/wenyanglu/Workspace/meebits.png",
        output_path="/Users/wenyanglu/Workspace/meebits_output.png",
        watermark=wm,
        method="dwtDct",
    )
    image_watermark.extract(
        input_path="/Users/wenyanglu/Workspace/meebits_output.png",
        extract_length=len(wm),
        method="dwtDct",
    )


if __name__ == "__main__":
    test()
