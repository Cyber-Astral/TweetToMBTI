"""
Twitter Scraper Core Logic
基于函数式编程和契约式设计的核心抓取逻辑
"""

import functools
from typing import Callable, Dict, List

from .config import ScraperConfig, SearchQuery, UserTweetsQuery


def build_user_tweets_input(query: UserTweetsQuery) -> Dict:
    """
    构建用户推文查询的API输入

    前置条件：username非空，max_items > 0
    后置条件：返回有效的API输入配置
    """
    assert query["username"], "Username cannot be empty"
    assert query["max_items"] > 0, "max_items must be positive"

    return {"twitterHandles": [query["username"]], "maxItems": query["max_items"], "sort": "Latest"}


def build_search_input(query: SearchQuery) -> Dict:
    """
    构建搜索查询的API输入

    前置条件：search_terms非空，max_items > 0
    后置条件：返回有效的API输入配置
    """
    assert query["search_terms"], "Search terms cannot be empty"
    assert query["max_items"] > 0, "max_items must be positive"

    return {
        "searchTerms": [query["search_terms"]],  # searchTerms 需要是数组
        "maxItems": query["max_items"],
        "sort": "Latest",
    }


def create_api_caller(config: ScraperConfig) -> Callable[[Dict], List[Dict]]:
    """
    创建配置好的API调用函数（高阶函数）

    返回一个闭包，封装了API客户端配置
    """
    from apify_client import ApifyClient

    client = ApifyClient(config["api_token"])

    def call_actor(input_data: Dict) -> List[Dict]:
        """执行API调用并返回结果列表"""
        run = client.actor(config["actor_id"]).call(run_input=input_data)
        return list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return call_actor


def extract_tweet_fields(tweet: Dict) -> Dict:
    """
    提取推文的关键字段（纯函数）

    保持数据不可变，只提取必要信息
    """
    # 基于实际API响应格式提取字段
    author = tweet.get("author", {})
    if isinstance(author, dict):
        author_username = author.get("userName", "")
        author_name = author.get("name", "") or author.get("displayName", "")
    else:
        author_username = tweet.get("userName", "")
        author_name = tweet.get("name", "")

    # 处理媒体内容
    media_list = tweet.get("media", [])
    if not isinstance(media_list, list):
        media_list = []

    # 提取照片URL
    photos = tweet.get("photos", [])
    if isinstance(photos, list):
        media_urls = [
            photo.get("url", "") if isinstance(photo, dict) else str(photo) for photo in photos
        ]
    else:
        media_urls = [
            media.get("url", "") if isinstance(media, dict) else str(media) for media in media_list
        ]

    return {
        "text": tweet.get("text", "") or tweet.get("fullText", ""),
        "author": author_username,
        "author_name": author_name,
        "created_at": tweet.get("createdAt", ""),
        "likes": tweet.get("likeCount", 0),
        "retweets": tweet.get("retweetCount", 0),
        "replies": tweet.get("replyCount", 0),
        "views": tweet.get("viewCount", 0),
        "url": tweet.get("url", "") or tweet.get("twitterUrl", ""),
        "id": tweet.get("id", ""),
        "is_reply": tweet.get("isReply", False) or bool(tweet.get("inReplyToId")),
        "is_retweet": tweet.get("isRetweet", False) or bool(tweet.get("retweetedStatusId")),
        "is_quote": tweet.get("isQuote", False),
        "is_pin": tweet.get("isPin", False),
        "media": media_urls,
        "hashtags": tweet.get("hashtags", []),
        "mentions": tweet.get("mentions", []),
    }


def compose(*functions: Callable) -> Callable:
    """
    函数组合工具（从右到左）

    使用reduce实现函数组合，支持管道式数据处理
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def scrape_tweets(query: UserTweetsQuery, config: ScraperConfig) -> List[Dict]:
    """
    主抓取函数 - 通过组合纯函数实现

    前置条件：query包含有效的用户名和数量
    后置条件：返回格式化的推文列表
    """
    # 1. 构建输入配置
    input_data = build_user_tweets_input(query)

    # 2. 创建API调用器
    api_caller = create_api_caller(config)

    # 3. 执行API调用
    raw_tweets = api_caller(input_data)

    # 4. 转换数据（使用map保持函数式风格）
    return list(map(extract_tweet_fields, raw_tweets))


def filter_tweets(tweets: List[Dict], predicate: Callable[[Dict], bool]) -> List[Dict]:
    """
    过滤推文的纯函数

    可用于后续的数据筛选，如只获取原创推文等
    """
    return list(filter(predicate, tweets))


def sort_tweets(tweets: List[Dict], key: str, reverse: bool = True) -> List[Dict]:
    """
    排序推文的纯函数

    默认按指定字段降序排列
    """
    return sorted(tweets, key=lambda t: t.get(key, 0), reverse=reverse)


def scrape_with_search(query: SearchQuery, config: ScraperConfig) -> List[Dict]:
    """
    使用搜索条件抓取推文

    前置条件：query包含有效的搜索条件和数量
    后置条件：返回格式化的推文列表
    """
    # 1. 构建输入配置
    input_data = build_search_input(query)

    # 2. 创建API调用器
    api_caller = create_api_caller(config)

    # 3. 执行API调用
    raw_tweets = api_caller(input_data)

    # 4. 转换数据
    return list(map(extract_tweet_fields, raw_tweets))
