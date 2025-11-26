from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.amap_service import get_amap_service
from backend.app.services.unsplash_service import get_unsplash_service

router = APIRouter(
    prefix="/poi",
    tags=["POI"]
)

class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None

@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取兴趣点的详细信息"
)
async def get_poi_detail(
    poi_id: str
) -> POIDetailResponse:
    """
    获取POI详情

    Args:
        poi_id: POI ID

    Returns:
        POI详情
    """
    try:
        amap_service = get_amap_service()
        poi_detail = await amap_service.get_poi_detail(poi_id)

        return POIDetailResponse(
            success=True,
            message="POI详情获取成功",
            data=poi_detail
        )

    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        return POIDetailResponse(
            success=False,
            message=f"获取POI详情失败: {str(e)}"
        )

@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词和城市搜索兴趣点(POI)"
)
async def search_poi(
    keywords: str,
    city: str,
    citylimit: bool = True
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
        amap_service = get_amap_service()
        pois = await amap_service.search_poi(keywords, city, citylimit)

        return {
            "success": True,
            "message": "POI搜索成功",
            "data": pois
        }

    except Exception as e:
        print(f"❌ POI搜索失败: {str(e)}")
        return {
            "success": False,
            "message": f"POI搜索失败: {str(e)}"
        }

@router.get(
    "/pic",
    summary="获取POI图片",
    description="根据POI名称获取相关图片URL"
)
async def get_attraction_picture(name: str):
    """
    获取POI图片

    Args:
        name: POI名称

    Returns:
        图片URL
    """
    try:
        unsplash_service = get_unsplash_service()
        pic_url = await unsplash_service.get_picture_url(name)

        return {
            "success": True,
            "message": "图片获取成功",
            "data": pic_url
        }

    except Exception as e:
        print(f"❌ 获取图片失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取图片失败: {str(e)}"
        }