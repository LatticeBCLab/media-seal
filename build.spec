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
    'opencv-python',
    'cv2',
    'PIL',
    'invisible_watermark',
    'librosa',
    'soundfile',
    'scipy',
    'audioread',
    'numba',
    'imageio',
    'tqdm',
    'PyWavelets',
    'pywt',
]

# 额外的二进制文件
binaries = []

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    strip=False,
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
