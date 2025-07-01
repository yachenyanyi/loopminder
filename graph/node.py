from graph.agent_state import AgentState
from agent.agent import Project_Analyst,Project_Manager,System_Architect,Database_Design,Task_Extraction,Coder,File_Saver_0,File_Saver_1,File_Saver_2,File_Saver_3,folder,Code_Reviewer,Intelligent_Assistant
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)
from langgraph.types import interrupt
from langgraph.graph import StateGraph,START,END
from typing_extensions import TypedDict, List, Literal,Optional, Dict, Any,Union
def Project_Analyst_Agent(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function：调用 Project_Analyst Agent 并更新状态。

    参数:
        state (AgentState): 当前图状态

    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 正在运行 Project_Analyst Agent...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }




    # 调用 agent
    result = Project_Analyst.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )

    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    last_message=last_message.content if last_message else ""
    #print("------------------------------")
    #print(output_messages)
    #print("------------------------------")
    #print(last_message)#需求分析字符串
    #print("------------------------------")
    # 返回更新的状态
    return {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
def Project_Manager_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 Project_Manager_Agent...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }



    # 调用 agent
    result = Project_Manager.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )

    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    print("------------------------------")
    print(output_messages)
    print("------------------------------")
    print(last_message)#需求分析字符串
    print("------------------------------")
    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_message.content if last_message else "",
        "iterations": state["iterations"] + 1
    }

def System_Architect_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 System_Architect_Agent...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }



    # 调用 agent
    result = System_Architect.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_message.content if last_message else "",
        "iterations": state["iterations"] + 1
    }
def Database_Design_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 Database_Design_Agent...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }


    # 调用 agent
    result = Database_Design.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_message.content if last_message else "",
        "iterations": state["iterations"] + 1
    }
def Bash_Agent(state: AgentState) -> dict:
    pass
def Task_Extraction_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 Task_Extraction_Agent...")
    input_messages = state["last_output"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_data = {
        "messages": [HumanMessage(content=input_messages)],
    }


    # 调用 agent
    result = Task_Extraction.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )
    #for i in result["messages"]:
        #print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_message.content if last_message else "",
        "iterations": state["iterations"] + 1
    }


def manage_history(
        messages: List[BaseMessage],
        max_history: Optional[int] = None
) -> List[BaseMessage]:
    """
    管理历史消息长度，确保不破坏 tool_calls -> tool 的关联关系

    Args:
        messages: 原始消息列表
        max_history: 最大保留条数，None表示不限制

    Returns:
        处理后的消息列表，保证 tool 消息始终跟随对应的 tool_calls
    """
    # 1. 如果没有长度限制，直接返回
    if max_history is None or max_history <= 0:
        return messages

    # 2. 如果要保留的消息比实际少，直接返回
    if len(messages) <= max_history:
        return messages

    # 3. 从后往前截取消息，但需要检查 tool 消息的关联性
    truncated = messages[-max_history:]

    # 4. 检查第一条消息是否是 tool 消息但没有对应的 tool_calls
    first_msg = truncated[0]
    if first_msg.type == "tool":
        # 查找原始列表中这条 tool 消息对应的 tool_calls
        for i, msg in enumerate(messages[:-max_history]):
            if (msg.type == "assistant" and
                    hasattr(msg, "tool_calls") and
                    any(tc.id == first_msg.tool_call_id for tc in msg.tool_calls)):
                # 把对应的 assistant 消息也加入
                return messages[i:-max_history + 1] + truncated[1:]

        # 如果没有找到对应的 tool_calls，丢弃这条孤立的 tool 消息
        return truncated[1:]

    return truncated
def Coder_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 Coder_Agent...")
    #input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }


    # 调用 agent
    result = Coder.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    # 检查是否包含终止标记
    is_done = True
    last_output_content = ""

    if last_message:
        last_output_content = last_message.content
        # 检查输出中是否包含终止标记 [DONE]
        if "[DONE]" in last_output_content:
            is_done = False
            print("✅ 检测到终止标记 [DONE]，任务完成！")
            last_output_content = last_output_content.replace("[DONE]", "").strip()

            # 更新最后一条消息的内容
            last_message.content = last_output_content
            output_messages[-1] = last_message
        else:
            print("🔄 未检测到终止标记，继续执行...")

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_output_content,
        "iterations": state["iterations"] + 1,
        "done": is_done  # 根据终止标记设置done状态
    }
def Code_Review_Agent(state: AgentState) -> dict:
    print("🔄 正在运行 Code_Review_Agent...")
    #input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }


    # 调用 agent
    result = Code_Reviewer.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
        stream_mode="values",  # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    # 检查是否包含终止标记
    is_done = True
    last_output_content = ""

    if last_message:
        last_output_content = last_message.content
        # 检查输出中是否包含终止标记 [DONE]
        if "[DONE]" in last_output_content:
            is_done = False
            print("✅ 检测到终止标记 [DONE]，任务完成！")
            last_output_content = last_output_content.replace("[DONE]", "").strip()

            # 更新最后一条消息的内容
            last_message.content = last_output_content
            output_messages[-1] = last_message
        else:
            print("🔄 未检测到终止标记，继续执行...")

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_output_content,
        "iterations": state["iterations"] + 1,
        "done": is_done  # 根据终止标记设置done状态
    }
def routing_function(state: AgentState) -> bool:
    if state["done"]:

        return True

    return False
def Loop_Coder_Agent(state: AgentState) -> Dict[str, Any]:
    """
    {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")
    orgin_messages=state["messages"]
    orgin_last_output=state["last_output"]
    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = Coder.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": orgin_messages,  # 已经在analyst_node中清理过
        "last_output": orgin_last_output,  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }



def Loop_Project_Analyst_Agent(state: AgentState) -> dict:
    """
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")

    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = File_Saver_0.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": state["messages"],  # 已经在analyst_node中清理过
        "last_output": state["last_output"],  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }

def Loop_File_Saver_Agent_0(state: AgentState) -> Dict[str, Any]:
    """
    {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")
    orgin_messages=state["messages"]
    orgin_last_output=state["last_output"]
    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = File_Saver_0.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": orgin_messages,  # 已经在analyst_node中清理过
        "last_output": orgin_last_output,  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }
def Loop_File_Saver_Agent_1(state: AgentState) -> Dict[str, Any]:
    """
    {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")
    orgin_messages=state["messages"]
    orgin_last_output=state["last_output"]
    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = File_Saver_1.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": orgin_messages,  # 已经在analyst_node中清理过
        "last_output": orgin_last_output,  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }
def Loop_File_Saver_Agent_2(state: AgentState) -> Dict[str, Any]:
    """
    {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")
    orgin_messages=state["messages"]
    orgin_last_output=state["last_output"]
    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = File_Saver_2.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": orgin_messages,  # 已经在analyst_node中清理过
        "last_output": orgin_last_output,  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }
def Loop_File_Saver_Agent_3(state: AgentState) -> Dict[str, Any]:
    """
    {
        "messages": output_messages,#list[HumanMessage]
        "last_output": last_message,#str
        "iterations": state["iterations"] + 1
    }
    LangGraph Node Function：使用内部图结构实现自动循环执行
    参数:
        state (AgentState): 当前图状态
    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 启动 Loop_File_Saver_Agent (内部图循环模式)...")
    orgin_messages=state["messages"]
    orgin_last_output=state["last_output"]
    # 定义内部图状态
    class InnerState(TypedDict):
        messages: List[BaseMessage]
        iterations: int
        done: bool

    # 1. 创建内部图
    inner_graph = StateGraph(InnerState)

    # 2. 定义节点 - 实际调用 Project_Analyst
    def analyst_node(state: InnerState) -> dict:
        print(f"🔧 内部图调用 (迭代 {state['iterations']})...")
        input_data = {"messages": state["messages"]}

        result = File_Saver_3.invoke(
            input=input_data,
            config=state.get("config", {}),
            stream_mode="values",
        )

        output_messages = result.get("messages", [])
        print(output_messages)
        last_message = output_messages[-1].content if output_messages else ""

        # 检查完成条件
        done = "[DONE]" in last_message

        # 方案2：简洁处理 - 只处理包含[DONE]的最后一条消息
        if done and output_messages and "[DONE]" in output_messages[-1].content:
            # 清理最后一条消息中的[DONE]标记
            last_content = output_messages[-1].content.replace("[DONE]", "").strip()

            if not last_content:
                # 如果清理后内容为空，移除最后一条消息
                output_messages = output_messages[:-1]
            else:
                # 创建清理后的消息，保持原有类型
                original_msg = output_messages[-1]
                if isinstance(original_msg, HumanMessage):
                    cleaned_msg = HumanMessage(content=last_content)
                elif isinstance(original_msg, AIMessage):
                    cleaned_msg = AIMessage(content=last_content)
                else:
                    # 保持原有类型
                    cleaned_msg = type(original_msg)(content=last_content)

                # 替换最后一条消息
                output_messages = output_messages[:-1] + [cleaned_msg]

        return {
            "messages": output_messages,
            "iterations": state["iterations"] + 1,
            "done": done
        }

    # 3. 定义条件判断
    def should_continue(state: InnerState) -> Literal["continue", "end"]:
        if state["done"]:
            print("✅ 任务完成，退出内部循环")
            return "end"
        if state["iterations"] >= 5:  # 安全限制
            print("⚠️ 达到最大迭代次数，退出内部循环")
            return "end"
        return "continue"

    # 4. 构建内部图结构
    inner_graph.add_node("analyst", analyst_node)
    inner_graph.set_entry_point("analyst")

    # 添加条件边
    inner_graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "analyst",  # 继续循环
            "end": END  # 结束循环
        }
    )

    # 5. 编译内部图
    runnable = inner_graph.compile()
    initial_message = HumanMessage(content=state["last_output"])

    # 6. 准备初始状态
    inner_state = InnerState(
        messages=[initial_message],
        iterations=0,
        done=False,
        config=state.get("config", {})
    )

    # 7. 执行内部图
    final_state = runnable.invoke(inner_state)

    # 8. 处理最终输出，确保不包含[DONE]
    final_messages = final_state["messages"]
    last_output = ""

    if final_messages:
        last_content = final_messages[-1].content
        # 从last_output中移除[DONE]标记（双重保险）
        last_output = last_content.replace("[DONE]", "").strip()

    print(f"🏁 内部图完成，共 {final_state['iterations']} 轮迭代")

    return {
        "messages": orgin_messages,  # 已经在analyst_node中清理过
        "last_output": orgin_last_output,  # 确保不包含[DONE]
        "iterations": state["iterations"] + 1
    }

def Dir_Creater_agent(state: AgentState) -> dict:
    print("🔄 正在运行 Dir_Creat_agent...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }


    # 调用 agent
    result = folder.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
          # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    # 检查是否包含终止标记
    is_done = True
    last_output_content = ""

    if last_message:
        last_output_content = last_message.content
        # 检查输出中是否包含终止标记 [DONE]
        if "DONE" in last_output_content:
            is_done = False
            print("✅ 检测到终止标记 [DONE]，任务完成！")
            last_output_content = last_output_content.replace("[DONE]", "").strip()

            # 更新最后一条消息的内容
            last_message.content = last_output_content
            output_messages[-1] = last_message
        else:
            print("🔄 未检测到终止标记，继续执行...")

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_output_content,
        "iterations": state["iterations"] + 1,
        "done": is_done  # 根据终止标记设置done状态
    }


from langchain_core.messages import HumanMessage
from langgraph.types import interrupt


def User_Input_Node(state: AgentState) -> AgentState:
    """
    用户输入中断节点 - 将用户输入作为新消息加入状态
    整合历史消息管理逻辑和终止标记检测

    参数:
        state (AgentState): 当前代理状态

    返回:
        AgentState: 更新后的状态，包含用户输入作为新消息
    """
    print("⏸️ 用户输入节点：等待用户反馈...")
    print("当前状态:", state)

    # 安全获取状态字段
    last_output = state.get("last_output", "无输出")
    current_agent = state.get("current_agent", "未知代理")
    iterations = state.get("iterations", 0)
    config = state.get("config", {"configurable": {"thread_id": "default"}})
    max_history = state.get("max_history")

    # 准备中断上下文信息
    context = {
        "last_output": last_output,
        "current_agent": current_agent,
        "iteration": iterations
    }

    # 触发中断获取用户输入
    user_input = interrupt(
        {
            "system": "需要您的输入来继续工作流",
            "context": context,
            "prompt": "请输入您的反馈或指令（输入[DONE]终止流程）"
        }
    )

    print(f"✅ 收到用户输入: {user_input}")

    # 创建新的用户消息
    user_message = HumanMessage(content=user_input)

    # 更新消息历史（使用 manage_history 管理历史长度）
    current_messages = state.get("messages", [])
    updated_messages = current_messages + [user_message]
    updated_messages = manage_history(updated_messages, max_history)

    # 检查是否包含终止标记 [DONE]
    workflow_done = True  # 默认继续工作流

    if "[DONE]" in user_input:
        print("✅ 检测到终止标记 [DONE]，工作流终止！")
        # 清理终止标记
        cleaned_content = user_input.replace("[DONE]", "").strip()
        # 更新消息内容
        user_message.content = cleaned_content
        # 更新消息列表中的最后一条消息
        updated_messages[-1] = user_message
        workflow_done = False  # 终止工作流
    else:
        print("🔄 用户输入节点完成，工作流继续...")

    print("更新后的消息历史:", updated_messages)

    # 返回更新的状态
    return {
        "messages": updated_messages,
        "current_agent": current_agent,
        "last_output": cleaned_content if "[DONE]" in user_input else user_input,
        "iterations": iterations + 1,
        "config": config,
        "done": workflow_done,  # 根据终止标记设置工作流状态
        "max_history": max_history
    }

def Intelligent_Assistant_Agent(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function：调用 Project_Analyst Agent 并更新状态。

    参数:
        state (AgentState): 当前图状态

    返回:
        dict: 更新后的状态字段（如 messages, last_output, iterations）
    """
    print("🔄 正在运行 Intelligent_Assistant...")
    input_messages = state["messages"]#注意--------注意#
    config = state["config"]
    # 构造输入参数
    input_messages = manage_history(
        state["messages"],
        state.get("max_history")
    )
    input_data = {
        "messages": input_messages,
            #HumanMessage(content=input_messages),
    }


    # 调用 agent
    result = Intelligent_Assistant.invoke(
        input=input_data,
        config=config,  # 可配置 thread_id
          # 默认返回最终状态值
    )
    for i in result["messages"]:
        print(i)
    # 提取输出消息
    output_messages = result.get("messages", [])

    last_message = output_messages[-1] if output_messages else None
    # 检查是否包含终止标记
    is_done = True
    last_output_content = ""

    if last_message:
        last_output_content = last_message.content
        # 检查输出中是否包含终止标记 [DONE]
        if "DONE" in last_output_content:
            is_done = False
            print("✅ 检测到终止标记 [DONE]，任务完成！")
            last_output_content = last_output_content.replace("[DONE]", "").strip()

            # 更新最后一条消息的内容
            last_message.content = last_output_content
            output_messages[-1] = last_message
        else:
            print("🔄 未检测到终止标记，继续执行...")

    # 返回更新的状态
    return {
        "messages": output_messages,
        "last_output": last_output_content,
        "iterations": state["iterations"] + 1,
        "done": is_done  # 根据终止标记设置done状态
    }
