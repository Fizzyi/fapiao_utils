"""
将 SVG 图标转换为 ICO 格式
需要安装: pip install cairosvg pillow
"""
import os
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("请先安装依赖: pip install cairosvg pillow")
    exit(1)

def svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """
    将 SVG 文件转换为 ICO 格式
    
    Args:
        svg_path: SVG 文件路径
        ico_path: 输出的 ICO 文件路径
        sizes: ICO 文件包含的尺寸列表
    """
    # 读取 SVG 文件
    svg_file = Path(svg_path)
    if not svg_file.exists():
        print(f"错误: SVG 文件不存在: {svg_path}")
        return False
    
    # 创建 PIL Image 对象列表
    images = []
    
    for size in sizes:
        # 将 SVG 转换为 PNG (字节流)
        png_data = cairosvg.svg2png(
            url=str(svg_file),
            output_width=size,
            output_height=size
        )
        
        # 从字节流创建 PIL Image
        img = Image.open(io.BytesIO(png_data))
        images.append(img)
    
    # 保存为 ICO 格式
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images]
    )
    
    print(f"成功转换: {svg_path} -> {ico_path}")
    return True

if __name__ == "__main__":
    svg_path = "rename_utils/icon.svg"
    ico_path = "rename_utils/icon.ico"
    
    if svg_to_ico(svg_path, ico_path):
        print(f"\n图标已转换为: {ico_path}")
        print("现在可以使用 build.spec 文件进行打包了")
    else:
        print("转换失败")

