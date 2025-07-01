from graph.agent_state import AgentState
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)
from langgraph.graph import StateGraph,START,END
from typing_extensions import TypedDict, List, Literal,Optional, Dict, Any,Union



def Coder_Agent_input_state(state: AgentState) -> Dict[str, Any]:

    message="查看文档内容，开始编写代码/no_think"
    # 返回更新的状态
    return {
        "messages": [HumanMessage(content=message)],#list[HumanMessage]
        "last_output": message,#str
        "iterations": state["iterations"] + 1
    }