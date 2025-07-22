# Media Seal - 数字水印工具

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Version](https://img.shields.io/badge/Version-0.1.0-red.svg)](https://github.com/yourusername/media-seal)

**语言 / Language:** 中文 | [English](./README_EN.md)

一个功能强大的数字水印CLI工具，支持图像、音频、视频的水印嵌入和提取，专为版权保护而设计。

## ✨ 特性

- 🖼️ **图像水印**：基于DWT+DCT/DWT+DCT+SVD频域变换，支持jpg、png、bmp等格式
- 🎵 **音频水印**：基于DCT/DWT频域量化调制，支持wav、flac、ogg、mp3等格式  
- 🎬 **视频水印**：基于帧级水印处理，支持mp4、avi、mov、mkv等格式
- 🚀 **高性能**：优化的算法实现，支持批量处理
- 🛡️ **鲁棒性强**：抗压缩、抗噪声、抗几何变换攻击
- 💻 **跨平台**：支持Windows、macOS、Linux
- 🎨 **美观界面**：基于Rich的彩色终端输出

## 🚀 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/yourusername/media-seal.git
cd media-seal
pip install -e .

# 或使用uv (推荐)
uv install
```

### 基本用法

```bash
# 显示帮助
media-seal --help

# 图像水印
media-seal image embed input.jpg output.jpg "版权所有"
media-seal image extract output.jpg 9

# 音频水印
media-seal audio embed input.wav output.wav "版权保护"
media-seal audio extract output.wav 12

# 视频水印
media-seal video embed input.mp4 output.mp4 "水印内容"
media-seal video extract output.mp4 12

# 批量处理
media-seal image batch-embed ./input_dir ./output_dir "批量水印"
```

## 📖 详细使用说明

### 图像水印

#### 嵌入水印
```bash
# 基本用法
media-seal image embed input.jpg output.jpg "我的水印"

# 指定算法
media-seal image embed input.jpg output.jpg "我的水印" --method dwtDctSvd

# 批量处理
media-seal image batch-embed ./images ./watermarked "版权保护"
```

#### 提取水印
```bash
# 提取水印（需要指定水印长度）
media-seal image extract watermarked.jpg 12 --method dwtDct
```

### 音频水印

#### 嵌入水印
```bash
# 基本用法（DCT算法）
media-seal audio embed input.wav output.wav "音频水印"

# 使用小波变换算法
media-seal audio embed input.wav output.wav "水印" --method dwt

# 批量处理
media-seal audio batch-embed ./audio ./watermarked "版权"
```

#### 提取水印
```bash
# 提取水印
media-seal audio extract watermarked.wav 8 --method dct
```

### 视频水印

#### 嵌入水印
```bash
# 基本用法
media-seal video embed input.mp4 output.mp4 "视频水印"

# 设置帧间隔（每隔5帧嵌入一次）
media-seal video embed input.mp4 output.mp4 "水印" --frame-interval 5

# 限制处理帧数（用于测试）
media-seal video embed input.mp4 output.mp4 "测试" --max-frames 100
```

#### 提取水印
```bash
# 提取水印
media-seal video extract watermarked.mp4 10 --sample-frames 20

# 查看视频信息
media-seal video info input.mp4

# 提取视频帧
media-seal video extract-frames input.mp4 ./frames --interval 30
```

### 算法说明

#### 图像水印算法
- `dwtDct`：DWT+DCT域水印，速度快，鲁棒性中等
- `dwtDctSvd`：DWT+DCT+SVD域水印，鲁棒性高，速度中等

#### 音频水印算法  
- `dct`：DCT域量化调制水印，适合大多数场景
- `dwt`：小波域系数修改水印，鲁棒性更强

## 🛠️ 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/media-seal.git
cd media-seal

# 使用uv安装开发依赖
uv sync --dev

# 或使用pip
pip install -e ".[dev]"
```

### 代码检查

```bash
# 运行代码检查
uv run ruff check
uv run ruff format

# 运行测试
uv run pytest
```

### 构建可执行文件

```bash
# 使用PyInstaller打包
uv run pyinstaller --onefile main.py

# 输出文件在 dist/ 目录下
```

## 📁 项目结构

```
media-seal/
├── main.py              # CLI入口文件
├── watermark/           # 水印处理模块
│   ├── __init__.py     # 模块初始化
│   ├── image_watermark.py   # 图像水印处理
│   ├── audio_watermark.py   # 音频水印处理
│   └── video_watermark.py   # 视频水印处理
├── pyproject.toml      # 项目配置
├── uv.lock            # 依赖锁定文件
└── README.md          # 项目说明
```

## 🔧 技术实现

### 核心算法

1. **图像水印**：
   - 使用invisible-watermark库
   - 支持DWT+DCT和DWT+DCT+SVD变换域水印
   - 盲水印技术，无需原图即可提取

2. **音频水印**：
   - 基于librosa和scipy的自实现算法
   - DCT域量化调制和小波域系数修改
   - 支持多种音频格式的读写

3. **视频水印**：
   - 基于帧级处理的视频水印
   - 使用imageio处理视频帧序列
   - 可配置帧间隔和处理参数

### 依赖库

- `typer + rich`: 现代化CLI界面
- `opencv-python`: 图像处理
- `invisible-watermark`: 图像水印算法
- `librosa + scipy`: 音频处理和变换
- `imageio[ffmpeg]`: 视频处理
- `PyWavelets`: 小波变换支持

## 🎯 支持格式

### 图像格式
- `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### 音频格式  
- `.wav`, `.flac`, `.ogg`, `.mp3`, `.m4a`, `.aac`

### 视频格式
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`

## ⚠️ 注意事项

1. **水印长度**：提取时需要知道确切的水印长度
2. **算法一致**：嵌入和提取必须使用相同的算法
3. **格式限制**：某些格式可能有兼容性问题
4. **性能考虑**：视频处理较为耗时，建议先用小文件测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如果遇到问题，请：
1. 查看文档和示例
2. 在GitHub上提交Issue
3. 检查依赖是否正确安装

---

> 💡 **提示**: 数字水印主要用于版权保护，请合法使用此工具。
