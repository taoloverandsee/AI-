# 这是一个示例 Python 脚本。
from openai.types import model

AGENT_SYSTEM_PROMPT = ""
import os
from idlelib import query
from zoneinfo import available_timezones

# 按 Ctrl+F5 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import requests
from openai import responses, api_key
from openai.types.beta.threads import message
from tavily import tavily, TavilyClient


#查询天气方法
def get_weather(city:str)->str:
    url= f"https://wttr.in/{city}?format=j1"
    try:
        response=requests.get(url)
        response.raise_for_status()
        data=response.json()
        current_conditon=data['current_condition'][0]
        weather_desc=current_conditon['weatherDesc'][0]['value']
        temp_c=current_conditon['temp_C']
        return f"{city}当前天气{weather_desc},气温{temp_c}摄氏度"
    except requests.exceptions.RequestException as err:
        return f"查询时候遇到网络问题{err}"
    except (KeyError, IndexError) as err:
        return f"天气数据解析失败,没有这个城市-{err}"




#查询并推荐旅游景点
def get_attraction(city:str,weather:str)->str:
    api_key=os.environ.get('TAVTILY_API_KEY')
    if not api_key:
        return \
            "没有配置环境变量"
    #初始化客户端
    tavily=TavilyClient(api_key=api_key)
    query=f"'{city}'在'{weather}'天气下最值得去的旅游景点以及推荐理由"
    try:
        response=tavily.search(query=query,search_depth="basic",include_usage=True)
        if response.get('answer'):
            return response['answer']
        #没有综合性回答就格式化原始结果
        formatted_results=[]
        for result in response.get('results',[]):
            formatted_results.append(f"-{result['title']}:{result['content']}")
        if not  formatted_results:
            return "没有找到相关景点推荐"
        return '根据结果找到了一下信息'+'\n'.join(formatted_results)
    except Exception as err:
        return  f"错误:执行Tavily搜索时候出现问题-{err}"







#将工具函数放入字典
available_tools={
    "get_weather":get_weather,
    "get_attraction":get_attraction
}

from  openai import OpenAI
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


import re

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

# response = client.chat.completions.create(
#     model=MODEL_ID,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False,
#     reasoning_effort="high",
#     extra_body={"thinking": {"type": "enabled"}}
#)

# llm = OpenAICompatibleClient(
#     model=MODEL_ID,
#     api_key=API_KEY,
#     base_url=BASE_URL
# )

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天南宁的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "=" * 40)

# --- 3. 运行主循环 ---
for i in range(5):  # 设置最大循环次数
    print(f"--- 循环 {i + 1} ---\n")

    # 3.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)

    # 3.2. 调用LLM进行思考
    llm_output = deepseek.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"任务完成，最终答案: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误：未定义的工具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "=" * 40)
    prompt_history.append(observation_str)


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
