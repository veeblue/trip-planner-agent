import os

from backend.app.config import get_settings
from backend.app.utils.mcp import create_mcp_streamable_http_client

async def amap_tools():
    """Create Amap MCP tool client."""
    key = get_settings().amap_api_key
    try:
        if not key:
            raise ValueError("错误: 未设置 AMAP_API_KEY 环境变量。")
    except Exception as e:
        raise ValueError(f"错误: 检查 AMAP_API_KEY 环境变量时发生异常: {e}")
    url = f"https://mcp.amap.com/mcp?key={key}"
    tools = await create_mcp_streamable_http_client("amap", url)
    return tools