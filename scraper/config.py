"""
Twitter Scraper Configuration
基于数据导向编程原则的配置模块
"""

import os
from typing import TypedDict

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ScraperConfig(TypedDict):
    """API配置结构"""

    api_token: str
    actor_id: str


class UserTweetsQuery(TypedDict):
    """用户推文查询参数"""

    username: str
    max_items: int


class SearchQuery(TypedDict):
    """搜索查询参数"""

    search_terms: str
    max_items: int


# 从环境变量读取配置
api_token = os.getenv("APIFY_API_TOKEN")
if not api_token:
    raise ValueError("APIFY_API_TOKEN environment variable is not set")

# 全局配置
CONFIG = ScraperConfig(api_token=api_token, actor_id="apidojo/tweet-scraper")

# 默认值
DEFAULT_MAX_ITEMS = 100

# 数据保存路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "scraped_data")
USER_TWEETS_DIR = os.path.join(DATA_DIR, "user_tweets")
