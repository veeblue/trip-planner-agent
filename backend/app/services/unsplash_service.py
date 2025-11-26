#!/usr/bin/env python3
"""
Unsplash API Python 使用示例
完整的图片搜索、下载和使用指南
"""

import os
import requests
from typing import List, Dict, Optional
from urllib.parse import urlencode

from backend.app.config import get_settings


class UnsplashService:
    """Unsplash API 封装类"""

    BASE_URL = "https://api.unsplash.com"

    def __init__(self, access_key: str):
        """
        初始化 Unsplash API 客户端

        Args:
            access_key: Unsplash API Access Key
        """
        self.access_key = access_key
        self.headers = {
            "Authorization": f"Client-ID {access_key}"
        }

    async def search_photos(
            self,
            query: str,
            page: int = 1,
            per_page: int = 10,
            orientation: Optional[str] = "landscape",
            color: Optional[str] = None,
            order_by: str = "relevant"
    ) -> Dict:
        """
        搜索图片

        Args:
            query: 搜索关键词
            page: 页码（默认 1）
            per_page: 每页数量（默认 10，最大 30）
            orientation: 方向 (landscape, portrait, squarish)
            color: 颜色过滤 (black_and_white, black, white, yellow, orange, red, purple, magenta, green, teal, blue)
            order_by: 排序方式 (relevant, latest)

        Returns:
            搜索结果字典
        """
        url = f"{self.BASE_URL}/search/photos"

        params = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "order_by": order_by
        }

        if orientation:
            params["orientation"] = orientation
        if color:
            params["color"] = color

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    async def get_random_photo(
            self,
            query: Optional[str] = None,
            orientation: Optional[str] = None,
            count: int = 1
    ) -> Dict:
        """
        获取随机图片

        Args:
            query: 搜索关键词（可选）
            orientation: 方向（可选）
            count: 数量（1-30）

        Returns:
            随机图片数据
        """
        url = f"{self.BASE_URL}/photos/random"

        params = {"count": count}
        if query:
            params["query"] = query
        if orientation:
            params["orientation"] = orientation

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    async def get_photo(self, photo_id: str) -> Dict:
        """
        获取指定图片详情

        Args:
            photo_id: 图片 ID

        Returns:
            图片详情
        """
        url = f"{self.BASE_URL}/photos/{photo_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def track_download(self, download_location: str) -> None:
        """
        跟踪下载（API 要求）
        当用户下载或使用图片时必须调用此方法

        Args:
            download_location: 图片的 download_location URL
        """
        response = requests.get(download_location, headers=self.headers)
        response.raise_for_status()

    async def download_photo(self, photo_url: str, save_path: str) -> None:
        """
        下载图片到本地

        Args:
            photo_url: 图片 URL
            save_path: 保存路径
        """
        response = requests.get(photo_url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    async def get_attribution_text(self, photo: Dict) -> str:
        """
        生成版权归属文本（API 要求必须显示）

        Args:
            photo: 图片数据字典

        Returns:
            版权归属文本
        """
        photographer_name = photo['user']['name']
        photographer_link = photo['user']['links']['html']
        unsplash_link = "https://unsplash.com"

        return f"Photo by {photographer_name} ({photographer_link}) on Unsplash ({unsplash_link})"

    async def get_picture_url(self, query: str) -> Optional[str]:
        """
        根据关键词获取一张图片的常规尺寸 URL

        Args:
            query: 搜索关键词

        Returns:
            图片的常规尺寸 URL 或 None
        """
        results = await self.search_photos(query=query, per_page=1)
        if results['results']:
            return results['results'][0]['urls']['regular']
        return None

_unsplash_service = None
def get_unsplash_service() -> UnsplashService:
    """获取全局 UnsplashService 实例"""
    global _unsplash_service
    if _unsplash_service is None:
        access_key = get_settings().unsplash_access_key
        if not access_key:
            raise ValueError("请设置环境变量 UNSPLASH_ACCESS_KEY")
        _unsplash_service = UnsplashService(access_key=access_key)
    return _unsplash_service
# # ==================== 使用示例 ====================
#
# def example_search_photos():
#     """示例 1: 搜索图片"""
#     print("=== 示例 1: 搜索图片 ===\n")
#
#     # 初始化 API
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     # 搜索风景图片
#     results = api.search_photos(
#         query="beijing",
#         per_page=5,
#         orientation="landscape"
#     )
#
#     print(f"总共找到 {results['total']} 张图片\n")
#
#     for i, photo in enumerate(results['results'], 1):
#         print(f"图片 {i}:")
#         print(f"  ID: {photo['id']}")
#         print(f"  描述: {photo.get('description', '无描述')}")
#         print(f"  摄影师: {photo['user']['name']}")
#         print(f"  常规尺寸 URL: {photo['urls']['regular']}")
#         print(f"  下载链接: {photo['links']['download_location']}")
#         print(f"  版权信息: {api.get_attribution_text(photo)}")
#         print()
#
#
# def example_get_random_photos():
#     """示例 2: 获取随机图片"""
#     print("\n=== 示例 2: 获取随机图片 ===\n")
#
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     # 获取 3 张关于"猫"的随机图片
#     photos = api.get_random_photo(query="cat", count=3)
#
#     for i, photo in enumerate(photos, 1):
#         print(f"随机图片 {i}:")
#         print(f"  ID: {photo['id']}")
#         print(f"  摄影师: {photo['user']['name']}")
#         print(f"  URL: {photo['urls']['small']}")
#         print()
#
#
# def example_download_with_tracking():
#     """示例 3: 下载图片并正确跟踪"""
#     print("\n=== 示例 3: 下载图片（含跟踪）===\n")
#
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     # 搜索一张图片
#     results = api.search_photos(query="mountain", per_page=1)
#
#     if results['results']:
#         photo = results['results'][0]
#
#         # 重要：在下载前必须调用跟踪接口
#         print("跟踪下载...")
#         api.track_download(photo['links']['download_location'])
#
#         # 下载图片
#         print("下载图片...")
#         api.download_photo(
#             photo['urls']['regular'],
#             f"unsplash_{photo['id']}.jpg"
#         )
#
#         print(f"图片已保存为: unsplash_{photo['id']}.jpg")
#         print(f"版权信息: {api.get_attribution_text(photo)}")
#
#
# def example_get_photo_details():
#     """示例 4: 获取图片详情"""
#     print("\n=== 示例 4: 获取图片详情 ===\n")
#
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     # 使用特定的图片 ID
#     photo_id = "LBI7cgq3pbM"  # 示例 ID
#
#     try:
#         photo = api.get_photo(photo_id)
#
#         print(f"图片 ID: {photo['id']}")
#         print(f"创建时间: {photo['created_at']}")
#         print(f"尺寸: {photo['width']} x {photo['height']}")
#         print(f"点赞数: {photo['likes']}")
#         print(f"摄影师: {photo['user']['name']}")
#         print(f"摄影师主页: {photo['user']['links']['html']}")
#         print(f"\n可用尺寸:")
#         for size, url in photo['urls'].items():
#             print(f"  {size}: {url}")
#
#     except requests.exceptions.HTTPError as e:
#         print(f"错误: {e}")
#
#
# def example_advanced_search():
#     """示例 5: 高级搜索（带过滤条件）"""
#     print("\n=== 示例 5: 高级搜索 ===\n")
#
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     # 搜索蓝色调的竖版海洋图片
#     results = api.search_photos(
#         query="ocean",
#         orientation="portrait",
#         color="blue",
#         per_page=3
#     )
#
#     print(f"找到 {len(results['results'])} 张符合条件的图片:\n")
#
#     for photo in results['results']:
#         print(f"- {photo['user']['name']}: {photo['urls']['small']}")
#
#
# # ==================== 集成到应用示例 ====================
#
# def example_flask_integration():
#     """示例 6: Flask 应用集成示例"""
#     print("\n=== 示例 6: Flask 集成代码 ===\n")
#
#     code = '''
# from flask import Flask, render_template, request
# from unsplash_api import UnsplashService
#
# app = Flask(__name__)
# api = UnsplashService(access_key="YOUR_ACCESS_KEY")
#
# @app.route('/search')
# def search_images():
#     query = request.args.get('q', 'nature')
#     page = int(request.args.get('page', 1))
#
#     results = api.search_photos(query=query, page=page, per_page=20)
#
#     return render_template(
#         'gallery.html',
#         photos=results['results'],
#         total=results['total'],
#         page=page
#     )
#
# # 在模板中必须显示版权信息：
# # Photo by {{ photo.user.name }} on Unsplash
# # 并链接到摄影师主页和 Unsplash
# '''
#     print(code)
#
# def get_pic(query: str = "sunset"):
#     """示例 7: 获取图片 URL 的简单函数示例"""
#     print("\n=== 示例 7: 获取图片 URL 的简单函数示例 ===\n")
#
#     api = UnsplashService(access_key=os.getenv("UNSPLASH_ACCESS_KEY"))
#
#     pic_url = api.get_picture_url(query=query)
#
#     if pic_url:
#         print(f"关键词 '{query}' 的图片 URL: {pic_url}")
#     else:
#         print(f"未找到关键词 '{query}' 的图片。")
#
# def main():
#     """主函数：运行所有示例"""
#
#     # 检查是否设置了 API Key
#     if not os.getenv("UNSPLASH_ACCESS_KEY"):
#         print("❌ 错误: 请设置环境变量 UNSPLASH_ACCESS_KEY")
#         print("\n设置方法:")
#         print("  export UNSPLASH_ACCESS_KEY='your_access_key_here'")
#         return
#
#     try:
#         # 运行各个示例
#         get_pic("wuhan")
#         # example_search_photos()
#         # example_get_random_photos()
#         # example_download_with_tracking()  # 取消注释以下载图片
#         # example_get_photo_details()
#         # example_advanced_search()
#         # example_flask_integration()
#
#     except requests.exceptions.HTTPError as e:
#         print(f"\n❌ API 错误: {e}")
#         print("请检查:")
#         print("1. Access Key 是否正确")
#         print("2. 是否超过了速率限制（开发模式: 50 次/小时）")
#     except Exception as e:
#         print(f"\n❌ 发生错误: {e}")
#
#
# if __name__ == "__main__":
#     main()