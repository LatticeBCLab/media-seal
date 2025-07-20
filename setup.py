#!/usr/bin/env python3
"""
Media Seal 环境配置和安装脚本
支持 uv 和 pip 两种包管理工具
"""

import subprocess
import sys


def run_command(cmd, check=True):
    """运行命令并返回结果"""
    print(f"🔧 执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def check_uv_available():
    """检查uv是否可用"""
    try:
        result = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_with_uv():
    """使用uv安装依赖"""
    print("📦 使用 uv 安装依赖...")

    # 初始化项目
    if not run_command("uv sync", check=False):
        print("⚠️  uv sync 失败，尝试手动解决依赖冲突...")

        # 尝试单独安装有问题的包
        problematic_packages = [
            "numba>=0.58.0",
            "librosa>=0.10.0",
            "scipy>=1.9.0"
        ]

        for package in problematic_packages:
            print(f"尝试安装 {package}...")
            if not run_command(f"uv add '{package}'", check=False):
                print(f"❌ {package} 安装失败")
            else:
                print(f"✅ {package} 安装成功")

        # 尝试安装其余依赖
        print("安装其余依赖...")
        run_command("uv sync", check=False)

    # 安装开发依赖
    print("安装开发依赖...")
    run_command("uv sync --group dev", check=False)

def install_with_pip():
    """使用pip安装依赖"""
    print("📦 使用 pip 安装依赖...")

    # 升级pip
    run_command(f"{sys.executable} -m pip install --upgrade pip")

    # 按顺序安装依赖，避免冲突
    base_packages = [
        "numpy>=1.21.0",
        "scipy>=1.9.0",
        "numba>=0.58.0",
        "typer>=0.16.0",
        "rich>=13.0.0"
    ]

    for package in base_packages:
        print(f"安装 {package}...")
        run_command(f"{sys.executable} -m pip install '{package}'")

    # 安装其余依赖
    run_command(f"{sys.executable} -m pip install -r requirements.txt")

def create_alternative_requirements():
    """创建兼容性更好的依赖版本"""
    alt_requirements = """# 兼容性优化版本 - 适用于Python 3.11+
typer>=0.16.0
rich>=13.0.0

# 图像处理
opencv-python>=4.5.0
numpy>=1.21.0,<2.0.0
pillow>=8.0.0

# 基础科学计算（优先安装）
scipy>=1.9.0,<1.12.0
numba>=0.58.0,<0.60.0

# 水印库
blind-watermark>=0.2.1
PyWavelets>=1.3.0

# 音频处理（可能需要降级）
librosa>=0.9.2,<0.11.0
pydub>=0.25.1
soundfile>=0.12.1
audioread>=3.0.0

# 视频处理
imageio>=2.9.0
moviepy>=1.0.3

# 工具库
tqdm>=4.64.0
"""

    with open("requirements-alt.txt", "w", encoding="utf-8") as f:
        f.write(alt_requirements)

    print("✅ 创建了 requirements-alt.txt 兼容性版本")

def main():
    """主函数"""
    print("🚀 Media Seal 环境配置")
    print("=" * 50)

    # 检查Python版本
    python_version = sys.version_info
    print(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 11):
        print("⚠️  建议使用 Python 3.11 或更高版本")

    # 创建替代requirements文件
    create_alternative_requirements()

    # 选择包管理工具
    if check_uv_available():
        print("✅ 检测到 uv，使用 uv 进行包管理")
        install_with_uv()
    else:
        print("⚠️  未检测到 uv，使用 pip 进行包管理")
        print("💡 建议安装 uv 以获得更好的包管理体验: pip install uv")
        install_with_pip()

    # 测试安装
    print("\n🧪 测试安装...")
    if run_command(f"{sys.executable} main.py version", check=False):
        print("✅ 安装成功！")
    else:
        print("❌ 安装可能有问题，请检查错误信息")
        print("\n🔧 故障排除建议:")
        print("1. 尝试使用兼容版本: pip install -r requirements-alt.txt")
        print("2. 如果是 librosa 问题，尝试: pip install librosa==0.9.2")
        print("3. 如果是 numba 问题，尝试: pip install numba==0.58.1")

    print("\n📚 接下来的步骤:")
    print("1. 运行基本测试: python test_basic.py")
    print("2. 查看使用指南: cat QUICKSTART.md")
    print("3. 运行演示: python examples/demo.py")

if __name__ == "__main__":
    main()
