# Copyright (C) 2025 YachenYanyi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import os
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)
from graph.graph import create_graphs_with_context
from langgraph.types import Command
import json
graph_full, graph_simple=create_graphs_with_context()
def convert_messages_to_dict(messages):
    """将消息列表中的消息对象转换为字典"""
    converted = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
            converted.append({
                "type": type(msg).__name__,
                "content": msg.content
            })
        else:
            # 处理其他类型的消息
            converted.append(str(msg))
    return converted
def start_workflow():
    """主启动函数，让用户选择工作流模式并执行"""
    # 1. 用户选择模式
    print("=" * 50)
    print("欢迎使用智能工作流系统")
    print("请选择工作模式：")
    print("1. 简单对话模式 - 快速问答")
    print("2. 大型构建模式 - 项目开发")
    print("=" * 50)

    mode_choice = input("请输入选择 (1/2): ").strip()

    # 2. 根据选择初始化不同状态
    if mode_choice == "1":
        # 简单对话模式初始化
        print("\n🔹 进入简单对话模式")
        user_input = input("请输入您的问题: ")

        initial_states = {
            "messages": [HumanMessage(content=user_input)],
            "last_output": user_input,
            "iterations": 0,
            "config": {"configurable": {"thread_id": "simple_chat"}},
            "done": True,
            "max_history": 20
        }
        graph = graph_simple  # 使用简单对话图
        share_config = {"configurable": {"thread_id": "simple_chat"}, "recursion_limit": 20}

    elif mode_choice == "2":
        # 大型构建模式初始化
        print("\n🔹 进入大型构建模式")
        print("请确认项目需求 (输入任意内容继续):")
        project_desc = input("或输入自定义项目描述: ")

        if not project_desc.strip():
            project_desc = "根据已学的JSP知识和相应的技术，设计一个学生信息管理系统..."
        share_config = {"configurable": {"thread_id": "project_build"}, "recursion_limit": 50}
        initial_states = {
            "messages": [HumanMessage(content=project_desc)],
            "current_agent": "软件需求分析",
            "last_output": project_desc,
            "iterations": 0,
            "config": {"configurable": {"thread_id": "project_build"}},
            "done": True,
            "max_history": 40
        }
        graph = graph_full  # 使用完整构建图


    else:
        print("❌ 无效选择，程序退出")
        return

    # 3. 启动工作流
    print("\n🚀 启动工作流...")
    result = graph.invoke(initial_states, config=share_config)

    # 4. 中断处理循环
    while True:
        if "__interrupt__" in result:
            print("\n⏸️ 工作流已暂停，等待用户输入...")

            # 获取中断信息
            interrupt_data = result["__interrupt__"][0].value

            # 展示中断信息
            print(f"\n系统消息: {interrupt_data.get('system', '')}")
            print(f"上下文: {interrupt_data.get('context', {})}")
            print(f"提示: {interrupt_data.get('prompt', '请输入')}")

            # 获取用户输入
            user_input = input("\n请在此输入 (输入[DONE]结束流程): ")

            # 恢复执行
            result = graph.invoke(
                Command(resume=user_input),
                config=share_config
            )
        else:
            # 没有中断，工作流完成
            print("\n✅ 工作流执行完成!")
            break

    # 5. 显示最终结果
    print("\n🎉 最终工作流结果:")

    # 创建可序列化的结果副本
    result_to_print = result.copy()

    # 转换消息列表
    if "messages" in result_to_print:
        result_to_print["messages"] = convert_messages_to_dict(result_to_print["messages"])

    # 打印结果
    print(json.dumps(result_to_print, indent=2, ensure_ascii=False))
    print("\n工作流结束!")


# 启动程序
if __name__ == "__main__":
    start_workflow()

