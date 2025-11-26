import asyncio
import json
from typing import List, Union, Dict, Any, Optional

from backend.app.models.schemas import POIInfo, Location, WeatherInfo
from backend.app.tools.amap_tools import amap_tools


class AmapService:

    async def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        搜索POI

        Args:
            keywords: 搜索关键词
            city: 城市
            citylimit: 是否限制在城市范围内

        Returns:
            POI信息列表
        """
        try:
            # 1. 获取工具并调用
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_text_search"), None)

            if not tool:
                print("❌ 未找到 maps_text_search 工具")
                return []

            payload = {"keywords": keywords, "city": city, "citylimit": str(citylimit).lower()}
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📄 POI搜索结果: {response[:200] if isinstance(response, str) else response}...")

            # 2. 解析 JSON 字符串
            data = json.loads(response) if isinstance(response, str) else response

            # 3. 提取 pois 数组
            pois = data.get("pois", []) if isinstance(data, dict) else data

            # 4. 转换为 POIInfo 对象列表
            poi_list = []
            for poi_data in pois:
                try:
                    poi_list.append(POIInfo(
                        id=poi_data.get("id", ""),
                        name=poi_data.get("name", ""),
                        type=poi_data.get("type", ""),
                        address=poi_data.get("address", ""),
                        location=Location(
                            longitude=float(poi_data.get("location", "0,0").split(",")[0]),
                            latitude=float(poi_data.get("location", "0,0").split(",")[1])
                        ),
                        tel=poi_data.get("tel") or None
                    ))
                except Exception as e:
                    print(f"⚠️  解析单个 POI 失败: {e}")
                    continue

            print(f"✅ 成功解析 {len(poi_list)} 个 POI")
            return poi_list

        except Exception as e:
            print(f"❌ POI搜索失败: {str(e)}")
            return []

    async def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气

        Args:
            city: 城市名称

        Returns:
            天气信息字符串
        """
        try:
            # 1. 获取工具
            tools = await amap_tools()
            tool = next(
                (t for t in tools if getattr(t, "name", None) == "maps_weather"),
                None
            )

            if not tool:
                raise RuntimeError("未找到 maps_weather 工具")

            # 2. 调用工具
            payload = {"city": city}
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)
            # print(f"📄 天气查询结果: {response}")
            return parse_weather_response(response)
        except Exception as e:
            print(f"❌ 天气查询失败: {str(e)}")
            return f"天气查询失败: {str(e)}"

    async def plan_route(
            self,
            origin_address: str,
            destination_address: str,
            origin_city: Optional[str] = None,
            destination_city: Optional[str] = None,
            route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线

        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit/bicycling)

        Returns:
            路线信息
        """
        try:
            tools = await amap_tools()

            # 1. 先进行地理编码，将地址转换为坐标
            geocode_tool = next((t for t in tools if getattr(t, "name", None) == "maps_geo"), None)
            if not geocode_tool:
                return {"error": "未找到地理编码工具"}

            # 获取起点坐标
            origin_payload = {"address": origin_address}
            if origin_city:
                origin_payload["city"] = origin_city
            origin_response = await geocode_tool.ainvoke(origin_payload) if hasattr(geocode_tool,
                                                                                    "ainvoke") else geocode_tool.invoke(
                origin_payload)

            print(f"📍 起点地理编码结果: {origin_response[:200]}...")
            origin_data = json.loads(origin_response) if isinstance(origin_response, str) else origin_response

            # 关键修复：使用 results 而不是 geocodes
            origin_results = origin_data.get("results", [])
            if not origin_results:
                return {"error": f"无法找到起点 '{origin_address}' 的坐标"}

            origin_location = origin_results[0].get("location", "")
            print(f"🗺️  起点坐标: {origin_location}")

            if not origin_location:
                return {"error": f"无法找到起点 '{origin_address}' 的坐标"}

            # 获取终点坐标
            dest_payload = {"address": destination_address}
            if destination_city:
                dest_payload["city"] = destination_city
            dest_response = await geocode_tool.ainvoke(dest_payload) if hasattr(geocode_tool,
                                                                                "ainvoke") else geocode_tool.invoke(
                dest_payload)

            print(f"📍 终点地理编码结果: {dest_response[:200]}...")
            dest_data = json.loads(dest_response) if isinstance(dest_response, str) else dest_response

            # 关键修复：使用 results 而不是 geocodes
            dest_results = dest_data.get("results", [])
            if not dest_results:
                return {"error": f"无法找到终点 '{destination_address}' 的坐标"}

            dest_location = dest_results[0].get("location", "")
            print(f"🗺️  终点坐标: {dest_location}")

            if not dest_location:
                return {"error": f"无法找到终点 '{destination_address}' 的坐标"}

            print(f"✅ 起点: {origin_location}, 终点: {dest_location}")

            # 2. 根据路线类型选择工具并调用
            tool_map = {
                "walking": "maps_direction_walking",
                "driving": "maps_direction_driving",
                "transit": "maps_direction_transit_integrated",
                "bicycling": "maps_direction_bicycling",
            }
            tool_name = tool_map.get(route_type, "maps_direction_walking")

            route_tool = next((t for t in tools if getattr(t, "name", None) == tool_name), None)
            if not route_tool:
                return {"error": f"未找到路线规划工具: {tool_name}"}

            # 调用路线规划工具
            route_payload = {
                "origin": origin_location,
                "destination": dest_location
            }

            route_response = await route_tool.ainvoke(route_payload) if hasattr(route_tool,
                                                                                "ainvoke") else route_tool.invoke(
                route_payload)

            print(f"📍 路线规划结果: {route_response[:200] if isinstance(route_response, str) else route_response}...")

            # 3. 解析响应
            route_data = json.loads(route_response) if isinstance(route_response, str) else route_response

            return {
                "success": True,
                "route_type": route_type,
                "origin": {
                    "address": origin_address,
                    "location": origin_location
                },
                "destination": {
                    "address": destination_address,
                    "location": dest_location
                },
                "route_data": route_data
            }

        except Exception as e:
            print(f"❌ 路线规划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码(地址转坐标)

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_geo"), None)

            if not tool:
                print("❌ 未找到 maps_geo 工具")
                return None

            # 构建请求参数
            payload = {"address": address}
            if city:
                payload["city"] = city

            # 调用工具
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📍 地理编码结果: {response[:200] if isinstance(response, str) else response}...")

            # 解析响应
            data = json.loads(response) if isinstance(response, str) else response

            # 提取坐标
            geocodes = data.get("results", [])
            if not geocodes:
                print(f"⚠️  未找到地址 '{address}' 的坐标")
                return None

            location_str = geocodes[0].get("location", "")
            if not location_str:
                return None

            # 解析坐标字符串 "经度,纬度"
            lon, lat = location_str.split(",")
            return Location(longitude=float(lon), latitude=float(lat))

        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None

    async def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        获取POI详情

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_search_detail"), None)

            if not tool:
                print("❌ 未找到 maps_search_detail 工具")
                return {"error": "工具不可用"}

            # 调用工具
            payload = {"id": poi_id}
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📄 POI详情: {response[:200] if isinstance(response, str) else response}...")

            # 解析响应
            data = json.loads(response) if isinstance(response, str) else response

            # 提取POI详情
            pois = data.get("pois", [])
            if not pois:
                return {"error": "未找到POI详情"}

            poi_detail = pois[0]

            # 返回结构化数据
            return {
                "id": poi_detail.get("id", ""),
                "name": poi_detail.get("name", ""),
                "type": poi_detail.get("type", ""),
                "address": poi_detail.get("address", ""),
                "location": poi_detail.get("location", ""),
                "tel": poi_detail.get("tel", ""),
                "website": poi_detail.get("website", ""),
                "photos": poi_detail.get("photos", []),
                "business_area": poi_detail.get("business_area", ""),
                "rating": poi_detail.get("rating", ""),
                "cost": poi_detail.get("cost", ""),
                "opentime": poi_detail.get("opentime", ""),
                "introduction": poi_detail.get("introduction", "")
            }

        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return {"error": str(e)}

    async def reverse_geocode(self, longitude: float, latitude: float) -> Optional[str]:
        """
        逆地理编码(坐标转地址)

        Args:
            longitude: 经度
            latitude: 纬度

        Returns:
            地址字符串
        """
        try:
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_regeocode"), None)

            if not tool:
                print("❌ 未找到 maps_regeocode 工具")
                return None

            # 调用工具
            payload = {"location": f"{longitude},{latitude}"}
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📍 逆地理编码结果: {response[:200] if isinstance(response, str) else response}...")

            # 解析响应
            data = json.loads(response) if isinstance(response, str) else response

            # 提取地址
            regeocode = data.get("regeocode", {})
            formatted_address = regeocode.get("formatted_address", "")

            return formatted_address if formatted_address else None

        except Exception as e:
            print(f"❌ 逆地理编码失败: {str(e)}")
            return None

    async def search_nearby(
            self,
            longitude: float,
            latitude: float,
            keywords: str,
            radius: int = 1000
    ) -> List[POIInfo]:
        """
        周边搜索

        Args:
            longitude: 经度
            latitude: 纬度
            keywords: 搜索关键词
            radius: 搜索半径（米）

        Returns:
            POI信息列表
        """
        try:
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_around_search"), None)

            if not tool:
                print("❌ 未找到 maps_around_search 工具")
                return []

            # 调用工具
            payload = {
                "location": f"{longitude},{latitude}",
                "keywords": keywords,
                "radius": str(radius)
            }
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📍 周边搜索结果: {response[:200] if isinstance(response, str) else response}...")

            # 解析响应
            data = json.loads(response) if isinstance(response, str) else response
            pois = data.get("pois", [])

            # 转换为 POIInfo 对象列表
            poi_list = []
            for poi_data in pois:
                try:
                    poi_list.append(POIInfo(
                        id=poi_data.get("id", ""),
                        name=poi_data.get("name", ""),
                        type=poi_data.get("type", ""),
                        address=poi_data.get("address", ""),
                        location=Location(
                            longitude=float(poi_data.get("location", "0,0").split(",")[0]),
                            latitude=float(poi_data.get("location", "0,0").split(",")[1])
                        ),
                        tel=poi_data.get("tel") or None,
                        distance=poi_data.get("distance") or None
                    ))
                except Exception as e:
                    print(f"⚠️  解析单个 POI 失败: {e}")
                    continue

            print(f"✅ 成功解析 {len(poi_list)} 个周边 POI")
            return poi_list

        except Exception as e:
            print(f"❌ 周边搜索失败: {str(e)}")
            return []

    async def calculate_distance(
            self,
            origin: str,
            destination: str,
            distance_type: str = "0"
    ) -> Optional[Dict[str, Any]]:
        """
        计算距离

        Args:
            origin: 起点坐标 "经度,纬度"
            destination: 终点坐标 "经度,纬度"
            distance_type: 距离类型 (0=直线距离, 1=驾车距离)

        Returns:
            距离信息
        """
        try:
            tools = await amap_tools()
            tool = next((t for t in tools if getattr(t, "name", None) == "maps_distance"), None)

            if not tool:
                print("❌ 未找到 maps_distance 工具")
                return None

            # 调用工具
            payload = {
                "origins": origin,
                "destination": destination,
                "type": distance_type
            }
            response = await tool.ainvoke(payload) if hasattr(tool, "ainvoke") else tool.invoke(payload)

            print(f"📏 距离计算结果: {response[:200] if isinstance(response, str) else response}...")

            # 解析响应
            data = json.loads(response) if isinstance(response, str) else response

            results = data.get("results", [])
            if results:
                return results[0]

            return None

        except Exception as e:
            print(f"❌ 距离计算失败: {str(e)}")
            return None

def parse_weather_response(response: Union[str, dict, list]) -> List[WeatherInfo]:
    """
    解析天气工具返回的数据

    Args:
        response: 可能是 JSON 字符串、字典或列表

    Returns:
        天气信息列表
    """
    # 1. 如果是字符串，先解析为对象
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {e}")

    # 2. 提取 forecasts 数据
    if isinstance(response, dict):
        forecasts = response.get("forecasts", [response])
    elif isinstance(response, list):
        forecasts = response
    else:
        raise ValueError(f"不支持的响应格式: {type(response)}")

    # 3. 转换为 WeatherInfo 对象列表
    weather_list = []
    for item in forecasts:
        try:
            weather_list.append(WeatherInfo(
                date=item.get("date", ""),
                day_weather=item.get("dayweather", ""),
                night_weather=item.get("nightweather", ""),
                day_temp=item.get("daytemp", "0"),
                night_temp=item.get("nighttemp", "0"),
                wind_direction=item.get("daywind", ""),
                wind_power=item.get("daypower", "")
            ))
        except Exception as e:
            print(f"⚠️  解析天气数据失败: {e}")
            continue

    return weather_list
# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service