#!/usr/bin/env python3
"""
基本功能测试脚本
用于验证Media Seal的基本功能
"""

import subprocess
from pathlib import Path


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def test_basic_commands():
    """测试基本命令"""
    print("🔧 测试基本CLI功能...")

    # 测试版本命令
    print("  - 测试版本命令...")
    code, stdout, stderr = run_command("python main.py version")
    if code == 0:
        print("    ✓ 版本命令正常")
    else:
        print(f"    ✗ 版本命令失败: {stderr}")

    # 测试帮助命令
    print("  - 测试帮助命令...")
    code, stdout, stderr = run_command("python main.py --help")
    if code == 0:
        print("    ✓ 帮助命令正常")
    else:
        print(f"    ✗ 帮助命令失败: {stderr}")

    # 测试算法帮助
    print("  - 测试算法帮助...")
    code, stdout, stderr = run_command("python main.py help-algorithms")
    if code == 0:
        print("    ✓ 算法帮助正常")
    else:
        print(f"    ✗ 算法帮助失败: {stderr}")

def test_dependencies():
    """测试依赖安装状态"""
    print("📦 检查依赖状态...")

    required_packages = [
        "typer", "rich", "numpy", "opencv-python", "pillow",
        "librosa", "scipy", "pydub", "moviepy", "invisible-watermark", "blind-watermark"
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"    ✓ {package}")
        except ImportError:
            print(f"    ✗ {package} (未安装)")

def check_project_structure():
    """检查项目结构"""
    print("📁 检查项目结构...")

    required_files = [
        "main.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "build.spec",
        "watermark/__init__.py",
        "watermark/image_watermark.py",
        "watermark/audio_watermark.py",
        "watermark/video_watermark.py",
        ".github/workflows/build.yml",
        "examples/demo.py"
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"    ✓ {file_path}")
        else:
            print(f"    ✗ {file_path} (缺失)")

def main():
    """主函数"""
    print("🚀 Media Seal 基本功能测试")
    print("=" * 50)

    check_project_structure()
    print()
    test_dependencies()
    print()
    test_basic_commands()

    print("\n" + "=" * 50)
    print("✅ 测试完成!")
    print("\n💡 提示:")
    print("   - 如果看到依赖缺失，请运行: pip install -r requirements.txt")
    print("   - 查看完整功能演示: python examples/demo.py")
    print("   - 查看使用指南: cat QUICKSTART.md")

if __name__ == "__main__":
    main()
