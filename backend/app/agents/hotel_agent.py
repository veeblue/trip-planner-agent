from langchain.agents import create_agent

from backend.app.llms import llm_qwen
from backend.app.tools.amap_tools import amap_tools

HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你的任务是根据城市和景点位置推荐合适的酒店。

**重要提示:**
你必须使用工具来搜索酒店!不要自己编造酒店信息!

**工具调用格式:**
使用maps_text_search工具搜索酒店时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=酒店,city=城市名]`

**示例:**
用户: "搜索北京的酒店"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=酒店,city=北京]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 关键词使用"酒店"或"宾馆"
"""
import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

async def hotel_agent():
    agent = create_agent(
        model=llm_qwen,
        tools=await amap_tools(),
        system_prompt=HOTEL_AGENT_PROMPT,
    )
    # response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "请帮我推荐一些北京的酒店。"}]}
    # )
    # print(response["messages"][-1].content)
    return agent