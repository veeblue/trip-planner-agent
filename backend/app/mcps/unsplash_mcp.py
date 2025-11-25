from fastmcp import FastMCP

from backend.app.services.unsplash_service import  get_unsplash_service
import os
mcp = FastMCP("Unsplash Search Tool")

@mcp.tool("get_unsplash_pic_url")
def get_unsplash_pic_url(query: str) -> str:
    """使用 Unsplash API 获取与查询相关的图片 URL"""

    service = get_unsplash_service()

    pic_url = service.get_picture_url(query=query)

    return pic_url if pic_url else "未找到相关图片。"

if __name__ == "__main__":
    mcp.run(transport="stdio")