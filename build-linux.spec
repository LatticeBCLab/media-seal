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
    # 只保留invisible_watermark需要的torch最小组件
    'torch',
    'torch._C',
    'torch.nn',
    'torch.nn.functional',
]

# 额外的二进制文件
binaries = []

# Linux特定的大型排除项 - 更激进的优化
excludes = [
    # PyTorch相关 - 排除不必要的组件
    'torch.distributed',
    'torch.multiprocessing', 
    'torch.cuda',
    'torch.backends.cuda',
    'torch.backends.cudnn',
    'torch.backends.mkl',
    'torch.backends.mkldnn',
    'torch.jit',
    'torch.onnx',
    'torch.quantization',
    'torch.autograd.profiler',
    'torch.utils.tensorboard',
    'torch.utils.data.dataloader',
    'torch.utils.benchmark',
    'torch.fx',
    'torch.package',
    'torch.profiler',
    
    # 机器学习框架
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
    
    # Jupyter和开发工具
    'jupyter',
    'notebook',
    'IPython',
    'sympy',
    'statsmodels',
    
    # GUI框架
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'tkinter',
    'wx',
    'gi',
    'gtk',
    'qt',
    
    # 文档和测试
    'sphinx',
    'docs',
    'examples',
    'demo',
    
    # Linux特定的大型库排除
    'multiprocessing.spawn',
    'multiprocessing.forkserver',
    'distutils',
    'setuptools',
    'pip',
    'wheel',
    'pkg_resources',
    
    # 网络和Web相关
    'urllib3',
    'requests',
    'http',
    'email',
    'html',
    'json',
    'xml',
    
    # 数据库相关
    'sqlite3',
    'dbm',
    
    # 其他不需要的标准库
    'curses',
    'readline',
    'rlcompleter',
    'pdb',
    'profile',
    'pstats',
    'trace',
    'calendar',
    'locale',
    'gettext',
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

# 过滤掉一些大型的二进制文件
def filter_binaries(binaries):
    filtered = []
    skip_patterns = [
        'libcuda',  # CUDA库
        'libcudnn', # CuDNN库
        'libmkl',   # Intel MKL库
        'libblas',  # BLAS库（如果不需要高性能计算）
        'liblapack', # LAPACK库
        '.debug',   # 调试信息
        '_debug',   # 调试版本
        'test_',    # 测试文件
        '_test',    # 测试文件
    ]
    
    for binary in binaries:
        skip = False
        for pattern in skip_patterns:
            if pattern in binary[1].lower():  # binary[1]是文件名
                skip = True
                break
        if not skip:
            filtered.append(binary)
    
    return filtered

# 应用二进制文件过滤
a.binaries = filter_binaries(a.binaries)

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
    upx=True,    # 启用UPX压缩
    upx_exclude=[], # 不排除任何文件的UPX压缩
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 