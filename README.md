# Python数字水印技术调研报告

## 项目概述

本项目旨在实现给图片、音频、视频加数字水印的功能，主要用于版权保护。基于鲁棒性考虑，排除LSB（最低有效位）方法，采用频域变换等更鲁棒的技术。项目使用Python开发，支持CLI框架（基于typer），并能打包为跨平台可执行文件。

## 数字水印技术分类

### 按域分类
- **空域方法**：直接修改像素值（LSB等），简单但鲁棒性差
- **频域方法**：在变换域嵌入水印（DCT、DWT、DFT等），鲁棒性强

### 按鲁棒性分类
- **鲁棒水印**：能抵抗各种攻击和处理操作
- **脆弱水印**：易受攻击，主要用于完整性检测

## Python数字水印库调研

### 1. 图像数字水印库

#### 1.1 invisible-watermark（推荐⭐⭐⭐⭐⭐）
- **GitHub**: https://github.com/ShieldMnt/invisible-watermark
- **PyPI**: `pip install invisible-watermark`
- **特点**：
  - 支持多种算法：DWT+DCT、DWT+DCT+SVD
  - 不可见盲水印，无需原图即可提取
  - 支持命令行和API接口
  - 对噪声、亮度、JPEG压缩有很好的鲁棒性
  - 速度较快，适合实时嵌入

```python
# 嵌入水印
import cv2
from imwatermark import WatermarkEncoder

bgr = cv2.imread('test.png')
wm = 'test'
encoder = WatermarkEncoder()
encoder.set_watermark('bytes', wm.encode('utf-8'))
bgr_encoded = encoder.encode(bgr, 'dwtDct')
cv2.imwrite('test_wm.png', bgr_encoded)

# 提取水印
from imwatermark import WatermarkDecoder
bgr = cv2.imread('test_wm.png')
decoder = WatermarkDecoder('bytes', 32)
watermark = decoder.decode(bgr, 'dwtDct')
print(watermark.decode('utf-8'))
```

#### 1.2 blind-watermark（推荐⭐⭐⭐⭐）
- **GitHub**: https://github.com/guofei9987/blind_watermark
- **PyPI**: `pip install blind-watermark`
- **特点**：
  - 基于DWT-DCT-SVD的盲水印
  - 支持字符串、图像、bit数组水印
  - 对旋转、裁剪、噪声等攻击有较强鲁棒性
  - 中文文档和示例丰富
  - 支持并发处理

```python
from blind_watermark import WaterMark

# 嵌入
bwm1 = WaterMark(password_img=1, password_wm=1)
bwm1.read_img('pic/ori_img.jpg')
bwm1.read_wm('pic/watermark.png')
bwm1.embed('output/embedded.png')

# 提取
bwm1 = WaterMark(password_img=1, password_wm=1)
bwm1.extract(filename='output/embedded.png', wm_shape=(128, 128), 
            out_wm_name='output/extracted.png')
```

#### 1.3 PyWavelets（基础库⭐⭐⭐）
- **PyPI**: `pip install PyWavelets`
- **特点**：
  - 提供DWT（离散小波变换）的底层实现
  - 可以用来构建自定义的水印算法
  - 广泛用于图像处理和信号处理

### 2. 视频数字水印库

#### 2.1 VideoSeal（Meta开源，推荐⭐⭐⭐⭐⭐）
- **GitHub**: https://github.com/facebookresearch/videoseal
- **特点**：
  - Meta开源的最新视频水印技术
  - 基于深度学习的编码器-解码器架构
  - 支持高分辨率视频和任意长度视频
  - 时间水印传播技术，提高效率
  - 对视频压缩、几何变换等攻击有很强鲁棒性
  - 支持96位水印容量

#### 2.2 RAWatermark（推荐⭐⭐⭐⭐）
- **GitHub**: https://github.com/jeremyxianx/RAWatermark
- **特点**：
  - 支持图像和视频水印
  - 即插即用框架，无需额外训练
  - 快速处理，高效的水印嵌入和提取
  - 提供可证明的假阳性率保证
  - 支持任意长度视频和可调水印强度

#### 2.3 blind-video-watermark（推荐⭐⭐⭐）
- **GitHub**: https://github.com/eluv-io/blind-video-watermark
- **PyPI**: `pip install blind-video-watermark`
- **特点**：
  - 基于DT CWT域的盲视频水印
  - 对压缩、缩放、裁剪、旋转等有较强鲁棒性
  - 支持帧率转换攻击检测

#### 2.4 传统视频水印方法
基于图像水印库扩展：
- 使用invisible-watermark对每帧进行处理
- 使用opencv处理视频帧序列
- 考虑时间同步和帧间关系

### 3. 音频数字水印库

#### 3.1 基于频域变换的方法
目前Python生态中缺乏成熟的音频数字水印专用库，主要依赖以下基础库：

- **librosa**: 音频处理和特征提取
- **scipy**: 信号处理，提供FFT、DCT等变换
- **pydub**: 音频文件操作
- **numpy**: 数值计算基础

#### 3.2 可实现的音频水印技术
- **DCT域水印**: 在音频的DCT系数中嵌入水印
- **DWT域水印**: 利用小波变换的多分辨率特性
- **扩频水印**: 使用伪随机序列扩展水印信号
- **回声隐藏**: 通过添加微小回声嵌入水印

```python
# 音频水印示例框架
import librosa
import numpy as np
from scipy.fft import dct, idct

def embed_audio_watermark(audio_file, watermark_data):
    # 加载音频
    y, sr = librosa.load(audio_file)
    
    # 分帧处理
    frame_length = 1024
    frames = librosa.util.frame(y, frame_length=frame_length, 
                               hop_length=frame_length//2)
    
    # DCT变换并嵌入水印
    for i, frame in enumerate(frames.T):
        dct_coeffs = dct(frame)
        # 在中频系数中嵌入水印
        # 具体实现需要根据水印算法设计
        modified_coeffs = embed_watermark_dct(dct_coeffs, watermark_data)
        frames[:, i] = idct(modified_coeffs)
    
    return frames
```

## 技术选型建议

### 图像水印
1. **首选**: invisible-watermark
   - 成熟稳定，算法多样
   - 性能良好，适合生产环境
   - 文档完善，易于集成

2. **备选**: blind-watermark
   - 中文支持好
   - 算法透明度高
   - 适合学习和定制

### 视频水印
1. **首选**: VideoSeal (如果能获得模型)
   - 最新技术，性能最佳
   - Meta官方支持

2. **备选**: RAWatermark
   - 开源可用
   - 性能优秀
   - 支持可证明保证

3. **实用方案**: 基于invisible-watermark扩展
   - 逐帧处理视频
   - 技术成熟可靠

### 音频水印
1. **推荐方案**: 基于librosa + scipy自实现
   - 使用DCT/DWT频域变换
   - 结合psychoacoustic masking
   - 考虑音频压缩鲁棒性

## 跨平台打包方案

### 1. PyInstaller（推荐）
```bash
pip install pyinstaller
pyinstaller --onefile --console main.py
```

### 2. cx_Freeze
```bash
pip install cx_freeze
# 配置setup.py后执行
python setup.py build
```

### 3. GitHub Actions自动打包
```yaml
name: Build Executables
on: [push, pull_request]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build executable
      run: pyinstaller --onefile main.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: executable-${{ matrix.os }}
        path: dist/
```

## 性能对比

| 库/方法 | 嵌入速度 | 提取速度 | 鲁棒性 | 容量 | 推荐度 |
|---------|----------|----------|--------|------|--------|
| invisible-watermark (dwtDct) | 快 | 快 | 中等 | 中等 | ⭐⭐⭐⭐⭐ |
| blind-watermark | 中等 | 中等 | 高 | 中等 | ⭐⭐⭐⭐ |
| VideoSeal | 快 | 快 | 很高 | 高 | ⭐⭐⭐⭐⭐ |
| RAWatermark | 很快 | 很快 | 高 | 中等 | ⭐⭐⭐⭐ |

## 实施建议

### 第一阶段：图像水印
1. 集成invisible-watermark库
2. 实现CLI接口（基于typer）
3. 添加基本的攻击测试

### 第二阶段：视频水印
1. 评估VideoSeal和RAWatermark
2. 实现视频处理pipeline
3. 优化内存使用和处理速度

### 第三阶段：音频水印
1. 基于librosa实现DCT域水印
2. 添加心理声学掩蔽
3. 测试音频压缩鲁棒性

### 第四阶段：系统集成
1. 统一CLI接口
2. 配置GitHub Actions
3. 生成跨平台可执行文件

## 依赖包列表

```txt
# 图像处理
opencv-python>=4.5.0
numpy>=1.21.0
pillow>=8.0.0

# 水印库
invisible-watermark>=0.1.5
blind-watermark>=0.2.1

# 音频处理
librosa>=0.8.1
pydub>=0.25.1
scipy>=1.7.0

# 视频处理
imageio[ffmpeg]>=2.9.0

# CLI框架
typer>=0.9.0
rich>=10.0.0

# 打包工具
pyinstaller>=5.0.0
```

## 总结

通过调研发现，Python生态中图像数字水印库相对成熟，推荐使用invisible-watermark作为主要解决方案。视频水印方面，新兴的深度学习方法（如VideoSeal）表现优异，但也可以通过扩展图像水印方法实现。音频水印需要基于底层音频处理库自行实现。整体技术路线可行，能够满足跨平台部署和CLI使用的需求。
