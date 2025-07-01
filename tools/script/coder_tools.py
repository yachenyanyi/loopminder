import os
import stat
import mimetypes
from typing import Optional, Dict, Any,Union
from langchain_core.tools import tool,StructuredTool

from pypdf import PdfReader
from datetime import datetime
from pathlib import Path
import os
WORKSPACE_ROOT = "./workspace"
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
file_write_tool = StructuredTool.from_function(
    func=write_file,
    name="file_write",
    description="""
    文件写入工具（覆盖模式）。将指定内容写入目标路径，若文件已存在则完全覆盖。

    ⚠️ 安全规则：
    1. 仅接受相对路径（如 "data/notes.txt"）
    2. 严格禁止路径穿越符（../ 或 ..\\）
    

    参数:
        - file_path (str): 目标文件相对路径（示例: "src/main.py"）
        - text (str): 要写入的文本内容

    返回:
        - 成功返回写入路径，失败返回错误原因

    示例:
    1. 写入文本: file_write("log.txt", "2023-01-01 system started")
    2. 写入JSON: file_write("config.json", '{"timeout": 30}')
    """
)


def replace_text_between_lines(file_path: str, new_text: str, start_line: int, end_line: int) -> str:
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


replace_tool = StructuredTool.from_function(
    func=replace_text_between_lines,
    name="file_replace_range",
    description="""
    文件范围替换工具 - 替换指定行范围内的内容

    ⚠️ 使用规则：
    1. 使用简单相对路径（如 "data/notes.txt"）
    2. 禁止路径穿越符（../）
    3. 行号从1开始计数（包含两端）
    4. 新内容将完全替换指定行范围内的原始内容

    参数:
        - file_path: 目标文件相对路径
        - new_text: 要写入的新内容（支持多行文本）
        - start_line: 开始替换的行号（包含）
        - end_line: 结束替换的行号（包含）

    示例:
    1. 替换第3-5行: 
       file_replace_range("log.txt", "修正内容", 3, 5)
    2. 替换单行: 
       file_replace_range("config.ini", "debug=true", 10, 10)

    返回:
        - 成功返回操作结果，失败返回错误信息
    """
)
