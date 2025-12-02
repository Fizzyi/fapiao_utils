import re
import pdfplumber
from pathlib import Path
from typing import Optional


def parse_tax_pdf(filename):
    data = {}
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            fphm = re.findall(r'\b\d{20}\b', text)[0]
            data["fphm"] = fphm
            fpsj = re.findall(r'\d{4}年(?:0[1-9]|1[0-2])月(?:0[1-9]|[12][0-9]|3[01])日', text)[0]
            data["fpsj"] = fpsj
            table = page.extract_table()
            table = process_data(table)
            for line in table:
                if line[0] == "购买方信息":
                    gfmc = re.findall(r'名称：(.*?)统一社会信用代码', line[1])[0]
                    gfsh = re.findall(r'识别号：(.*?)$', line[1])[0]
                    data["gfmc"] = gfmc
                    data["gfsh"] = gfsh
                if len(line) > 2 and line[2] == "销售方信息":
                    xfmc = re.findall(r'名称：(.*?)统一社会信用代码', line[3])[0]
                    xfsh = re.findall(r'识别号：(.*?)$', line[3])[0]
                    data["xfmc"] = xfmc
                    data["xfsh"] = xfsh
                if line[0] == "价税合计（大写）":
                    jshj = re.findall(r'¥(.*?)$', line[1])[0]
                    data["fpje"] = jshj.replace(" ","")
    return data


def process_data(data):
    """
    定义一个函数来提取特定值或映射为空,处理■,□后面的取值
    """

    def extract_value(item):
        if '□' in item and '■' in item:
            return re.findall(r'(?<=■).*?(?=□)|(?<=■).*', item)[0].strip()  # ■' 后面的值 修正 ■是□否 类似情况
        elif '■' in item:
            return re.findall(r'■(.*)', item)[0].strip()  # 提取 '■' 后面的值
        elif '□' in item:
            return ''  # 将特定格式的字符串映射为空
        else:
            return item.replace('\n', '')  # 去除换行符

    # 使用列表解析来处理数据 去除None
    return [[extract_value(item) for item in sublist if item is not None] for sublist in data]


def rename_file(old_file_path: str, new_file_path: str) -> Optional[str]:
    """
    重命名文件，保留原文件所在目录和后缀（除非新文件名指定后缀）

    参数：
        old_file_path: 原文件的完整路径（绝对路径或相对路径）
        new_file_name: 新文件名称（可带后缀，如 "new.pdf"；也可不带，如 "new"，将保留原后缀）

    返回：
        成功：新文件的完整路径（字符串）
        失败：None（并打印错误信息）
    """
    # 转换为 Path 对象，方便路径操作
    old_path = Path(old_file_path)

    # 校验原文件是否存在
    if not old_path.exists():
        print(f"错误：原文件不存在 → {old_file_path}")
        return None

    # 校验原路径是否是文件（不是目录）
    if not old_path.is_file():
        print(f"错误：路径不是文件 → {old_file_path}")
        return None

    try:
        # 执行重命名（rename 方法会移动文件到新路径，同目录下就是重命名）
        old_path.rename(new_file_path)
        print(f"重命名成功：{old_file_path} → {new_file_path}")
        # 转换为字符串返回（兼容后续可能的字符串路径操作）
        return str(new_file_path)
    except PermissionError:
        print(f"错误：权限不足，无法重命名 → {old_file_path}")
    except Exception as e:
        print(f"错误：重命名失败 → {str(e)}")

    return None


def rename_main(file_url: str, new_file_url: str, title_dict: dict) -> Optional[bool]:
    print(file_url, new_file_url, title_dict)
    tax_data = parse_tax_pdf(file_url)
    print("解析数据为:", tax_data)
    title_params_list = title_dict["title_params_list"]
    separator = title_dict["separator"]
    param_values = [tax_data[key] for key in title_params_list]
    params_text = separator.join(param_values)
    new_file_name = f"/{params_text}.pdf"
    new_file_path = rename_file(file_url, new_file_url + new_file_name)
    if new_file_path:
        print(f"文件重命名成功：{file_url} → {new_file_path}")
        return True
    else:
        print(f"文件重命名失败：{file_url}")
        return False


