"""
MBTI 人格分析核心逻辑
负责收集和处理推文数据
"""

import sys
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.exceptions import (  # noqa: E402
    NoTweetsError,
    UserNotFoundError,
)
from common.path_utils import add_project_to_path  # noqa: E402
from scraper import (  # noqa: E402
    filter_tweets,
    scrape_user_original_tweets_advanced,
    scrape_user_replies_advanced,
    scrape_user_tweets,
)

add_project_to_path()


def collect_tweet_data(
    username: str, original_count: int = 100, reply_count: int = 100
) -> Dict[str, any]:
    """
    收集用户推文数据

    Args:
        username: Twitter用户名（不带@）
        original_count: 原创推文数量
        reply_count: 回复推文数量

    Returns:
        包含原创推文和回复推文的字典
    """
    # 分别抓取原创和回复，使用更精确的方法
    print("    - 正在抓取推文数据...")

    try:
        # 方案1：先尝试使用搜索API（成本低）
        try:
            # 尝试使用高级搜索
            original_tweets = scrape_user_original_tweets_advanced(username, original_count)
            reply_tweets = scrape_user_replies_advanced(username, reply_count)

            # 如果原创推文不够，使用补充方案
            if len(original_tweets) < original_count:
                print("    - 原创推文不足，使用补充方案...")
                # 只额外抓取需要的数量
                needed = original_count - len(original_tweets)
                extra_tweets = scrape_user_tweets(username, needed * 2)
                extra_originals = filter_tweets(
                    extra_tweets, lambda t: not t["is_retweet"] and not t["is_reply"]
                )
                original_tweets.extend(extra_originals[:needed])
                original_tweets = original_tweets[:original_count]

        except (UserNotFoundError, NoTweetsError):
            # 用户不存在或无推文，直接抛出
            raise
        except Exception:
            # 如果搜索失败，使用传统方法但限制数量
            print("    - 搜索失败，使用备用方案...")
            tweets = scrape_user_tweets(username, 300)  # 限制最多300条
            original_tweets = filter_tweets(
                tweets, lambda t: not t["is_retweet"] and not t["is_reply"]
            )[:original_count]
            reply_tweets = filter_tweets(tweets, lambda t: t["is_reply"] and not t["is_retweet"])[
                :reply_count
            ]
    except (UserNotFoundError, NoTweetsError) as e:
        # 记录错误并重新抛出
        print(f"    ✗ {str(e)}")
        raise

    # 获取用户的显示名称（从第一条推文中提取）
    display_name = ""
    if original_tweets and original_tweets[0].get("author_name"):
        display_name = original_tweets[0]["author_name"]
    elif reply_tweets and reply_tweets[0].get("author_name"):
        display_name = reply_tweets[0]["author_name"]

    return {
        "username": username,
        "display_name": display_name,
        "original_tweets": simplify_tweets(original_tweets),
        "reply_tweets": simplify_tweets(reply_tweets),
        "stats": {"total_original": len(original_tweets), "total_replies": len(reply_tweets)},
    }


def simplify_tweets(tweets: List[Dict]) -> List[Dict]:
    """
    简化推文数据，只保留分析所需字段

    Args:
        tweets: 原始推文列表

    Returns:
        简化后的推文列表
    """
    simplified = []

    for tweet in tweets:
        # 提取关键信息
        simplified_tweet = {
            "text": tweet["text"],
            "created_at": tweet["created_at"],
            "likes": tweet["likes"],
            "retweets": tweet["retweets"],
            "replies": tweet["replies"],
            "hashtags": tweet["hashtags"],
            "mentions": tweet["mentions"],
            "has_media": len(tweet.get("media", [])) > 0,
        }

        # 计算互动率
        simplified_tweet["engagement_rate"] = (
            tweet["likes"] + tweet["retweets"] + tweet["replies"]
        ) / max(tweet.get("views", 1), 1)

        simplified.append(simplified_tweet)

    return simplified


def analyze_tweet_patterns(tweet_data: Dict) -> Dict:
    """
    分析推文模式，为MBTI分析提供额外信息

    Args:
        tweet_data: 收集的推文数据

    Returns:
        推文模式分析结果
    """
    patterns = {
        "posting_frequency": {},
        "interaction_style": {},
        "content_patterns": {},
        "language_style": {},
    }

    # 分析原创推文
    if tweet_data["original_tweets"]:
        original = tweet_data["original_tweets"]

        # 平均推文长度
        avg_length = sum(len(t["text"]) for t in original) / len(original)
        patterns["content_patterns"]["avg_tweet_length"] = avg_length

        # 使用表情/标签/提及的频率
        patterns["content_patterns"]["hashtag_usage"] = sum(
            1 for t in original if t["hashtags"]
        ) / len(original)

        patterns["content_patterns"]["mention_usage"] = sum(
            1 for t in original if t["mentions"]
        ) / len(original)

        # 媒体使用频率
        patterns["content_patterns"]["media_usage"] = sum(
            1 for t in original if t["has_media"]
        ) / len(original)

        # 平均互动率
        patterns["interaction_style"]["avg_engagement"] = sum(
            t["engagement_rate"] for t in original
        ) / len(original)

    # 分析回复推文
    if tweet_data["reply_tweets"]:
        replies = tweet_data["reply_tweets"]

        # 回复的平均长度
        avg_reply_length = sum(len(t["text"]) for t in replies) / len(replies)
        patterns["interaction_style"]["avg_reply_length"] = avg_reply_length

        # 回复中的提及频率（表示互动深度）
        patterns["interaction_style"]["reply_mention_rate"] = sum(
            1 for t in replies if t["mentions"]
        ) / len(replies)

    return patterns
