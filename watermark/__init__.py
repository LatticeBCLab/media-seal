"""
数字水印工具包
支持图像、音频、视频的数字水印嵌入和提取
"""

from .audio_watermark import AudioWatermark
from .image_watermark import ImageWatermark
from .video_watermark import VideoWatermark

__version__ = "0.1.0"
__all__ = ["ImageWatermark", "AudioWatermark", "VideoWatermark"]
