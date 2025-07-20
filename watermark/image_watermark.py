"""
图像数字水印模块
支持多种算法：DWT+DCT、DWT+DCT+SVD、RivaGAN等
"""

from pathlib import Path
from typing import Literal

import cv2
from rich.console import Console
from rich.progress import track

try:
    from imwatermark import WatermarkDecoder, WatermarkEncoder
    INVISIBLE_WATERMARK_AVAILABLE = True
except ImportError:
    INVISIBLE_WATERMARK_AVAILABLE = False

try:
    from blind_watermark import WaterMark
    BLIND_WATERMARK_AVAILABLE = True
except ImportError:
    BLIND_WATERMARK_AVAILABLE = False

console = Console()

class ImageWatermark:
    """图像数字水印处理类"""

    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    def embed(
        self,
        input_path: str | Path,
        output_path: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1
    ) -> bool:
        """
        嵌入图像水印
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            watermark: 水印内容（字符串或图片路径）
            method: 水印算法
            password_img: 图片密码（用于blind方法）
            password_wm: 水印密码（用于blind方法）
            
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
                console.print(f"[red]错误：不支持的图片格式: {input_path.suffix}[/red]")
                return False

            # 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if method in ["dwtDct", "dwtDctSvd", "rivaGan"]:
                return self._embed_invisible_watermark(input_path, output_path, watermark, method)
            elif method == "blind":
                return self._embed_blind_watermark(input_path, output_path, watermark, password_img, password_wm)
            else:
                console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]嵌入水印时发生错误: {str(e)}[/red]")
            return False

    def extract(
        self,
        input_path: str | Path,
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1,
        wm_shape: tuple | None = None,
        output_wm_path: str | Path | None = None
    ) -> str | None:
        """
        提取图像水印
        
        Args:
            input_path: 输入图片路径
            method: 水印算法
            password_img: 图片密码（用于blind方法）
            password_wm: 水印密码（用于blind方法）
            wm_shape: 水印形状（用于blind方法提取图像水印）
            output_wm_path: 输出水印路径（用于blind方法提取图像水印）
            
        Returns:
            str: 提取的水印内容，如果是图像水印则返回输出路径
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                console.print(f"[red]错误：输入文件不存在: {input_path}[/red]")
                return None

            if method in ["dwtDct", "dwtDctSvd", "rivaGan"]:
                return self._extract_invisible_watermark(input_path, method)
            elif method == "blind":
                return self._extract_blind_watermark(input_path, password_img, password_wm, wm_shape, output_wm_path)
            else:
                console.print(f"[red]错误：不支持的水印方法: {method}[/red]")
                return None

        except Exception as e:
            console.print(f"[red]提取水印时发生错误: {str(e)}[/red]")
            return None

    def _embed_invisible_watermark(self, input_path: Path, output_path: Path, watermark: str, method: str) -> bool:
        """使用invisible-watermark库嵌入水印"""
        if not INVISIBLE_WATERMARK_AVAILABLE:
            console.print("[red]错误：请安装 invisible-watermark 库[/red]")
            return False

        bgr = cv2.imread(str(input_path))
        if bgr is None:
            console.print(f"[red]错误：无法读取图片: {input_path}[/red]")
            return False

        encoder = WatermarkEncoder()
        encoder.set_watermark('bytes', watermark.encode('utf-8'))
        bgr_encoded = encoder.encode(bgr, method)

        success = cv2.imwrite(str(output_path), bgr_encoded)
        if success:
            console.print(f"[green]成功嵌入水印到: {output_path}[/green]")
        return success

    def _extract_invisible_watermark(self, input_path: Path, method: str) -> str | None:
        """使用invisible-watermark库提取水印"""
        if not INVISIBLE_WATERMARK_AVAILABLE:
            console.print("[red]错误：请安装 invisible-watermark 库[/red]")
            return None

        bgr = cv2.imread(str(input_path))
        if bgr is None:
            console.print(f"[red]错误：无法读取图片: {input_path}[/red]")
            return None

        decoder = WatermarkDecoder('bytes', 32)
        watermark_bytes = decoder.decode(bgr, method)

        try:
            watermark = watermark_bytes.decode('utf-8')
            console.print(f"[green]成功提取水印: {watermark}[/green]")
            return watermark
        except UnicodeDecodeError:
            console.print("[yellow]警告：无法解码水印为UTF-8文本[/yellow]")
            return watermark_bytes.hex()

    def _embed_blind_watermark(self, input_path: Path, output_path: Path, watermark: str, password_img: int, password_wm: int) -> bool:
        """使用blind-watermark库嵌入水印"""
        if not BLIND_WATERMARK_AVAILABLE:
            console.print("[red]错误：请安装 blind-watermark 库[/red]")
            return False

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        bwm.read_img(str(input_path))

        # 检查是否为图片路径
        if Path(watermark).exists() and Path(watermark).suffix.lower() in self.supported_formats:
            # 嵌入图像水印
            bwm.read_wm(watermark)
        else:
            # 嵌入文字水印
            bwm.read_wm(watermark, mode='str')

        bwm.embed(str(output_path))
        console.print(f"[green]成功嵌入水印到: {output_path}[/green]")
        return True

    def _extract_blind_watermark(self, input_path: Path, password_img: int, password_wm: int, wm_shape: tuple | None, output_wm_path: Path | None) -> str | None:
        """使用blind-watermark库提取水印"""
        if not BLIND_WATERMARK_AVAILABLE:
            console.print("[red]错误：请安装 blind-watermark 库[/red]")
            return None

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)

        if wm_shape and output_wm_path:
            # 提取图像水印
            output_wm_path = Path(output_wm_path)
            output_wm_path.parent.mkdir(parents=True, exist_ok=True)
            bwm.extract(filename=str(input_path), wm_shape=wm_shape, out_wm_name=str(output_wm_path))
            console.print(f"[green]成功提取图像水印到: {output_wm_path}[/green]")
            return str(output_wm_path)
        else:
            # 提取文字水印
            watermark = bwm.extract(filename=str(input_path), mode='str')
            console.print(f"[green]成功提取文字水印: {watermark}[/green]")
            return watermark

    def batch_embed(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        watermark: str,
        method: Literal["dwtDct", "dwtDctSvd", "rivaGan", "blind"] = "dwtDct",
        password_img: int = 1,
        password_wm: int = 1
    ) -> int:
        """
        批量嵌入图像水印
        
        Returns:
            int: 成功处理的文件数量
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            console.print(f"[red]错误：输入目录不存在: {input_dir}[/red]")
            return 0

        # 获取所有图片文件
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
            if self.embed(img_file, output_file, watermark, method, password_img, password_wm):
                success_count += 1

        console.print(f"[green]批量处理完成：成功处理 {success_count}/{len(image_files)} 个文件[/green]")
        return success_count
