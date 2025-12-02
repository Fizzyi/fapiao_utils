#!/bin/bash

echo "========================================"
echo "发票重命名工具 - 打包脚本"
echo "========================================"
echo ""

echo "[提示] 此脚本在 macOS/Linux 上运行"
echo "要打包成 Windows EXE，请在 Windows 系统上运行 build.bat"
echo ""

echo "[1/3] 检查依赖..."
if ! python -c "import pyinstaller" 2>/dev/null; then
    echo "正在安装 PyInstaller..."
    pip install pyinstaller
fi

echo "[2/3] 转换图标格式..."
python convert_icon.py
if [ $? -ne 0 ]; then
    echo "警告: 图标转换失败，请手动转换 SVG 为 ICO 格式"
    echo "或者使用在线工具: https://convertio.co/zh/svg-ico/"
    exit 1
fi

echo "[3/3] 注意: 在 macOS/Linux 上无法直接打包成 Windows EXE"
echo "请将项目复制到 Windows 系统，然后运行:"
echo "  build.bat"
echo ""
echo "或者使用 Wine + PyInstaller 进行交叉编译（不推荐）"

