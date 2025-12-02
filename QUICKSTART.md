# 快速打包指南

## 🚀 一键打包（Windows）

在 Windows 系统上，直接运行：

```bash
build.bat
```

脚本会自动：
1. 检查并安装 PyInstaller
2. 将 SVG 图标转换为 ICO 格式
3. 打包成 EXE 文件

打包完成后，EXE 文件位于：`dist/发票重命名工具.exe`

## 📋 手动打包步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 转换图标

```bash
# 安装转换工具
pip install cairosvg pillow

# 转换图标
python convert_icon.py
```

**或者**使用在线工具手动转换：
- https://convertio.co/zh/svg-ico/
- 将 `rename_utils/icon.svg` 转换为 `rename_utils/icon.ico`

### 3. 执行打包

```bash
pyinstaller build.spec
```

## ⚠️ 重要提示

1. **必须在 Windows 系统上打包**：macOS/Linux 无法直接打包成 Windows EXE
2. **图标格式**：PyInstaller 需要 ICO 格式，不是 SVG
3. **测试**：打包后建议在干净的 Windows 系统上测试

## 📁 项目结构

```
fapiao_utils/
├── rename_utils/
│   ├── main.py          # 主程序入口
│   ├── func.py          # 核心功能
│   ├── icon.svg         # SVG 图标（源文件）
│   └── icon.ico         # ICO 图标（转换后，用于打包）
├── requirements.txt     # Python 依赖
├── build.spec          # PyInstaller 配置文件
├── convert_icon.py     # 图标转换脚本
├── build.bat           # Windows 打包脚本
└── build.sh            # macOS/Linux 打包脚本（仅转换图标）
```

## 🔧 自定义打包选项

编辑 `build.spec` 文件可以自定义：
- 程序名称（`name='发票重命名工具'`）
- 图标路径（`icon='rename_utils/icon.ico'`）
- 是否显示控制台（`console=False`）
- 隐藏导入的模块（`hiddenimports`）

## ❓ 常见问题

**Q: 为什么打包后的文件很大？**  
A: 这是正常的，PyInstaller 会打包所有依赖（包括 PyQt6 和 pdfplumber）。

**Q: 可以在 macOS 上打包成 Windows EXE 吗？**  
A: 不可以，需要在 Windows 系统上打包。可以使用虚拟机或 Windows 电脑。

**Q: 打包后运行报错？**  
A: 检查是否在 Windows 系统上打包，并确保安装了 Visual C++ Redistributable。

