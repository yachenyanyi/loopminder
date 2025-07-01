from graph.agent_state import AgentState
from langgraph.graph import StateGraph,START,END
from graph.node import Project_Analyst_Agent,Project_Manager_Agent,System_Architect_Agent,Database_Design_Agent,Bash_Agent,Task_Extraction_Agent,Loop_Coder_Agent,Code_Review_Agent,Coder_Agent,Dir_Creater_agent,User_Input_Node,Intelligent_Assistant_Agent
from graph.node import Loop_File_Saver_Agent_0,Loop_File_Saver_Agent_1,Loop_File_Saver_Agent_2,Loop_File_Saver_Agent_3
from graph.state_node import Coder_Agent_input_state
from graph.node import routing_function
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
# 使用内存中的 SQLite 数据库（也可以指定文件路径）
def create_graphs_with_context():
    """创建图，不使用上下文管理器"""

    # 创建检查点（不使用 with）
    #memory_full = SqliteSaver.from_conn_string("file:graph_full.db")
    #memory_simple = SqliteSaver.from_conn_string("file:graph_simple.db")


    # 方法1：直接创建 SqliteSaver 实例
    memory_full = SqliteSaver(conn=sqlite3.connect("graph_full.db", check_same_thread=False))
    memory_simple = SqliteSaver(conn=sqlite3.connect("graph_simple.db", check_same_thread=False))

    # 构建完整图
    builder = StateGraph(AgentState)
    builder.add_node("软件需求分析", Project_Analyst_Agent)
    builder.add_node("文档保存0", Loop_File_Saver_Agent_0)
    builder.add_node("开发计划", Project_Manager_Agent)
    builder.add_node("文档保存1", Loop_File_Saver_Agent_1)
    builder.add_node("系统架构", System_Architect_Agent)
    builder.add_node("文档保存2", Loop_File_Saver_Agent_2)
    builder.add_node("数据库设计", Database_Design_Agent)
    builder.add_node("文档保存3", Loop_File_Saver_Agent_3)
    builder.add_node("命令行执行", Bash_Agent)
    builder.add_node("任务抽取", Task_Extraction_Agent)
    builder.add_node("代码编写", Coder_Agent)
    builder.add_node("代码检查", Code_Review_Agent)
    builder.add_node("文件夹创建", Dir_Creater_agent)
    builder.add_node("初始化代码智能体输入", Coder_Agent_input_state)
    builder.add_node("用户输入", User_Input_Node)
    builder.add_node("用户输入1", User_Input_Node)

    # 添加边
    builder.add_edge(START, "用户输入")
    builder.add_edge("用户输入", "软件需求分析")
    builder.add_edge("软件需求分析", "文档保存0")
    builder.add_edge("文档保存0", "开发计划")
    builder.add_edge("开发计划", "文档保存1")
    builder.add_edge("文档保存1", "系统架构")
    builder.add_edge("系统架构", "文档保存2")
    builder.add_edge("文档保存2", "数据库设计")
    builder.add_edge("数据库设计", "文档保存3")
    builder.add_edge("文档保存3", "初始化代码智能体输入")
    builder.add_edge("初始化代码智能体输入", "用户输入1")
    builder.add_conditional_edges("用户输入1", routing_function, {True: "代码编写", False: END})
    builder.add_conditional_edges("代码编写", routing_function, {True: "代码编写", False: "代码检查"})
    builder.add_conditional_edges("代码检查", routing_function, {True: "代码检查", False: "用户输入1"})

    # 编译完整图
    graph_full = builder.compile(checkpointer=memory_full)

    # 构建简单图
    simple_graph = StateGraph(AgentState)
    simple_graph.add_node("用户输入", User_Input_Node)
    simple_graph.add_node("代码编写", Coder_Agent)
    simple_graph.add_node("智能助手", Intelligent_Assistant_Agent)

    simple_graph.add_edge(START, "用户输入")
    simple_graph.add_conditional_edges("用户输入", routing_function, {True: "智能助手", False: END})
    simple_graph.add_conditional_edges("智能助手", routing_function, {True: "智能助手", False: "用户输入"})

    # 编译简单图
    graph_simple = simple_graph.compile(checkpointer=memory_simple)

    return graph_full, graph_simple