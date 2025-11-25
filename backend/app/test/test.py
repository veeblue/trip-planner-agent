from datetime import datetime
import json
import asyncio
from langchain.agents import create_agent

from backend.app.agents.multi_agent_trip_planner import MultiAgentTripPlanner
from backend.app.llms import llm_qwen
from backend.app.models.schemas import TripPlan
from backend.app.tools.amap_tools import amap_tools

multi_agent = MultiAgentTripPlanner


async def get_trip_plan(request) -> TripPlan:
    planner = multi_agent()
    trip_plan = await planner.plan_trip(request)
    return trip_plan


async def main():
    from backend.app.models.schemas import TripRequest

    trip_request = TripRequest(
        city='武汉',
        start_date="2025-06-01",
        end_date="2025-06-07",
        travel_days=7,
        preferences=["历史文化", "美食"],
        transportation='飞机',  # 添加这个
        accommodation='酒店'  # 添加这个
    )
    trip_plan = await get_trip_plan(trip_request)
    print(json.dumps(trip_plan.model_dump(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
