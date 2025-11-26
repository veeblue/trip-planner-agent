from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import get_settings, validate_config, print_config, settings
from backend.app.api.routers import map as map_routers, poi, trip


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 60)
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print("=" * 60)

    print_config()

    try:
        validate_config()
        print("\n✅ 配置验证通过")
    except ValueError as e:
        print(f"\n❌ 配置验证失败:\n{e}")
        print("\n请检查.env文件并确保所有必要的配置项都已设置")
        raise

    print("\n" + "=" * 60)
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("=" * 60 + "\n")

    try:
        yield
    finally:
        print("\n" + "=" * 60)
        print("👋 应用正在关闭...")
        print("=" * 60 + "\n")


app = FastAPI(
    title="基于LangChain的智能旅行规划助手API",
    description="基于LangChain的智能旅行规划助手API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(map_routers.router, prefix="/api")
app.include_router(poi.router, prefix="/api")
app.include_router(trip.router, prefix="/api")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=True)