WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**重要提示:**
你必须使用工具来查询天气!不要自己编造天气信息!

**工具调用格式:**
使用maps_weather工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_weather:city=城市名]`

**示例:**
用户: "查询北京天气"
你的回复: [TOOL_CALL:amap_maps_weather:city=北京]

用户: "上海的天气怎么样"
你的回复: [TOOL_CALL:amap_maps_weather:city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
"""

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"
from langchain.agents import create_agent

from backend.app.llms import llm_qwen
from backend.app.tools.amap_tools import amap_tools
async def weather_agent()-> create_agent:


    agent = create_agent(
        model=llm_qwen,
        tools=await amap_tools(),
        system_prompt=WEATHER_AGENT_PROMPT,
    )
    # response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "请告诉我北京的天气怎么样？"}]}
    # )
    # print(response["messages"][-1].content)
    return agent