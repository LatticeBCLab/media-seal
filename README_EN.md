# Media Seal - Digital Watermarking Tool

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Version](https://img.shields.io/badge/Version-0.1.0-red.svg)](https://github.com/yourusername/media-seal)

**Language / 语言:** [中文](./README.md) | English

A powerful digital watermarking CLI tool that supports watermark embedding and extraction for images, audio, and video files, designed specifically for copyright protection.

## ✨ Features

- 🖼️ **Image Watermarking**: Frequency domain watermarking based on DWT+DCT/DWT+DCT+SVD, supports jpg, png, bmp and other formats
- 🎵 **Audio Watermarking**: DCT/DWT frequency domain quantization modulation, supports wav, flac, ogg, mp3 and other formats  
- 🎬 **Video Watermarking**: Frame-level watermark processing, supports mp4, avi, mov, mkv and other formats
- 🚀 **High Performance**: Optimized algorithms with batch processing support
- 🛡️ **Strong Robustness**: Resistant to compression, noise, and geometric transformation attacks
- 💻 **Cross-platform**: Supports Windows, macOS, Linux
- 🎨 **Beautiful Interface**: Rich terminal output with colors

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/yourusername/media-seal.git
cd media-seal
pip install -e .

# Or use uv (recommended)
uv install
```

### Basic Usage

```bash
# Show help
media-seal --help

# Image watermarking
media-seal image embed input.jpg output.jpg "Copyright"
media-seal image extract output.jpg 9

# Audio watermarking
media-seal audio embed input.wav output.wav "Copyright Protection"
media-seal audio extract output.wav 12

# Video watermarking
media-seal video embed input.mp4 output.mp4 "Watermark Content"
media-seal video extract output.mp4 12

# Batch processing
media-seal image batch-embed ./input_dir ./output_dir "Batch Watermark"
```

## 📖 Detailed Usage

### Image Watermarking

#### Embed Watermark
```bash
# Basic usage
media-seal image embed input.jpg output.jpg "My Watermark"

# Specify algorithm
media-seal image embed input.jpg output.jpg "My Watermark" --method dwtDctSvd

# Batch processing
media-seal image batch-embed ./images ./watermarked "Copyright Protection"
```

#### Extract Watermark
```bash
# Extract watermark (need to specify watermark length)
media-seal image extract watermarked.jpg 12 --method dwtDct
```

### Audio Watermarking

#### Embed Watermark
```bash
# Basic usage (DCT algorithm)
media-seal audio embed input.wav output.wav "Audio Watermark"

# Use wavelet transform algorithm
media-seal audio embed input.wav output.wav "Watermark" --method dwt

# Batch processing
media-seal audio batch-embed ./audio ./watermarked "Copyright"
```

#### Extract Watermark
```bash
# Extract watermark
media-seal audio extract watermarked.wav 8 --method dct
```

### Video Watermarking

#### Embed Watermark
```bash
# Basic usage
media-seal video embed input.mp4 output.mp4 "Video Watermark"

# Set frame interval (embed every 5 frames)
media-seal video embed input.mp4 output.mp4 "Watermark" --frame-interval 5

# Limit processing frames (for testing)
media-seal video embed input.mp4 output.mp4 "Test" --max-frames 100
```

#### Extract Watermark
```bash
# Extract watermark
media-seal video extract watermarked.mp4 10 --sample-frames 20

# Show video info
media-seal video info input.mp4

# Extract video frames
media-seal video extract-frames input.mp4 ./frames --interval 30
```

### Algorithm Description

#### Image Watermarking Algorithms
- `dwtDct`: DWT+DCT domain watermarking, fast speed, medium robustness
- `dwtDctSvd`: DWT+DCT+SVD domain watermarking, high robustness, medium speed

#### Audio Watermarking Algorithms  
- `dct`: DCT domain quantization modulation watermarking, suitable for most scenarios
- `dwt`: Wavelet domain coefficient modification watermarking, stronger robustness

## 🛠️ Development

### Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/media-seal.git
cd media-seal

# Install development dependencies with uv
uv sync --dev

# Or use pip
pip install -e ".[dev]"
```

### Code Quality

```bash
# Run code checks
uv run ruff check
uv run ruff format

# Run tests
uv run pytest
```

### Build Executable

```bash
# Build with PyInstaller
uv run pyinstaller --onefile main.py

# Output files in dist/ directory
```

## 📁 Project Structure

```
media-seal/
├── main.py              # CLI entry point
├── watermark/           # Watermark processing modules
│   ├── __init__.py     # Module initialization
│   ├── image_watermark.py   # Image watermark processing
│   ├── audio_watermark.py   # Audio watermark processing
│   └── video_watermark.py   # Video watermark processing
├── pyproject.toml      # Project configuration
├── uv.lock            # Dependency lock file
└── README.md          # Project documentation
```

## 🔧 Technical Implementation

### Core Algorithms

1. **Image Watermarking**:
   - Uses invisible-watermark library
   - Supports DWT+DCT and DWT+DCT+SVD transform domain watermarking
   - Blind watermarking technology, no original image needed for extraction

2. **Audio Watermarking**:
   - Self-implemented algorithms based on librosa and scipy
   - DCT domain quantization modulation and wavelet domain coefficient modification
   - Supports reading and writing multiple audio formats

3. **Video Watermarking**:
   - Frame-level video watermarking processing
   - Uses imageio to handle video frame sequences
   - Configurable frame intervals and processing parameters

### Dependencies

- `typer + rich`: Modern CLI interface
- `opencv-python`: Image processing
- `invisible-watermark`: Image watermarking algorithms
- `librosa + scipy`: Audio processing and transforms
- `imageio[ffmpeg]`: Video processing
- `PyWavelets`: Wavelet transform support

## 🎯 Supported Formats

### Image Formats
- `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### Audio Formats  
- `.wav`, `.flac`, `.ogg`, `.mp3`, `.m4a`, `.aac`

### Video Formats
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`

## ⚠️ Important Notes

1. **Watermark Length**: Need to know exact watermark length for extraction
2. **Algorithm Consistency**: Must use same algorithm for embedding and extraction
3. **Format Limitations**: Some formats may have compatibility issues
4. **Performance Considerations**: Video processing is time-consuming, test with small files first

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve this project!

## 📞 Support

If you encounter problems, please:
1. Check documentation and examples
2. Submit an Issue on GitHub
3. Verify dependencies are correctly installed

---

> 💡 **Note**: Digital watermarking is primarily for copyright protection, please use this tool legally.