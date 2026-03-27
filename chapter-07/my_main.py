from dotenv import load_dotenv
from my_llm import MyLLM
import os

# 加载环境变量
load_dotenv()

# 实例化我们重写的客户端，并指定provider
llm = MyLLM(provider="modelscope", 
            base_url=os.getenv("LLM_BASE_URL"), 
            model=os.getenv("LLM_MODEL_ID"),
            api_key=os.getenv("LLM_API_KEY"))

# 准备消息
messages = [{"role": "user", "content": "你好，请介绍一下自己"}]

# 发起调用，think等方法都已从父类继承，无需重写
response_stream = llm.think(messages)


print("ModelScope Response:")
for chunk in response_stream:
    # chunk 已经是文本片段，可以直接使用
    print(chunk, end="", flush=True)