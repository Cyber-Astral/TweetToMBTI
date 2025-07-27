"""
推文处理工具函数
提供通用的推文过滤、简化和验证功能
"""

from typing import Callable, Dict, List


def filter_tweets(tweets: List[Dict], predicate: Callable[[Dict], bool]) -> List[Dict]:
    """
    根据条件过滤推文

    Args:
        tweets: 原始推文列表
        predicate: 过滤条件函数

    Returns:
        过滤后的推文列表
    """
    if not tweets:
        return []
    return [tweet for tweet in tweets if predicate(tweet)]


def filter_original_tweets(tweets: List[Dict]) -> List[Dict]:
    """过滤原创推文（非转推、非回复）"""
    return filter_tweets(
        tweets, lambda t: not t.get("is_retweet", False) and not t.get("is_reply", False)
    )


def filter_reply_tweets(tweets: List[Dict]) -> List[Dict]:
    """过滤回复推文（非转推）"""
    return filter_tweets(
        tweets, lambda t: t.get("is_reply", False) and not t.get("is_retweet", False)
    )


def filter_retweets(tweets: List[Dict]) -> List[Dict]:
    """过滤转推"""
    return filter_tweets(tweets, lambda t: t.get("is_retweet", False))


def filter_tweets_by_type(
    tweets: List[Dict],
    tweet_type: str = "all"
) -> List[Dict]:
    """
    根据类型过滤推文（统一接口）
    
    Args:
        tweets: 推文列表
        tweet_type: 推文类型 ('all', 'original', 'reply', 'retweet')
        
    Returns:
        过滤后的推文列表
    """
    if tweet_type == "original":
        return filter_original_tweets(tweets)
    elif tweet_type == "reply":
        return filter_reply_tweets(tweets)
    elif tweet_type == "retweet":
        return filter_retweets(tweets)
    else:
        return tweets


def filter_tweets_by_criteria(
    tweets: List[Dict],
    min_likes: int = None,
    min_retweets: int = None,
    min_replies: int = None,
    has_media: bool = None,
    has_hashtags: bool = None,
    text_contains: str = None,
    author: str = None
) -> List[Dict]:
    """
    根据多个条件过滤推文
    
    Args:
        tweets: 推文列表
        min_likes: 最小点赞数
        min_retweets: 最小转发数
        min_replies: 最小回复数
        has_media: 是否包含媒体
        has_hashtags: 是否包含标签
        text_contains: 文本包含内容
        author: 作者用户名
        
    Returns:
        过滤后的推文列表
    """
    filtered = tweets
    
    if min_likes is not None:
        filtered = filter_tweets(
            filtered, lambda t: t.get("likes", 0) >= min_likes
        )
    
    if min_retweets is not None:
        filtered = filter_tweets(
            filtered, lambda t: t.get("retweets", 0) >= min_retweets
        )
    
    if min_replies is not None:
        filtered = filter_tweets(
            filtered, lambda t: t.get("replies", 0) >= min_replies
        )
    
    if has_media is not None:
        filtered = filter_tweets(
            filtered, lambda t: bool(t.get("media", [])) == has_media
        )
    
    if has_hashtags is not None:
        filtered = filter_tweets(
            filtered, lambda t: bool(t.get("hashtags", [])) == has_hashtags
        )
    
    if text_contains:
        text_lower = text_contains.lower()
        filtered = filter_tweets(
            filtered, lambda t: text_lower in t.get("text", "").lower()
        )
    
    if author:
        author_lower = author.lower()
        filtered = filter_tweets(
            filtered, lambda t: t.get("author", "").lower() == author_lower
        )
    
    return filtered


def simplify_tweet(tweet: Dict) -> Dict:
    """
    简化单条推文数据，只保留必要字段

    Args:
        tweet: 原始推文数据

    Returns:
        简化后的推文数据
    """
    return {
        "text": tweet.get("text", ""),
        "created_at": tweet.get("created_at", ""),
        "reply_to": tweet.get("in_reply_to_screen_name", ""),
        "metrics": {
            "likes": tweet.get("favorite_count", 0),
            "retweets": tweet.get("retweet_count", 0),
            "replies": tweet.get("reply_count", 0),
        },
    }


def simplify_tweets(tweets: List[Dict]) -> List[Dict]:
    """
    批量简化推文数据

    Args:
        tweets: 原始推文列表

    Returns:
        简化后的推文列表
    """
    return [simplify_tweet(tweet) for tweet in tweets]


def validate_tweet_data(tweet: Dict) -> bool:
    """
    验证推文数据是否有效

    Args:
        tweet: 推文数据

    Returns:
        是否有效
    """
    # 必须有文本内容
    if not tweet.get("text"):
        return False

    # 文本长度应该合理（不是空的，也不太长）
    text_length = len(tweet["text"].strip())
    if text_length < 1 or text_length > 10000:
        return False

    return True


def get_user_display_name(tweets: List[Dict]) -> str:
    """
    从推文列表中提取用户显示名称

    Args:
        tweets: 推文列表

    Returns:
        用户显示名称，如果找不到返回空字符串
    """
    for tweet in tweets:
        if tweet.get("author_name"):
            return tweet["author_name"]
    return ""


def calculate_tweet_stats(tweets: List[Dict]) -> Dict:
    """
    计算推文统计信息

    Args:
        tweets: 推文列表

    Returns:
        统计信息字典
    """
    if not tweets:
        return {
            "total": 0,
            "avg_length": 0,
            "total_likes": 0,
            "total_retweets": 0,
            "total_replies": 0,
        }

    total_length = sum(len(tweet.get("text", "")) for tweet in tweets)
    total_likes = sum(tweet.get("favorite_count", 0) for tweet in tweets)
    total_retweets = sum(tweet.get("retweet_count", 0) for tweet in tweets)
    total_replies = sum(tweet.get("reply_count", 0) for tweet in tweets)

    return {
        "total": len(tweets),
        "avg_length": total_length // len(tweets) if tweets else 0,
        "total_likes": total_likes,
        "total_retweets": total_retweets,
        "total_replies": total_replies,
    }
