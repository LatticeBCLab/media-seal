# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path.cwd()

# 数据文件和隐藏导入
datas = []
hiddenimports = [
    'watermark',
    'watermark.audio_watermark',
    'watermark.image_watermark', 
    'watermark.video_watermark',
    'typer',
    'rich',
    'numpy',
    'cv2',
    'PIL',
    'invisible_watermark',
    'librosa',
    'soundfile',
    'scipy.fft',
    'scipy.signal',
    'scipy.io',
    'scipy.interpolate',
    'audioread',
    'numba',
    'imageio',
    'tqdm',
    'pywt',
]

# 额外的二进制文件
binaries = []

# 排除不需要的大型模块
excludes = [
    'torchvision', 
    'torchaudio',
    'tensorflow',
    'keras',
    'sklearn',
    'scikit-learn',
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    'jupyter',
    'notebook',
    'IPython',
    'sympy',
    'statsmodels',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'tkinter',
    'wx',
    'gi',
    'gtk',
    'qt',
    'sphinx',
    'docs',
    'examples',
    'demo',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='media-seal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用strip来减小二进制大小
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
