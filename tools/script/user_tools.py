import os
import stat
import mimetypes
from langgraph.types import interrupt
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
def ask_user_question(question: str, context: Optional[str] = None) -> Dict[str, Any]:
    """向用户提问并等待回答"""
    try:
        # 构建提问数据
        interrupt_data = {
            "question": question,
            "type": "user_question",
            "timestamp": None  # 可以添加时间戳
        }

        # 如果有上下文信息，添加到中断数据中
        if context:
            interrupt_data["context"] = context

        # 使用 LangGraph 的 interrupt 功能暂停执行并等待用户输入
        user_response = interrupt(interrupt_data)

        return {
            "question": question,
            "answer": user_response,
            "status": "success"
        }

    except Exception as e:
        return {
            "question": question,
            "answer": None,
            "status": "error",
            "error": str(e)
        }


# 创建结构化工具
user_question_tool = StructuredTool.from_function(
    func=ask_user_question,
    name="ask_user",
    description="""
    用户提问工具 - 基于 LangGraph 人机协同功能实现交互式提问。

    🤖 功能特性：
    1. 暂停图形执行，向用户展示问题
    2. 等待用户输入回答
    3. 收集用户反馈并继续执行流程
    4. 支持上下文信息展示

    ⚠️ 使用要求：
    1. 必须在配置了 checkpointer 的 LangGraph 环境中使用
    2. 需要通过 Command(resume=answer) 来恢复执行
    3. 图形必须有有效的 thread_id 配置

    参数:
        - question (str): 要向用户提出的问题（必填）
        - context (str, 可选): 相关上下文信息，帮助用户理解问题背景

    返回:
        - Dict: 包含问题、答案和状态的字典
          {
            "question": "提出的问题",
            "answer": "用户的回答",
            "status": "success/error"
          }

    使用示例:
    1. 简单提问: ask_user("请输入您的姓名")
    2. 带上下文: ask_user("是否确认删除？", "将删除 users.db 中的所有记录")
    3. 选择题: ask_user("请选择操作方式：1-自动 2-手动", "当前检测到多个配置文件")

    恢复执行:
    ```python
    # 图形暂停后，使用以下方式恢复：
    graph.invoke(Command(resume="用户的回答"), config=thread_config)
    ```
    """
)