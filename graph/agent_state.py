from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)
from typing_extensions import TypedDict, List, Literal,Optional, Dict, Any,Union

class AgentState(TypedDict):
    messages: List[BaseMessage]         # 所有对话历史（用户 + AI）
    current_agent: Literal["file_assistant_1", "file_assistant_2"]  # 当前活跃 agent
    last_output: str                    # 最后一次 agent 输出的内容（用于路由）
    iterations: int                     # 已执行的迭代次数（防止无限循环）
    config: Optional[Dict[str, Any]]    # 配置信息，包含 thread_id 等
    done: bool
    max_history: Optional[int]