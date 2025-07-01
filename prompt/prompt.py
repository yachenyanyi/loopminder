
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)

def load_prompt_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()  # .strip() 移除首尾空白字符

loop_agnet=load_prompt_from_file('prompt/text/agent_loop.txt')
file_assistant_prompt=  SystemMessage(content=load_prompt_from_file('prompt/text/file_assistant_prompt.txt'))
Project_Analyst_prompt=  SystemMessage(content=load_prompt_from_file('prompt/text/Project Analyst.txt'))#软件需求分析
Project_Manager_prompt=  SystemMessage(content=load_prompt_from_file('prompt/text/Project Manager.txt'))#开发计划
System_Architect_prompt=  SystemMessage(content=load_prompt_from_file('prompt/text/System Architect.txt'))#系统架构
Database_Design_prompt= SystemMessage(content=load_prompt_from_file('prompt/text/Database Design.txt'))#数据库设计
Task_Extraction_prompt= SystemMessage(content=load_prompt_from_file('prompt/text/Database Design.txt'))
Coder_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/Coder.txt'))
File_Saver_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/File_Save.txt'))
Loop_coder_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/Loop_coder.txt'))
dir_creater_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/Create_dir.txt'))
code_review_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/Code_Review.txt'))
Intelligent_Assistant_prompt=SystemMessage(content=load_prompt_from_file('prompt/text/Intelligent_Assistant.txt'))