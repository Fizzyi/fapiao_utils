@echo off
chcp 65001 >nul
echo ========================================
echo 发票重命名工具 - 打包脚本
echo ========================================
echo.

echo [1/3] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

echo [2/3] 转换图标格式...
python convert_icon.py
if errorlevel 1 (
    echo 警告: 图标转换失败，请手动转换 SVG 为 ICO 格式
    echo 或者使用在线工具: https://convertio.co/zh/svg-ico/
    pause
    exit /b 1
)

echo [3/3] 开始打包...
pyinstaller build.spec

if exist "dist\发票重命名工具.exe" (
    echo.
    echo ========================================
    echo 打包成功！
    echo 可执行文件位置: dist\发票重命名工具.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 打包失败，请检查错误信息
    echo ========================================
)

pause

