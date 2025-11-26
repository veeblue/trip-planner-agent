"""地图服务API路由"""
import json

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Union, List, Dict, Any

from backend.app.models.schemas import WeatherResponse, RouteResponse, RouteRequest, POISearchResponse, RouteInfo
from backend.app.services.amap_service import get_amap_service
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
        # 获取服务实例
        service = get_amap_service()

        # 搜索POI
        pois = await service.search_poi(keywords, city, citylimit)

        return POISearchResponse(
            success=True,
            message="POI搜索成功",
            data=pois
        )

    except Exception as e:
        print(f"❌ POI搜索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI搜索失败: {str(e)}"
        )

@router.get("/weather",
            response_model=WeatherResponse,
            summary="查询天气",
            description="查询指定城市的天气信息"
            )
async def get_weather(
        city: str = Query(..., description="城市名称", example="北京")
):
     """
    查询天气

    Args:
        city: 城市名称

    Returns:
        天气信息
    """
     try:
        service = get_amap_service()
        forecasts = await service.get_weather(city)
        return WeatherResponse(
             success=True,
             message="天气查询成功",
             data=forecasts
        )
     except Exception as e:
         raise HTTPException(status_code=500, detail=f"天气查询失败: {e}")




def _extract_distance_duration(data: Any) -> tuple:
    def _coerce_float(x):
        try:
            return float(x)
        except Exception:
            return None
    def _coerce_int(x):
        try:
            return int(float(x))
        except Exception:
            return None
    dist = None
    dur = None
    if isinstance(data, dict):
        for k, v in data.items():
            if dist is None and k == "distance":
                dist = _coerce_float(v)
            elif dur is None and k == "duration":
                dur = _coerce_int(v)
            if (dist is None or dur is None):
                d2, d3 = _extract_distance_duration(v)
                dist = dist if dist is not None else d2
                dur = dur if dur is not None else d3
    elif isinstance(data, list):
        for item in data:
            if dist is not None and dur is not None:
                break
            d2, d3 = _extract_distance_duration(item)
            dist = dist if dist is not None else d2
            dur = dur if dur is not None else d3
    return dist, dur

@router.post(
    "/route",
    response_model=RouteResponse,
    summary="规划路线",
    description="规划两点之间的路线"
)
async def plan_route(request: RouteRequest):
    """
       规划路线

       Args:
           request: 路线规划请求

       Returns:
           路线信息
       """
    try:
        seevice = get_amap_service()
        response = await seevice.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )
        # 检查是否有错误
        if "error" in response:
            raise HTTPException(
                status_code=400,
                detail=response["error"]
            )

        # 检查是否成功
        if not response.get("success"):
            raise HTTPException(
                status_code=500,
                detail="路线规划失败"
            )

        dist, dur = _extract_distance_duration(response.get("route_data"))
        info = RouteInfo(
            distance=float(dist or 0.0),
            duration=int(dur or 0),
            route_type=request.route_type,
            description=f"{request.origin_address} -> {request.destination_address}"
        )
        return RouteResponse(success=True, message="路线规划成功", data=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路线规划失败: {e}")


@router.get(
    "/health",
    summary="健康检查",
    description="检查地图服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查服务是否可用
        service = get_amap_service()

        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_tools_count": len(service.mcp_tool._available_tools)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
