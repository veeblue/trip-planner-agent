import json

from langchain_core.messages import HumanMessage

from backend.app.agents.attraction_agent import attraction_agent
from backend.app.agents.hotel_agent import hotel_agent
from backend.app.agents.planner_agent import planner_agent
from backend.app.agents.weather_agent import weather_agent
from backend.app.llms import llm_qwen
from backend.app.models.schemas import TripRequest, TripPlan, Meal, Location, Attraction, DayPlan


class MultiAgentTripPlanner:
    def __init__(self):
        """Initialize the multi-agent trip planner."""
        print("🔄 开始初始化多智能体旅行规划系统...")

        try:
            self.llm = llm_qwen
            self.attraction_agent = None
            self.hotel_agent = None
            self.weather_agent = None
            self.planner_agent = None

            print(f"✅ 多智能体系统初始化成功")

        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def initialize(self):
        """异步初始化各个Agent"""
        print("🔄 异步初始化各个智能体...")
        self.attraction_agent = await attraction_agent()
        self.hotel_agent = await hotel_agent()
        self.weather_agent = await weather_agent()
        self.planner_agent = await planner_agent()
        print("✅ 各个智能体初始化完成")

    async def plan_trip(self, request: TripRequest):

        """
       使用多智能体协作生成旅行计划

       Args:
           request: 旅行请求

       Returns:
           旅行计划
       """
        try:
            try:
                await self.initialize()
            except Exception as e:
                print(f"⚠️  智能体初始化失败: {str(e)}")
                return self._create_fallback_plan(request)

            if not all([self.attraction_agent, self.weather_agent, self.hotel_agent, self.planner_agent]):
                print("⚠️  有智能体未成功初始化,使用备用方案生成计划")
                return self._create_fallback_plan(request)

            print(f"\n{'=' * 60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'=' * 60}\n")

            # 步骤1: 景点搜索Agent搜索景点
            print("📍 步骤1: 搜索景点...")
            attraction_query = self._build_attraction_query(request)
            attractions = ""
            try:
                attraction_response = await self.attraction_agent.ainvoke(
                    {"messages": [HumanMessage(content=attraction_query)]}
                )
                attractions = attraction_response["messages"][-1].content
            except Exception as e:
                print(f"⚠️  景点搜索失败: {e}, 跳过使用空景点信息")
            print(f"✅ 景点搜索完成:\n{attractions}\n")

            # 步骤2: 天气查询Agent查询天气
            print("☁️ 步骤2: 查询天气...")
            weather_query = f"请查询{request.city}的天气信息"
            weather_info = ""
            try:
                weather_response = await self.weather_agent.ainvoke(
                    {"messages": [HumanMessage(content=weather_query)]}
                )
                weather_info = weather_response["messages"][-1].content
            except Exception as e:
                print(f"⚠️  天气查询失败: {e}, 跳过使用空天气信息")
            print(f"✅ 天气查询完成:\n{weather_info}\n")

            # 步骤3: 酒店推荐Agent推荐酒店
            print("🏨 步骤3: 推荐酒店...")
            hotel_query = f"请搜索{request.city}的{request.accommodation}酒店"
            hotels = ""
            try:
                hotel_response = await self.hotel_agent.ainvoke(
                    {"messages": [HumanMessage(content=hotel_query)]}
                )
                hotels = hotel_response["messages"][-1].content
            except Exception as e:
                print(f"⚠️  酒店推荐失败: {e}, 跳过使用空酒店信息")
            print(f"✅ 酒店推荐完成:\n{hotels}\n")

            # 步骤4: 行程规划Agent生成旅行计划
            print("🗺️ 步骤4: 生成旅行计划...")
            planner_query = self._build_planner_query(request, attractions, weather_info, hotels)
            plan_response = ""
            try:
                planner_response = await self.planner_agent.ainvoke(
                    {"messages": [HumanMessage(content=planner_query)]}
                )
                plan_response = planner_response["messages"][-1].content
            except Exception as e:
                print(f"⚠️  行程规划Agent失败: {e}, 使用备用方案")
                return self._create_fallback_plan(request)
            print(f"✅ 行程规划完成:\n{plan_response}\n")

            # 解析响应为TripPlan对象
            trip_plan = self._parse_response(plan_response, request)
            print(f"🎉 多智能体协作规划完成!")
            return trip_plan
        except Exception as e:
            print(f"❌ 多智能体协作失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _build_attraction_query(self, request: TripRequest) -> str:
        """构建景点搜索查询 - 直接包含工具调用"""
        keywords = []
        if request.preferences:
            # 只取第一个偏好作为关键词
            keywords = request.preferences[0]
        else:
            keywords = "景点"

        # 直接返回工具调用格式
        query = f"请使用amap_maps_text_search工具搜索{request.city}的{keywords}相关景点。\n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """构建行程规划查询"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

            **基本信息:**
            - 城市: {request.city}
            - 日期: {request.start_date} 至 {request.end_date}
            - 天数: {request.travel_days}天
            - 交通方式: {request.transportation}
            - 住宿: {request.accommodation}
            - 偏好: {', '.join(request.preferences) if request.preferences else '无'}
        
            **景点信息:**
            {attractions}
        
            **天气信息:**
            {weather}
        
            **酒店信息:**
            {hotels}
        
            **要求:**
            1. 每天安排2-3个景点
            2. 每天必须包含早中晚三餐
            3. 每天推荐一个具体的酒店(从酒店信息中选择)
            3. 考虑景点之间的距离和交通方式
            4. 返回完整的JSON格式数据
            5. 景点的经纬度坐标要真实准确
            """
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        return query

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        解析Agent响应

        Args:
            response: Agent响应文本
            request: 原始请求

        Returns:
            旅行计划
        """
        try:
            # 尝试从响应中提取JSON
            # 查找JSON代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # 直接查找JSON对象
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")

            # 解析JSON
            data = json.loads(json_str)

            # 转换为TripPlan对象
            trip_plan = TripPlan(**data)

            return trip_plan

        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            print(f"   将使用备用方案生成计划")
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta

        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        # 创建每日行程
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i + 1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j + 1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i * 0.01 + j * 0.005,
                                          latitude=39.9 + i * 0.01 + j * 0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i + 1}天早餐", description="当地特色早餐"),
                    Meal(type="lunch", name=f"第{i + 1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i + 1}天晚餐", description="晚餐推荐")
                ]
            )
            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。"
        )

# 全局多智能体系统实例
_multi_agent_planner = None

def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner
