import os
from langchain_community.chat_models import ChatZhipuAI
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
os.environ["ZhipuAI_API_KEY"] = "<api_key>"#智谱
os.environ["DEEPSEEK_API_KEY"]="<api_key>"#deepseek
os.environ["DASHSCOPE_API_KEY"]="<api_key>"#通义
os.environ["GOOGLE_API_KEY"] = "<api_key>"#谷歌
os.environ["DOUBAO_API_KEY"] = "<api_key>"#豆包api_key
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"#替换成你的openai_key
zhi_pu_model = ChatZhipuAI(
    model="glm-4-flash-250414",#'glm-z1-flash',"glm-4-flash-250414"
    temperature=2,

)
gpt_model=ChatOpenAI(
    model="gpt-4o",
    temperature=1.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,

)
ollam_model = ChatOllama(
    model="qwen3:4b-fp16",
    temperature=2,

)
qwen_model = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus-1125",
    # other params...
)
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=2,

    max_retries=2,
    # other params...
)
deepseek_model=ChatDeepSeek(model="deepseek-chat",#deepseek-response
                            temperature=1.5)
doubao_model=ChatOpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    model="doubao-seed-1-6-flash-250615",
    # other params...
)



default_model=ollam_model#在这里切换模型类，可以替换成zhi_pu_model，qwen_model,gemini_model,deepseek_model等