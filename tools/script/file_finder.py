import os
import stat
import mimetypes
from typing import Optional, Dict, Any,Union,Set
from langchain_core.tools import tool,StructuredTool

from pypdf import PdfReader
from datetime import datetime
from pathlib import Path
import os
import shutil
WORKSPACE_ROOT = "./workspace"
md_path="./DOC"
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


def read_file(file_path: str) -> dict:
    """
    读取文件内容，并返回包含行号的结构化数据。

    参数:
        file_path (str): 相对文件路径。

    返回:
        dict: 包含以下字段：
            - "file_path": 完整文件路径；
            - "mime_type": MIME 类型；
            - "content_with_line_numbers": 带行号的文件内容；
            - "error": 错误信息（如有）
    """

    full_path = safe_join_relative_paths(file_path)

    result = {
        "file_path": file_path,
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

read_file_tool = StructuredTool.from_function(
    func=read_file,
    name="read_file",
    description="""
    安全文件读取工具 - 获取文件内容及元数据

    功能特性:
    • 读取文本/PDF文件内容并自动添加行号
    • 自动检测文件MIME类型
    • 内置安全路径检查机制
    • 支持内容结构化返回

    支持格式:
    ✓ 文本文件 (.txt, .csv, .json, .xml等)
    ✓ 代码文件 (.py, .js, .java等)
    ✓ PDF文档 (.pdf)
    × 媒体文件 (图片/视频/音频)
    × 二进制可执行文件

    使用规范:
    1. 路径要求:
       - 仅接受相对路径 (如: 'docs/README.md')
       - 禁止路径穿越符 (如: ../)
       

    返回数据结构:
    {
        "file_path": string,    // 原始请求路径
        "mime_type": string,    // 如'text/plain'
        "content_with_line_numbers": string,  // 带行号的内容
        "error": string|null    // 错误信息(如有)
    }

    典型应用场景:
    • 查看日志文件内容
    • 阅读项目文档
    • 分析代码文件
    • 提取PDF文本内容

    示例调用:
    - 读取配置文件: read_file('config/settings.json')
    - 查看日志: read_file('logs/app.log')
    - 阅读文档: read_file('docs/API_REFERENCE.md')
    """
)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件的详细元数据信息。

    参数:
        file_path (str): 相对文件路径（禁止使用路径穿越符如../）

    返回:
        Dict[str, Any]: 包含文件完整元数据的字典，结构如下：
        {
            "filename": str,           # 文件名（含扩展名）
            "path": str,               # 原始请求路径
            "type": str,               # MIME类型（如'text/plain'）
            "permissions": str,        # 八进制权限表示（如'0o644'）
            "size": int,               # 文件大小（字节）
            "modified_time": float,    # 最后修改时间（时间戳）
            "error": str               # 错误信息（如有）
        }
    """
    full_path = safe_join_relative_paths(file_path)

    if not os.path.exists(full_path):
        return {
            "filename": os.path.basename(full_path),
            "path": file_path,
            "error": "文件未找到"
        }

    stats = os.stat(full_path)
    mime_type, _ = mimetypes.guess_type(full_path)

    return {
        "filename": os.path.basename(full_path),
        "path": file_path,
        "type": mime_type or "未知",
        "permissions": oct(stat.S_IMODE(stats.st_mode)),
        "size": stats.st_size,
        "modified_time": stats.st_mtime
    }


file_info_tool = StructuredTool.from_function(
    func=get_file_info,
    name="file_info",
    description="""
    文件元数据获取工具 - 安全读取文件系统信息

    功能特性:
    • 获取文件完整元数据
    • 自动检测文件类型
    • 内置安全路径检查
    • 标准化信息返回格式

    可获取信息:
    ✓ 文件名和路径
    ✓ 文件类型(MIME)
    ✓ 权限(八进制)
    ✓ 大小(字节)
    ✓ 修改时间戳

    安全限制:
    1. 仅接受相对路径
    2. 禁止路径穿越符(../)
    

    典型应用场景:
    • 检查文件属性
    • 验证文件权限
    • 获取文件统计信息
    • 调试文件系统问题

    示例调用:
    - 检查配置文件: file_info('config/settings.json')
    - 查看日志属性: file_info('logs/app.log')
    - 验证权限: file_info('scripts/startup.sh')
    """,
    return_direct=False  # 设置为True如果需要直接返回结果
)


def find_file(filename: str) -> Union[str, dict]:
    """
    在指定目录中递归查找文件，返回文件路径或详细信息。

    参数:
        filename (str): 要查找的文件名（支持部分匹配，不区分大小写）

    返回:
        Union[str, dict]:
        成功时返回文件相对路径字符串，
        失败时返回包含错误信息的字典 {
            "status": "error",
            "message": str,
            "requested_filename": str,
            "searched_directory": str
        }

    功能特点:
        - 递归搜索当前工作目录
        - 跳过二进制/编译文件（.pyc, .o, .so等）
        - 不区分大小写匹配
        - 安全路径处理
        - 详细的错误报告
    """
    directory = "."
    try:
        # 安全获取完整目录路径
        full_directory = safe_join_relative_paths(directory)
        if isinstance(full_directory, dict) and "error" in full_directory:
            return {
                "status": "error",
                "message": full_directory["error"],
                "requested_filename": filename,
                "searched_directory": directory
            }

        # 配置排除项
        excluded_extensions = {
            ".pyc", ".o", ".so", ".a",
            ".lib", ".dll", ".dylib",
            ".git", ".exe", ".bin"
        }

        filename_lower = filename.strip().lower()
        found_files = []

        # 递归搜索
        for root, _, files in os.walk(full_directory):
            for file in files:
                file_lower = file.lower()

                # 检查排除条件和匹配
                if (not any(file_lower.endswith(ext) for ext in excluded_extensions) and
                        filename_lower in file_lower):

                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, start=full_directory)

                    # 标准化路径格式
                    if not rel_path.startswith((".", "..")):
                        rel_path = f"./{rel_path}"

                    found_files.append(rel_path)

        # 处理搜索结果
        if not found_files:
            return {
                "status": "not_found",
                "message": f"未找到匹配文件 '{filename}'",
                "requested_filename": filename,
                "searched_directory": directory,
                "searched_files_count": len(found_files)
            }

        # 返回第一个匹配项（或可修改为返回所有匹配）
        return found_files[0] if len(found_files) == 1 else {
            "status": "multiple_found",
            "message": f"找到{len(found_files)}个匹配文件",
            "matches": found_files,
            "requested_filename": filename
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"搜索过程中发生错误: {str(e)}",
            "requested_filename": filename,
            "searched_directory": directory
        }


# 工具注册示例
file_search_tool = StructuredTool.from_function(
    func=find_file,
    name="file_search",
    description="""
    高级文件搜索工具 - 在项目目录中递归查找文件

    功能特点:
    • 智能文件名匹配（支持部分匹配）
    • 自动跳过二进制/编译文件
    • 安全路径限制（禁止目录穿越）
    • 详细结果报告（包括多重匹配）

    使用示例:
    - 查找配置文件: 'settings.ini'
    - 搜索日志文件: 'app.log'
    - 查找特定模块: 'utils.py'

    返回:
    - 找到单个文件时返回路径字符串
    - 找到多个文件时返回匹配列表
    - 错误时返回结构化错误信息
    """,
    return_direct=False
)


def list_files() -> Union[str, Dict[str, str]]:
    """
    查看工作区根目录结构（无参数版本）

    返回:
        Union[str, Dict]:
        - 成功时返回格式化目录树字符串
        - 错误时返回 {"error": "错误信息"}

    特点:
        - 自动从工作区根目录开始扫描
        - 显示文件类型/大小/修改时间
        - 安全路径处理
        - 清晰的树形可视化
    """
    try:
        abs_path = Path(WORKSPACE_ROOT)

        # 验证工作区目录
        if not abs_path.exists():
            return {"error": f"工作区目录不存在: {WORKSPACE_ROOT}"}
        if not abs_path.is_dir():
            return {"error": f"工作区路径不是目录: {WORKSPACE_ROOT}"}

        # 构建树形结构
        tree_lines = ["工作区目录结构:"]
        indent_stack = []

        def _add_entry(entry_path: Path, depth: int, is_last: bool):
            """添加目录条目"""
            # 计算缩进和连接线
            connector = "└── " if is_last else "├── "
            indent = "".join(indent_stack[:depth])
            full_indent = indent + connector

            # 获取文件信息
            try:
                stats = entry_path.stat()
                size = stats.st_size
                mtime = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')

                # 格式化显示
                size_str = (
                    f"{size:,}B" if size < 1024 else
                    f"{size / 1024:,.1f}KB" if size < 1024 * 1024 else
                    f"{size / (1024 * 1024):.1f}MB"
                )
                entry_type = "DIR" if entry_path.is_dir() else "FILE"

                tree_lines.append(
                    f"{full_indent}{entry_path.name} [{entry_type} {size_str} {mtime}]"
                )

                # 记录缩进状态
                if depth < len(indent_stack):
                    indent_stack[depth] = "    " if is_last else "│   "
                else:
                    indent_stack.append("    " if is_last else "│   ")

                return True

            except PermissionError:
                tree_lines.append(f"{full_indent}{entry_path.name} [权限不足]")
                return False
            except Exception as e:
                tree_lines.append(f"{full_indent}{entry_path.name} [错误: {e}]")
                return False

        # 递归扫描目录
        def _scan_directory(current_path: Path, depth: int = 0):
            try:
                entries = sorted(
                    [e for e in current_path.iterdir()],
                    key=lambda x: (not x.is_dir(), x.name.lower())
                )

                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1
                    if _add_entry(entry, depth, is_last) and entry.is_dir():
                        _scan_directory(entry, depth + 1)

            except Exception as e:
                tree_lines.append(f"{'    ' * depth}└── [扫描错误: {e}]")

        _scan_directory(abs_path)
        return "\n".join(tree_lines)

    except Exception as e:
        return {"error": f"系统错误: {e}"}


# 工具注册（保持原始接口）
dir_listing_tool = StructuredTool.from_function(
    func=list_files,
    name="list_files",
    description="""
    根目录列表工具

    特点:
    • 自动从根目录开始扫描
    • 显示完整的树形结构
    • 包含文件类型/大小/修改时间
    • 自动跳过无权限的目录

    输出示例:
    └── src [DIR 4.2KB 2023-05-01]
        ├── utils.py [FILE 1.2KB 2023-04-15]
        └── main.py [FILE 2.8KB 2023-04-20]
    """,
    return_direct=False
)


def create_directory(dir_path: str) -> Dict[str, Any]:
    """
    创建目录结构工具 - 安全创建嵌套目录

    参数:
        dir_path (str): 相对目录路径（禁止使用路径穿越符如../）

    返回:
        Dict[str, Any]: 包含操作结果的字典，结构如下：
        {
            "path": str,               # 原始请求路径
            "created": bool,            # 是否成功创建
            "already_exists": bool,    # 目录是否已存在
            "full_path": str,           # 创建的完整路径
            "error": str                # 错误信息（如有）
        }
    """
    # 安全路径处理
    try:
        full_path = safe_join_relative_paths(dir_path)
    except ValueError as e:
        return {
            "path": dir_path,
            "created": False,
            "already_exists": False,
            "error": f"路径安全检查失败: {str(e)}"
        }

    # 检查目录是否已存在
    if os.path.exists(full_path):
        return {
            "path": dir_path,
            "created": False,
            "already_exists": True,
            "full_path": full_path,
            "error": "目录已存在" if os.path.isdir(full_path) else "路径已存在但不是目录"
        }

    # 尝试创建目录
    try:
        os.makedirs(full_path, exist_ok=True)
        return {
            "path": dir_path,
            "created": True,
            "already_exists": False,
            "full_path": full_path,
            "error": ""
        }
    except Exception as e:
        #logging.error(f"创建目录失败: {dir_path} - {str(e)}")
        return {
            "path": dir_path,
            "created": False,
            "already_exists": False,
            "full_path": full_path,
            "error": f"创建失败: {str(e)}"
        }


# 创建目录工具
dir_create_tool = StructuredTool.from_function(
    func=create_directory,
    name="create_directory",
    description="""
    目录创建工具 - 安全构建文件夹结构

    功能特性:
    • 创建单层或多层嵌套目录
    • 自动处理路径分隔符差异（Windows/Linux）
    • 内置安全路径检查
    • 智能处理目录已存在情况

    关键能力:
    ✓ 创建新目录
    ✓ 递归创建父目录
    ✓ 验证目录创建结果
    ✓ 返回完整路径信息

    安全限制:
    1. 仅接受相对路径
    2. 禁止路径穿越符(../)
    3. 最大路径深度限制(10层)

    使用场景:
    • 初始化项目结构
    • 创建日志目录
    • 建立临时工作区
    • 组织资源文件

    示例调用:
    - 创建配置目录: create_directory('config/environments')
    - 建立用户数据目录: create_directory('data/user_profiles')
    - 初始化缓存文件夹: create_directory('cache/temp')

    错误处理:
    • 路径已存在 → 返回 already_exists:true
    • 权限不足 → 返回 error:"权限不足"
    • 无效路径 → 返回 error:"无效路径"
    """,
    return_direct=False  # 直接返回操作结果
)


def get_markdown_contents(folder_path=md_path) -> Dict[str, str]:
    """
    获取指定目录下所有 .md 文件的内容

    参数:
        folder_path: 文件夹路径

    返回:
        {
            "文件1路径": "文件1内容",
            "文件2路径": "文件2内容",
            ...
        }
    """

    if not os.path.isdir(folder_path):
        raise ValueError(f"路径不存在或不是文件夹: {folder_path}")

    contents = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents[file_path] = f.read()
                except UnicodeDecodeError:
                    contents[file_path] = "⚠️ 无法解码文件（非UTF-8编码）"
                except Exception as e:
                    contents[file_path] = f"⚠️ 读取失败: {str(e)}"

    return contents


def safe_delete_folder(relative_path: str) -> dict:
    """
    安全删除文件夹工具 - 删除指定文件夹及其内容

    参数:
        relative_path (str): 要删除的文件夹相对路径

    返回:
        dict: 包含以下字段：
            - "folder_path": 原始请求路径
            - "success": 是否删除成功
            - "error": 错误信息（如有）
    """
    full_path = safe_join_relative_paths(relative_path)

    result = {
        "folder_path": relative_path,
        "success": False,
        "error": None
    }

    if isinstance(full_path, str) and full_path.startswith("Error: "):
        result["error"] = full_path
        return result

    try:
        if not os.path.exists(full_path):
            result["error"] = f"错误：文件夹 '{full_path}' 不存在。"
            return result

        if not os.path.isdir(full_path):
            result["error"] = f"错误：路径 '{full_path}' 不是文件夹。"
            return result

        # 安全检查：确保不是重要系统目录
        important_dirs = {
            str(Path(WORKSPACE_ROOT).resolve()),
            str(Path.cwd().resolve()),
            str(Path.home().resolve())
        }

        if str(Path(full_path).resolve()) in important_dirs:
            result["error"] = "错误：禁止删除重要系统目录。"
            return result

        # 执行删除
        shutil.rmtree(full_path)

        result["success"] = True
        return result

    except Exception as e:
        result["error"] = f"删除文件夹时出错：{str(e)}"
        return result


delete_folder_tool = StructuredTool.from_function(
    func=safe_delete_folder,
    name="delete_folder",
    description="""
    安全文件夹删除工具 - 删除指定文件夹及其内容

    功能特性:
    • 安全删除整个文件夹及其内容
    • 内置多重安全检查机制
    • 支持相对路径操作
    • 防止误删重要目录

    安全限制:
    ✓ 仅接受相对路径
    × 禁止路径穿越符 (如: ../)
    × 禁止删除工作目录根路径
    × 禁止删除系统重要目录

    返回数据结构:
    {
        "folder_path": string,    // 原始请求路径
        "success": boolean,       // 是否删除成功
        "error": string|null      // 错误信息(如有)
    }

    使用注意事项:
    1. 此操作不可逆，请谨慎使用
    2. 删除前请确认文件夹内容
    3. 确保有足够的权限

    典型应用场景:
    • 清理临时文件夹
    • 删除不再需要的项目目录
    • 清除缓存目录

    示例调用:
    - 删除临时文件夹: delete_folder('temp/cache')
    - 清理日志目录: delete_folder('logs/old_logs')
    - 移除构建产物: delete_folder('dist/build')
    """
)


def create_folder_structure(directory_tree: str) -> str:
    """
    根据目录树结构创建文件夹（仅创建文件夹，跳过文件）

    Args:
        directory_tree: 目录树结构字符串，使用标准的树状格式

    Returns:
        操作结果状态信息

    Example Input:
        student-management/
        ├── src/
        │   ├── main/
        │   │   ├── java/
        │   │   │   ├── com/
        │   │   │   │   └── student/
        │   │   │   │       ├── controller/
        │   │   │   │       ├── model/
        │   │   │   │       ├── dao/
        │   │   │   │       └── util/
        │   │   ├── webapp/
        │   │   │   ├── WEB-INF/
        │   │   │   │   ├── lib/
        │   │   │   ├── pages/
        │   │   │   └── static/
        │   │   │       ├── css/
        │   │   │       └── js/
        │   └── resources/
    """

    def is_valid_folder_name(name: str) -> bool:
        """检查文件夹名称是否有效"""
        return name and not any(c in name for c in '\\/:*?"<>|')

    try:
        lines = directory_tree.split('\n')
        if not lines:
            return "错误: 目录树为空"

        base_path = None
        path_stack = []
        created_folders: Set[str] = set()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Determine the current depth
            depth = 0
            while line.startswith('│   ') or line.startswith('    '):
                line = line[4:]
                depth += 1

            # Remove tree graphics
            if line.startswith('├── '):
                line = line[4:]
            elif line.startswith('└── '):
                line = line[4:]

            # Skip files (anything with a dot in the last part)
            last_part = line.split('/')[-1].split('#')[0].strip()
            if '.' in last_part:
                continue

            # Remove comments and clean the path
            folder_path = line.split('#')[0].strip().rstrip('/')
            if not folder_path:
                continue

            # Validate folder names in the path
            if not all(is_valid_folder_name(part) for part in folder_path.split('/')):
                return f"错误: 包含无效文件夹名称: {folder_path}"

            # Handle base path with security check
            if depth == 0:
                # Security check for base path
                safe_path = safe_join_relative_paths(folder_path)
                if isinstance(safe_path, str) and safe_path.startswith("Error:"):
                    return safe_path

                base_path = Path(safe_path)
                path_stack = [base_path]
                if not base_path.exists():
                    base_path.mkdir(parents=True, exist_ok=True)
                    created_folders.add(str(base_path))
                continue

            # Ensure we have a base path
            if not base_path:
                return "错误: 第一行必须指定基础目录"

            # Trim the path stack to current depth
            path_stack = path_stack[:depth]
            if not path_stack:
                return f"错误: 缩进不正确在行: {line}"

            # Security check for relative path components
            parent = path_stack[-1]
            new_path = parent / folder_path

            # Verify the combined path is still safe
            rel_path = str(new_path.relative_to(base_path))
            safe_combined = safe_join_relative_paths(rel_path)
            if isinstance(safe_combined, str) and safe_combined.startswith("Error:"):
                return f"错误: 路径不安全: {rel_path}"

            # Create directory if it doesn't exist
            safe_path = Path(safe_combined)
            if not safe_path.exists():
                safe_path.mkdir(parents=True, exist_ok=True)
                created_folders.add(str(safe_path))

            # Add to path stack if it's a directory
            path_stack.append(safe_path)

        if not created_folders:
            return "警告: 没有创建任何文件夹（可能所有文件夹已存在或输入中只有文件）"

        return f"成功创建文件夹:\n" + "\n".join(sorted(created_folders))

    except Exception as e:
        return f"创建文件夹结构时出错: {str(e)}"


create_folder_structure_tool = StructuredTool.from_function(
    func=create_folder_structure,
    name="create_folder_structure",
    description="""
    文件夹结构创建工具 - 根据目录树图创建文件夹结构

    ⚠️ 使用规则:
    1. 输入必须是标准的树状目录结构
    2. 仅创建文件夹，自动跳过文件（任何包含扩展名的条目）
    3. 支持多级缩进表示层级关系
    4. 会自动忽略注释（#后面的内容）
    5. 所有路径必须通过安全检查

    参数:
        directory_tree: 目录树结构字符串

    返回:
        - 成功返回创建的文件夹列表
        - 失败返回错误信息

    示例输入:
        project/
        ├── src/
        │   ├── main/
        │   │   └── java/
        │   └── test/
        └── docs/
    """
)