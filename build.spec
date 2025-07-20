# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# 获取项目根目录
project_root = Path(__file__).parent

# 数据文件和隐藏导入
datas = []
hiddenimports = [
    'numpy',
    'scipy',
    'cv2',
    'librosa',
    'pydub',
    'moviepy',
    'rich',
    'typer',
    'pathlib',
    'tempfile',
    'imageio',
    'PIL',
    'imwatermark',
    'blind_watermark',
    'pywt',
    'sklearn',
    'sklearn.utils._weight_vector',
    'numba',
    'numba.core',
    'numba.typed',
    'resampy',
    'soundfile',
    'audioread',
    'decorator',
    'pooch',
    'joblib',
    'packaging',
]

# 添加可能的二进制文件
binaries = []

# Windows特定配置
if sys.platform == "win32":
    hiddenimports.extend([
        'win32api',
        'win32con',
        'win32gui',
        'win32clipboard',
    ])

# macOS特定配置
if sys.platform == "darwin":
    hiddenimports.extend([
        'Foundation',
        'AppKit',
    ])

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'jupyter',
        'notebook',
        'IPython',
        'sphinx',
        'pytest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 排除不必要的文件
def exclude_files(toc):
    """排除不必要的文件以减小包大小"""
    excluded_patterns = [
        'test',
        'tests',
        '__pycache__',
        '.pyc',
        '.pyo',
        '.git',
        'doc',
        'docs',
        'examples',
        'sample',
        'samples',
        '.md',
        '.txt',
        '.rst',
        'LICENSE',
        'CHANGELOG',
        'MANIFEST',
    ]
    
    new_toc = []
    for item in toc:
        path = item[0].lower()
        include = True
        for pattern in excluded_patterns:
            if pattern in path:
                include = False
                break
        if include:
            new_toc.append(item)
    return new_toc

a.datas = exclude_files(a.datas)
a.binaries = exclude_files(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    icon=None,  # 可以添加图标文件路径
) 