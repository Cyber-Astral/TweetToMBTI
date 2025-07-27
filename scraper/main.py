"""
Twitter Scraper Main Entry Point
最简化的用户接口
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List

from common.exceptions import (
    NoTweetsError,
    UserNotFoundError,
)
from .config import (
    CONFIG,
    DATA_DIR,
    DEFAULT_MAX_ITEMS,
    USER_TWEETS_DIR,
    SearchQuery,
    UserTweetsQuery,
)
from .error_handling import (
    handle_api_errors,
    retry_with_backoff,
    validate_tweet_data,
)
from .scraper import filter_tweets, scrape_tweets, scrape_with_search, sort_tweets


@retry_with_backoff(max_retries=3)
@handle_api_errors
def scrape_user_tweets(username: str, max_tweets: int = DEFAULT_MAX_ITEMS) -> List[Dict]:
    """
    抓取指定用户的推文

    Args:
        username: Twitter用户名（不带@）
        max_tweets: 最大抓取数量

    Returns:
        推文列表，每条推文包含text、author、created_at等字段
        
    Raises:
        UserNotFoundError: 用户不存在
        NoTweetsError: 用户无推文
        RateLimitError: API限流
        APIError: 其他API错误
    """
    query = UserTweetsQuery(username=username, max_items=max_tweets)
    tweets = scrape_tweets(query, CONFIG)
    
    # 验证推文数据
    return validate_tweet_data(tweets, username)


def scrape_user_original_tweets(username: str, max_tweets: int = DEFAULT_MAX_ITEMS) -> List[Dict]:
    """
    只抓取用户的原创推文（排除转发和回复）

    演示如何使用filter_tweets进行数据筛选
    """
    tweets = scrape_user_tweets(username, max_tweets)
    return filter_tweets(tweets, lambda t: not t["is_retweet"] and not t["is_reply"])


def scrape_user_original_tweets_advanced(
    username: str, max_tweets: int = DEFAULT_MAX_ITEMS
) -> List[Dict]:
    """
    使用高级搜索功能抓取用户的原创推文

    使用 searchTerms 参数，在 API 层面就过滤掉转发，提高效率
    """
    # 使用 Twitter 高级搜索语法
    # from:username - 来自特定用户
    # -filter:nativeretweets - 排除转发
    # -filter:replies - 排除回复
    search_terms = f"from:{username} -filter:nativeretweets -filter:replies"

    query = SearchQuery(search_terms=search_terms, max_items=max_tweets)
    return scrape_with_search(query, CONFIG)


def scrape_user_replies_advanced(username: str, max_tweets: int = DEFAULT_MAX_ITEMS) -> List[Dict]:
    """
    使用高级搜索功能抓取用户的回复推文

    使用 searchTerms 参数，在 API 层面就筛选回复
    """
    # 使用 Twitter 高级搜索语法
    # from:username - 来自特定用户
    # filter:replies - 只获取回复
    search_terms = f"from:{username} filter:replies"

    query = SearchQuery(search_terms=search_terms, max_items=max_tweets)
    return scrape_with_search(query, CONFIG)


def scrape_popular_tweets(
    username: str, max_tweets: int = DEFAULT_MAX_ITEMS, min_likes: int = 100
) -> List[Dict]:
    """
    抓取用户的热门推文（按点赞数筛选）

    演示函数组合的使用
    """
    tweets = scrape_user_tweets(username, max_tweets)
    filtered = filter_tweets(tweets, lambda t: t["likes"] >= min_likes)
    return sort_tweets(filtered, "likes")


def ensure_data_directory(directory: str) -> str:
    """
    确保数据目录存在

    返回完整的目录路径
    """
    os.makedirs(directory, exist_ok=True)
    return directory


def generate_filename(prefix: str, extension: str) -> str:
    """
    生成带时间戳的文件名

    格式: prefix_YYYYMMDD_HHMMSS.extension
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_to_json(tweets: List[Dict], filename: str = None, auto_dir: bool = True) -> str:
    """
    将推文保存到JSON文件

    Args:
        tweets: 推文列表
        filename: 自定义文件名（可选）
        auto_dir: 是否自动使用数据目录

    Returns:
        保存的文件路径
    """
    if filename is None:
        # 自动生成文件名
        filename = generate_filename("tweets", "json")

    if auto_dir and not os.path.isabs(filename):
        # 使用默认数据目录
        directory = ensure_data_directory(DATA_DIR)
        filepath = os.path.join(directory, filename)
    else:
        filepath = filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

    return filepath


def save_to_csv(tweets: List[Dict], filename: str = None, auto_dir: bool = True) -> str:
    """
    将推文保存到CSV文件

    Args:
        tweets: 推文列表
        filename: 自定义文件名（可选）
        auto_dir: 是否自动使用数据目录

    Returns:
        保存的文件路径
    """
    if not tweets:
        return None

    if filename is None:
        # 自动生成文件名
        filename = generate_filename("tweets", "csv")

    if auto_dir and not os.path.isabs(filename):
        # 使用默认数据目录
        directory = ensure_data_directory(DATA_DIR)
        filepath = os.path.join(directory, filename)
    else:
        filepath = filename

    # 选择要保存的字段
    fields = ["created_at", "author", "text", "likes", "retweets", "replies", "url"]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tweets)

    return filepath


def save_user_tweets(username: str, tweets: List[Dict], format: str = "both") -> Dict[str, str]:
    """
    保存用户推文到专门的用户文件夹

    Args:
        username: 用户名
        tweets: 推文列表
        format: 保存格式 ("json", "csv", "both")

    Returns:
        保存的文件路径字典
    """
    # 创建用户专属文件夹
    user_dir = os.path.join(USER_TWEETS_DIR, username)
    ensure_data_directory(user_dir)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = {}

    if format in ["json", "both"]:
        json_path = os.path.join(user_dir, f"{username}_{timestamp}.json")
        save_to_json(tweets, json_path, auto_dir=False)
        saved_files["json"] = json_path

    if format in ["csv", "both"]:
        csv_path = os.path.join(user_dir, f"{username}_{timestamp}.csv")
        save_to_csv(tweets, csv_path, auto_dir=False)
        saved_files["csv"] = csv_path

    return saved_files


if __name__ == "__main__":
    # 使用示例
    print("Twitter Scraper - 使用示例\n")

    # 创建数据目录
    print(f"数据将保存到: {os.path.abspath(DATA_DIR)}/")

    # 示例1：抓取用户推文并自动保存
    print("\n1. 抓取 elonmusk 的最新 10 条推文")
    try:
        tweets = scrape_user_tweets("elonmusk", max_tweets=10)
        print(f"成功抓取 {len(tweets)} 条推文")

        if tweets:
            # 自动保存到用户专属文件夹
            saved_files = save_user_tweets("elonmusk", tweets)
            print("数据已保存到:")
            for format, path in saved_files.items():
                print(f"  - {format.upper()}: {path}")

            print(f"\n最新推文预览: {tweets[0]['text'][:100]}...")
    except Exception as e:
        print(f"错误: {e}")

    # 示例2：使用简化的保存功能
    print("\n2. 简化保存示例")
    print("- save_to_json(tweets) - 自动保存到 scraped_data/ 目录")
    print("- save_to_csv(tweets) - 自动保存到 scraped_data/ 目录")
    print("- save_user_tweets(username, tweets) - 保存到 scraped_data/user_tweets/username/")
