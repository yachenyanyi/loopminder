import os
import stat
import mimetypes
from typing import Optional, Dict, Any,Union
from langchain_core.tools import tool,StructuredTool

from pypdf import PdfReader
from datetime import datetime
from pathlib import Path
import os
WORKSPACE_ROOT = "./DOC"
Project_Analyst_md="项目需求分析.md"
Project_Manager_md="项目开发计划.md"
System_Architect_md="项目架构设计.md"
Database_Design_md="数据库设计方案.md"
def safe_join_relative_paths(relative_path: str) -> str:
    """
    安全地合并工作目录和相对路径
    注意：这个不是ai工具
    参数:
        relative_path: 要合并的相对路径

    返回:
        成功: 合并后的安全路径
        失败: 以"Error: "开头的错误信息字符串
    """
    try:
        # 转换为Path对象
        base = Path(WORKSPACE_ROOT)
        rel = Path(relative_path)

        # 检查是否是绝对路径
        if rel.is_absolute():
            return f"Error: 路径必须是相对路径，但得到: {relative_path}"

        # 检查路径是否安全（不包含路径遍历）
        def is_safe(path: Path) -> bool:
            try:
                return (
                        not path.is_absolute()
                        and not any(p == ".." for p in path.parts)
                        and path.resolve().relative_to(Path.cwd())
                )
            except (RuntimeError, ValueError):
                return False

        if not is_safe(rel):
            return f"Error: 路径不安全: {relative_path}"

        # 安全地合并路径
        combined = (base / rel).resolve().relative_to(Path.cwd())

        # 确保结果仍然是相对路径
        if combined.is_absolute():
            return "Error: 意外错误：合并后得到了绝对路径"

        return str(combined)

    except Exception as e:
        return f"Error: 处理路径时发生意外错误: {str(e)}"

def write_file(file_path: str, text: str) -> str:
    """将文本内容写入指定路径的文件"""
    full_path = safe_join_relative_paths(file_path)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"成功写入文件：{file_path}"
    except Exception as e:
        return f"写入失败：{str(e)}"

def md_read_file(file_path: str) -> dict:
    """
    读取文件内容，并返回包含行号的结构化数据。

    参数:
        file_path (str): 相对文件路径。

    返回:
        dict: 包含以下字段：
            - "file_name": 文件名；
            - "mime_type": MIME 类型；
            - "content_with_line_numbers": 带行号的文件内容；
            - "error": 错误信息（如有）
    """

    full_path = safe_join_relative_paths(file_path)

    result = {
        "file_name": file_path,
        "mime_type": None,
        "content_with_line_numbers": "",
        "error": None
    }

    if not os.path.exists(full_path):
        result["error"] = f"错误：文件 '{full_path}' 不存在。"
        return result

    mime_type, _ = mimetypes.guess_type(full_path)
    result["mime_type"] = mime_type

    if mime_type and mime_type.startswith(('image/', 'video/', 'audio/')):
        result["error"] = "不支持的文件类型：图像、视频或音频文件暂不支持。"
        return result

    try:
        # 处理 PDF 文件
        if mime_type == "application/pdf":
            reader = PdfReader(full_path)
            content = '\n'.join([page.extract_text() for page in reader.pages])

        # 处理其他文本文件
        elif mime_type and mime_type.startswith('text/'):
            with open(full_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
        else:
            # 二进制文件尝试以文本方式读取（替换乱码）
            with open(full_path, 'rb') as file:
                content = file.read().decode('utf-8', errors='replace')

        # 添加行号
        lines = content.splitlines()
        content_with_lines = '\n'.join(f"{i + 1}: {line}" for i, line in enumerate(lines))

        result["content_with_line_numbers"] = content_with_lines
        return result

    except Exception as e:
        result["error"] = f"读取文件时出错：{e}"
        return result

def md_replace_text_between_lines(file_path: str, new_text: str, start_line: int, end_line: int) -> str:
    """
    替换文件中指定行范围内的内容

    Args:
        file_path: 目标文件路径（相对路径）
        new_text: 要替换的新内容（将替换start_line到end_line之间的内容）
        start_line: 开始替换的行号（从1开始计数）
        end_line: 结束替换的行号（包含在内）

    Returns:
        操作结果状态信息
    """
    full_path = safe_join_relative_paths(file_path)

    try:
        # 验证路径安全性
        if isinstance(full_path, str) and full_path.startswith("Error:"):
            return full_path

        # 读取原始文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证行号有效性
        total_lines = len(lines)
        if start_line < 1 or start_line > total_lines:
            return f"错误：起始行号 {start_line} 超出范围（文件共 {total_lines} 行）"
        if end_line < start_line or end_line > total_lines:
            return f"错误：结束行号 {end_line} 无效（必须 ≥ {start_line} 且 ≤ {total_lines}）"

        # 处理换行符：确保新文本以换行符结束（如果是多行内容则保持原样）
        processed_text = new_text
        if not new_text.endswith('\n') and end_line == start_line:
            processed_text += '\n'

        # 构建新内容（保留前start_line-1行 + 新内容 + 保留end_line之后的行）
        new_content = (
                ''.join(lines[:start_line - 1]) +
                processed_text +
                ''.join(lines[end_line:])
        )

        # 写入文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"成功替换 {file_path} 的第 {start_line}-{end_line} 行内容"

    except FileNotFoundError:
        return f"错误：文件 '{file_path}' 不存在"
    except PermissionError:
        return f"错误：没有写入权限 '{file_path}'"
    except Exception as e:
        return f"替换失败：{str(e)}"
#----------------------------------------------

def Project_Analyst_md_write(text: str) -> str:
    result = write_file(Project_Analyst_md, text)
    return result

Project_Analyst_md_write = StructuredTool.from_function(
    func=Project_Analyst_md_write,
    name="Project_Analyst_file_write",
    description="""
    文件写入工具（覆盖模式）。将指定内容写入"项目需求分析.md"，若文件已存在则完全覆盖。

    参数:
        - text (str): 要写入的文本内容
    返回:
        - 成功返回写入文件名，失败返回错误原因

    示例:
    1. 写入文本: Project_Analyst_file_write("2023-01-01 system started")
    2. 写入JSON: Project_Analyst_file_write('{"timeout": 30}')
    """
)


def Project_Analyst_md_read() -> str:
    result = md_read_file(Project_Analyst_md)
    return result
Project_Analyst_md_read = StructuredTool.from_function(
    func=Project_Analyst_md_read,
    name="Project_Analyst_read_file",
    description="""
    直接读取"项目需求分析.md"的内容
    使用规范:
    无需传入参数
    返回数据结构:
    {
        "file_name": string,    // 文件名
        "mime_type": string,    // 如'text/plain'
        "content_with_line_numbers": string,  // 带行号的内容
        "error": string|null    // 错误信息(如有)
    }
    示例调用:
    - 读取文件: Project_Analyst_read_file()
    """
)


def Project_Analyst_md_replace(new_text: str, start_line: int, end_line: int)-> str:
    result = md_replace_text_between_lines(Project_Analyst_md, new_text, start_line, end_line)
    return result
Project_Analyst_md_replace = StructuredTool.from_function(
    func=Project_Analyst_md_replace,
    name="Project_Analyst_file_replace_range",
    description="""
    "项目需求分析.md"文件范围替换工具 - 替换指定行范围内的内容
    ⚠️ 使用规则：
    3. 行号从1开始计数（包含两端）
    4. 新内容将完全替换指定行范围内的原始内容
    参数:
        - new_text: 要写入的新内容（支持多行文本）
        - start_line: 开始替换的行号（包含）
        - end_line: 结束替换的行号（包含）
    示例:
    1. 替换第3-5行: 
       Project_Analyst_file_replace_range( "修正内容", 3, 5)
    2. 替换单行: 
       Project_Analyst_file_replace_range("debug=true", 10, 10)
    返回:
        - 成功返回操作结果，失败返回错误信息
    """
)
#----------------------------------------------


def Project_Manager_md_write(text: str) -> str:
    result = write_file(Project_Manager_md, text)
    return result
Project_Manager_md_write = StructuredTool.from_function(
    func=Project_Manager_md_write,
    name="Project_Manager_file_write",
    description="""
    文件写入工具（覆盖模式）。将指定内容写入"项目开发计划.md"，若文件已存在则完全覆盖。
    参数:
        - text (str): 要写入的文本内容
    返回:
        - 成功返回写入文件名，失败返回错误原因
    示例:
    1. 写入文本: Project_Manager_file_write("2023-01-01 system started")
    2. 写入JSON: Project_Manager_file_write('{"timeout": 30}')
    """
)


def Project_Manager_md_read() -> str:
    result = md_read_file(Project_Manager_md)
    return result
Project_Manager_md_read = StructuredTool.from_function(
    func=Project_Manager_md_read,
    name="Project_Manager_read_file",
    description="""
    直接读取"项目开发计划.md"的内容
    使用规范:
    无需传入参数
    返回数据结构:
    {
        "file_name": string,    // 文件名
        "mime_type": string,    // 如'text/plain'
        "content_with_line_numbers": string,  // 带行号的内容
        "error": string|null    // 错误信息(如有)
    }
    示例调用:
    - 读取文件: Project_Manager_read_file()
    """
)


def Project_Manager_md_replace(new_text: str, start_line: int, end_line: int)-> str:
    result = md_replace_text_between_lines(Project_Manager_md, new_text, start_line, end_line)
    return result
Project_Manager_md_replace = StructuredTool.from_function(
    func=Project_Manager_md_replace,
    name="Project_Manager_file_replace_range",
    description="""
    "项目开发计划.md"文件范围替换工具 - 替换指定行范围内的内容
    ⚠️ 使用规则：
    3. 行号从1开始计数（包含两端）
    4. 新内容将完全替换指定行范围内的原始内容
    参数:
        - new_text: 要写入的新内容（支持多行文本）
        - start_line: 开始替换的行号（包含）
        - end_line: 结束替换的行号（包含）
    示例:
    1. 替换第3-5行: 
       Project_Manager_file_replace_range( "修正内容", 3, 5)
    2. 替换单行: 
       Project_Manager_file_replace_range("debug=true", 10, 10)
    返回:
        - 成功返回操作结果，失败返回错误信息
    """
)
#----------------------------------------------


def System_Architect_md_write(text: str) -> str:
    result = write_file(System_Architect_md, text)
    return result
System_Architect_md_write = StructuredTool.from_function(
    func=System_Architect_md_write,
    name="System_Architect_file_write",
    description="""
    文件写入工具（覆盖模式）。将指定内容写入"项目架构设计.md"，若文件已存在则完全覆盖。
    参数:
        - text (str): 要写入的文本内容
    返回:
        - 成功返回写入文件名，失败返回错误原因
    示例:
    1. 写入文本: System_Architect_file_write("2023-01-01 system started")
    2. 写入JSON: System_Architect_file_write('{"timeout": 30}')
    """
)


def System_Architect_md_read() -> str:
    result = md_read_file(System_Architect_md)
    return result
System_Architect_md_read = StructuredTool.from_function(
    func=System_Architect_md_read,
    name="System_Architect_read_file",
    description="""
    直接读取"项目架构设计.md"的内容
    使用规范:
    无需传入参数
    返回数据结构:
    {
        "file_name": string,    // 文件名
        "mime_type": string,    // 如'text/plain'
        "content_with_line_numbers": string,  // 带行号的内容
        "error": string|null    // 错误信息(如有)
    }
    示例调用:
    - 读取文件: System_Architect_read_file()
    """
)


def System_Architect_md_replace(new_text: str, start_line: int, end_line: int)-> str:
    result = md_replace_text_between_lines(System_Architect_md, new_text, start_line, end_line)
    return result
System_Architect_md_replace = StructuredTool.from_function(
    func=System_Architect_md_replace,
    name="System_Architect_file_replace_range",
    description="""
    "项目架构设计.md"文件范围替换工具 - 替换指定行范围内的内容
    ⚠️ 使用规则：
    3. 行号从1开始计数（包含两端）
    4. 新内容将完全替换指定行范围内的原始内容
    参数:
        - new_text: 要写入的新内容（支持多行文本）
        - start_line: 开始替换的行号（包含）
        - end_line: 结束替换的行号（包含）
    示例:
    1. 替换第3-5行: 
       System_Architect_file_replace_range( "修正内容", 3, 5)
    2. 替换单行: 
       System_Architect_file_replace_range("debug=true", 10, 10)
    返回:
        - 成功返回操作结果，失败返回错误信息
    """
)
#----------------------------------------------


def Database_Design_md_write(text: str) -> str:
    result = write_file(Database_Design_md, text)
    return result
Database_Design_md_write = StructuredTool.from_function(
    func=Database_Design_md_write,
    name="Database_Design_file_write",
    description="""
    文件写入工具（覆盖模式）。将指定内容写入"数据库设计方案.md"，若文件已存在则完全覆盖。
    参数:
        - text (str): 要写入的文本内容
    返回:
        - 成功返回写入文件名，失败返回错误原因
    示例:
    1. 写入文本: Database_Design_file_write("2023-01-01 system started")
    2. 写入JSON: Database_Design_file_write('{"timeout": 30}')
    """
)


def Database_Design_md_read() -> str:
    result = md_read_file(Database_Design_md)
    return result
Database_Design_md_read = StructuredTool.from_function(
    func=Database_Design_md_read,
    name="Database_Design_read_file",
    description="""
    直接读取"数据库设计方案.md"的内容
    使用规范:
    无需传入参数
    返回数据结构:
    {
        "file_name": string,    // 文件名
        "mime_type": string,    // 如'text/plain'
        "content_with_line_numbers": string,  // 带行号的内容
        "error": string|null    // 错误信息(如有)
    }
    示例调用:
    - 读取文件: Database_Design_read_file()
    """
)


def Database_Design_md_replace(new_text: str, start_line: int, end_line: int)-> str:
    result = md_replace_text_between_lines(Database_Design_md, new_text, start_line, end_line)
    return result
Database_Design_md_replace = StructuredTool.from_function(
    func=Database_Design_md_replace,
    name="Database_Design_file_replace_range",
    description="""
    "数据库设计方案.md"文件范围替换工具 - 替换指定行范围内的内容
    ⚠️ 使用规则：
    3. 行号从1开始计数（包含两端）
    4. 新内容将完全替换指定行范围内的原始内容
    参数:
        - new_text: 要写入的新内容（支持多行文本）
        - start_line: 开始替换的行号（包含）
        - end_line: 结束替换的行号（包含）
    示例:
    1. 替换第3-5行: 
       Database_Design_file_replace_range( "修正内容", 3, 5)
    2. 替换单行: 
       Database_Design_file_replace_range("debug=true", 10, 10)
    返回:
        - 成功返回操作结果，失败返回错误信息
    """
)
#----------------------------------------------