# Media Seal 快速开始指南

## 安装

### 方法1：源码安装
```bash
# 克隆仓库
git clone https://github.com/your-username/media-seal.git
cd media-seal

# 安装依赖
pip install -r requirements.txt

# 或使用项目配置安装
pip install -e .
```

### 方法2：使用预编译可执行文件
从 [Releases](https://github.com/your-username/media-seal/releases) 页面下载对应平台的可执行文件。

## 基本使用

### 图像水印

#### 嵌入图像水印
```bash
# 基本用法
python main.py image embed input.jpg output.jpg "我的水印"

# 指定算法
python main.py image embed input.png output.png "版权保护" --method dwtDctSvd

# 使用blind方法（需要密码）
python main.py image embed input.jpg output.jpg "秘密水印" --method blind --password-img 123 --password-wm 456
```

#### 提取图像水印
```bash
# 基本提取
python main.py image extract watermarked.jpg

# 指定算法提取
python main.py image extract watermarked.png --method dwtDctSvd

# blind方法提取（需要相同密码）
python main.py image extract watermarked.jpg --method blind --password-img 123 --password-wm 456
```

#### 批量处理图像
```bash
# 批量嵌入水印
python main.py image batch-embed input_folder/ output_folder/ "批量水印"
```

### 音频水印

#### 嵌入音频水印
```bash
# 基本用法
python main.py audio embed input.wav output.wav "音频水印"

# 指定算法和参数
python main.py audio embed input.mp3 output.mp3 "版权标识" --method dwt --alpha 0.2 --password 12345
```

#### 提取音频水印
```bash
# 基本提取
python main.py audio extract watermarked.wav --length 8

# 指定算法提取
python main.py audio extract watermarked.mp3 --method dwt --length 8 --password 12345
```

### 视频水印

#### 嵌入视频水印
```bash
# 基本用法
python main.py video embed input.mp4 output.mp4 "视频水印"

# 指定帧间隔（性能优化）
python main.py video embed input.avi output.avi "版权保护" --frame-interval 10

# 限制处理帧数（测试用）
python main.py video embed input.mov output.mov "测试水印" --max-frames 100
```

#### 提取视频水印
```bash
# 基本提取
python main.py video extract watermarked.mp4

# 指定采样参数
python main.py video extract watermarked.avi --sample-frames 5 --frame-interval 10
```

#### 视频工具功能
```bash
# 查看视频信息
python main.py video info video.mp4

# 提取视频帧
python main.py video extract-frames video.mp4 frames_output/ --interval 30 --max-frames 20
```

## 算法选择指南

### 图像水印算法

| 算法 | 特点 | 适用场景 | 鲁棒性 | 速度 |
|------|------|----------|--------|------|
| `dwtDct` | DWT+DCT域，平衡性能 | 一般图像保护 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| `dwtDctSvd` | 添加SVD，更鲁棒 | 重要图像保护 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| `rivaGan` | 深度学习方法 | 高质量需求 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| `blind` | 盲水印，支持图像水印 | 隐蔽性要求高 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 音频水印算法

| 算法 | 特点 | 适用场景 | 鲁棒性 |
|------|------|----------|--------|
| `dct` | DCT域扩频 | 一般音频保护 | ⭐⭐⭐ |
| `dwt` | 小波域变换 | 高质量音频 | ⭐⭐⭐⭐ |
| `spectrogram` | 频谱图域 | 语音内容 | ⭐⭐⭐ |

## 高级用法

### 鲁棒性测试
```bash
# TODO: 实现鲁棒性测试功能
python main.py benchmark test_files/ --watermark "测试水印"
```

### 性能优化建议

1. **图像处理**：对于大图片，建议使用 `dwtDct` 算法获得最佳速度
2. **音频处理**：设置合适的 `alpha` 值（0.05-0.2），过大会影响音质
3. **视频处理**：使用 `frame-interval` 参数减少处理帧数，提高速度
4. **批量处理**：使用批量命令可以获得更好的性能

### 错误排查

#### 常见问题

1. **依赖安装失败**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libsndfile1 ffmpeg portaudio19-dev
   
   # macOS
   brew install ffmpeg portaudio
   
   # Windows
   # 使用conda或直接下载预编译包
   ```

2. **水印提取失败**
   - 确保使用相同的算法和参数
   - 检查文件是否被压缩或修改
   - 对于盲水印，确保密码正确

3. **视频处理内存不足**
   - 增大 `frame-interval` 参数
   - 使用 `max-frames` 限制处理帧数
   - 分段处理大视频文件

## 开发模式

### 运行演示
```bash
python examples/demo.py
```

### 查看帮助
```bash
python main.py --help
python main.py image --help
python main.py audio --help
python main.py video --help

# 查看算法说明
python main.py help-algorithms

# 查看版本信息
python main.py version
```

## 构建可执行文件

### 本地构建
```bash
pip install pyinstaller
pyinstaller --clean --noconfirm build.spec
```

### 使用GitHub Actions
推送代码到GitHub，Actions会自动构建多平台可执行文件。

## 支持的格式

- **图像**: .jpg, .jpeg, .png, .bmp, .tiff
- **音频**: .wav, .mp3, .flac, .ogg, .m4a  
- **视频**: .mp4, .avi, .mov, .mkv, .flv, .wmv

## 注意事项

1. **版权保护**: 数字水印不是绝对安全的，请结合其他保护措施
2. **文件备份**: 处理重要文件前请先备份
3. **参数记录**: 记录好水印参数，提取时需要相同配置
4. **法律合规**: 确保水印使用符合当地法律法规

## 获取帮助

- 查看 [README.md](README.md) 了解技术细节
- 提交 [Issue](https://github.com/your-username/media-seal/issues) 报告问题
- 查看 [Wiki](https://github.com/your-username/media-seal/wiki) 获取更多文档 