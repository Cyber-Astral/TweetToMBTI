"""
错误处理和重试机制
"""

import time
from functools import wraps
from typing import Callable, Dict, List, Optional, Tuple

from common.exceptions import (
    APIError,
    NoTweetsError,
    RateLimitError,
    UserNotFoundError,
)
from common.rate_limiter import get_rate_limiter


def validate_api_response(response: List[Dict]) -> Tuple[bool, Optional[str]]:
    """
    验证API响应是否有效
    
    Returns:
        (是否有效, 错误信息)
    """
    if not response:
        return False, "Empty response from API"
    
    # 检查是否包含错误信息
    if len(response) == 1:
        first_item = response[0]
        if isinstance(first_item, dict):
            # 检查常见的错误模式
            if first_item.get("error"):
                error_msg = first_item.get("error", "Unknown error")
                if "User not found" in error_msg or "does not exist" in error_msg:
                    return False, f"User not found: {error_msg}"
                elif "rate limit" in error_msg.lower():
                    return False, f"Rate limit: {error_msg}"
                else:
                    return False, f"API error: {error_msg}"
            
            # 检查是否是有效的推文数据
            if not first_item.get("text") and not first_item.get("fullText"):
                return False, "Invalid tweet format"
    
    return True, None


def check_user_exists(tweets: List[Dict], username: str) -> bool:
    """
    通过推文数据检查用户是否存在
    """
    if not tweets:
        return False
    
    # 检查是否有推文作者匹配用户名
    for tweet in tweets[:5]:  # 只检查前几条
        author = tweet.get("author", "")
        if isinstance(author, dict):
            author = author.get("userName", "")
        
        if author.lower() == username.lower():
            return True
    
    return False


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    service_name: str = "apify"
) -> Callable:
    """
    带指数退避的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 退避因子
        max_delay: 最大延迟（秒）
        service_name: 服务名称（用于限流器）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay
            rate_limiter = get_rate_limiter(service_name)
            
            for attempt in range(max_retries + 1):
                # 检查限流器
                can_request, wait_time = rate_limiter.can_make_request()
                if not can_request and wait_time:
                    print(f"限流器：需要等待 {wait_time:.1f} 秒")
                    time.sleep(wait_time)
                
                try:
                    result = func(*args, **kwargs)
                    # 记录成功请求
                    rate_limiter.record_request(success=True)
                    return result
                except RateLimitError as e:
                    # 记录限流
                    rate_limiter.record_rate_limit_hit(e.retry_after)
                    last_exception = e
                    # 如果有明确的重试时间，使用它
                    if e.retry_after:
                        wait_time = min(e.retry_after, max_delay)
                    else:
                        wait_time = min(delay, max_delay)
                    
                    if attempt < max_retries:
                        print(f"API限流，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        delay *= backoff_factor
                except (APIError, Exception) as e:
                    last_exception = e
                    # 记录失败请求
                    rate_limiter.record_request(success=False)
                    
                    if attempt < max_retries:
                        wait_time = min(delay, max_delay)
                        print(f"API错误: {str(e)}，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        delay *= backoff_factor
                    else:
                        break
            
            # 所有重试都失败
            if last_exception:
                raise last_exception
            else:
                raise APIError(f"Failed after {max_retries} retries")
        
        return wrapper
    return decorator


def handle_api_errors(func: Callable) -> Callable:
    """
    API错误处理装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # 验证响应
            if isinstance(result, list):
                valid, error_msg = validate_api_response(result)
                if not valid:
                    if "User not found" in error_msg:
                        raise UserNotFoundError(error_msg)
                    elif "Rate limit" in error_msg:
                        raise RateLimitError(error_msg)
                    else:
                        raise APIError(error_msg)
            
            return result
            
        except Exception as e:
            # 转换常见的错误类型
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                raise RateLimitError(f"API rate limit exceeded: {str(e)}")
            elif "user not found" in error_str or "does not exist" in error_str:
                raise UserNotFoundError(f"User not found: {str(e)}")
            elif "timeout" in error_str:
                raise APIError(f"API timeout: {str(e)}")
            else:
                raise
    
    return wrapper


def validate_tweet_data(tweets: List[Dict], username: str) -> List[Dict]:
    """
    验证推文数据的完整性和有效性
    
    Args:
        tweets: 推文列表
        username: 期望的用户名
        
    Returns:
        验证后的推文列表
        
    Raises:
        UserNotFoundError: 用户不存在
        NoTweetsError: 用户无推文
    """
    if not tweets:
        raise NoTweetsError(f"用户 @{username} 没有可访问的推文")
    
    # 检查用户是否存在
    if not check_user_exists(tweets, username):
        # 可能是私密账号或被封禁
        raise UserNotFoundError(
            f"用户 @{username} 不存在或账号受限（私密/被封禁）"
        )
    
    # 过滤掉无效的推文
    valid_tweets = []
    for tweet in tweets:
        if tweet.get("text") or tweet.get("fullText"):
            valid_tweets.append(tweet)
    
    if not valid_tweets:
        raise NoTweetsError(f"用户 @{username} 的推文数据无效")
    
    return valid_tweets