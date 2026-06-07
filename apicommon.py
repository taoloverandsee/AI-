import re
import os
class OpenAICompatibleClient:
    def __init__(self,model:str,api_key:str,base_url:str ):

        self.model=model
        self.client=OpenAI(api_key=api_key,base_url=base_url)

    def generate(self,prompt:str,system_prompt:str)->str:
        print('正在调用大语言模型')
        try:
            messages=[
                {'role':'system','content':system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response =self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer= response.choices[0].message.content
            print('大模型响应成功')
            return answer
        except Exception as err:
            print(f"调用llm API时候发生错误:{err}")
            return "错误:调用语言模型服务的时候出错"
from tavily import tavily, TavilyClient
# --- 1. 配置LLM客户端 ---
# 请根据您使用的服务，将这里替换成对应的凭证和地址
API_KEY = "sk-5076ff5031924307ab732d5ebf30c673"
BASE_URL = "https://api.deepseek.com"
MODEL_ID = "deepseek-v4-pro"
TAVILY_API_KEY="YOUR_Tavily_KEY"
os.environ['TAVILY_API_KEY'] = "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"


import os
from openai import OpenAI

deepseek = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL,

   )