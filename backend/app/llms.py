from langchain_openai import ChatOpenAI
import os

from backend.app.config import get_settings

llm_qwen = ChatOpenAI(
    model=get_settings().llm_model_name,
    api_key=get_settings().llm_api_key,
    base_url=get_settings().llm_base_url
)

llm_deepseek = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    )