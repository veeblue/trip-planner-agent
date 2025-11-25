"""地图服务API路由"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.app.tools.amap_tools import amap_tools

router = APIRouter(prefix="/map", tags=["地图服务"])

@router.get(
    "/poi",
    summary="根据关键词搜索兴趣点(POI)",
    description="根据关键词搜索兴趣点(POI)，返回相关的兴趣点列表。",
)
async def search_poi(
    keywords: str = Query(..., description="搜索关键词", example="故宫"),
    city: str = Query(..., description="城市", example="北京"),
    citylimit: bool = Query(True, description="是否限制在城市范围内")
):
    """
    搜索POI

    Args:
        keywords: 搜索关键词
        city: 城市
        citylimit: 是否限制在城市范围内

    Returns:
        POI搜索结果
    """
    try:
        tools = await amap_tools()
        for tool in tools:
            if getattr(tool, "name", None) == "maps_text_search":
                payload = {"keywords": keywords, "city": city, "citylimit": citylimit}
                if hasattr(tool, "ainvoke"):
                    response = await tool.ainvoke(payload)
                else:
                    response = tool.invoke(payload)
                return response
        raise RuntimeError("未找到maps_text_search工具")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POI搜索失败: {e}")
