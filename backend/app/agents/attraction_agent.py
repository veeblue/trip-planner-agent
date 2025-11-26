from langchain.agents import create_agent

from backend.app.llms import llm_qwen
from backend.app.tools.amap_tools import amap_tools
from backend.app.tools.unsplash_tools import unsplash_tools

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**重要提示:**
你必须使用工具来搜索景点!不要自己编造景点信息!

**工具调用格式:**
使用maps_text_search工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]`
`[TOOL_CALL:get_picture_url:query=城市名]`

**示例:**
用户: "搜索北京的历史文化景点"
你的回复: 
- [TOOL_CALL:amap_maps_text_search:keywords=历史文化,city=北京]
- [TOOL_CALL:get_picture_url:query=北京]
用户: "搜索上海的公园"
你的回复: 
- [TOOL_CALL:amap_maps_text_search:keywords=公园,city=上海]
- [TOOL_CALL:get_picture_url:query=上海]
**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 参数用逗号分隔
"""
import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

async def attraction_agent():
    tools = await amap_tools() + await unsplash_tools()

    agent = create_agent(
        model=llm_qwen,
        tools=tools,
        system_prompt=ATTRACTION_AGENT_PROMPT,
    )
    # response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "请帮我制定一个去巴黎的10天旅行计划。"}]}
    # )
    # print(response["messages"][-1].content)
    return agent

# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(plan_trip())

