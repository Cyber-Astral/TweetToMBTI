"""
测试错误处理机制
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from common.exceptions import (
    APIError,
    NoTweetsError,
    RateLimitError,
    UserNotFoundError,
)
from common.rate_limiter import RateLimiter
from scraper.error_handling import (
    check_user_exists,
    handle_api_errors,
    retry_with_backoff,
    validate_api_response,
    validate_tweet_data,
)


class TestAPIResponseValidation:
    """测试 API 响应验证"""
    
    def test_valid_response(self):
        """测试有效响应"""
        response = [
            {"text": "Hello", "author": "user1"},
            {"text": "World", "author": "user2"}
        ]
        valid, error = validate_api_response(response)
        assert valid is True
        assert error is None
    
    def test_empty_response(self):
        """测试空响应"""
        response = []
        valid, error = validate_api_response(response)
        assert valid is False
        assert "Empty response" in error
    
    def test_user_not_found_error(self):
        """测试用户不存在错误"""
        response = [{"error": "User not found: @unknownuser"}]
        valid, error = validate_api_response(response)
        assert valid is False
        assert "User not found" in error
    
    def test_rate_limit_error(self):
        """测试限流错误"""
        response = [{"error": "Rate limit exceeded"}]
        valid, error = validate_api_response(response)
        assert valid is False
        assert "Rate limit" in error
    
    def test_invalid_tweet_format(self):
        """测试无效推文格式"""
        response = [{"id": "123", "author": "user"}]  # 缺少 text 字段
        valid, error = validate_api_response(response)
        assert valid is False
        assert "Invalid tweet format" in error


class TestUserExistenceCheck:
    """测试用户存在性检查"""
    
    def test_user_exists(self):
        """测试用户存在的情况"""
        tweets = [
            {"author": "testuser", "text": "Tweet 1"},
            {"author": "testuser", "text": "Tweet 2"}
        ]
        assert check_user_exists(tweets, "testuser") is True
    
    def test_user_exists_case_insensitive(self):
        """测试用户名大小写不敏感"""
        tweets = [{"author": "TestUser", "text": "Tweet"}]
        assert check_user_exists(tweets, "testuser") is True
    
    def test_user_exists_with_dict_author(self):
        """测试 author 是字典的情况"""
        tweets = [{"author": {"userName": "testuser"}, "text": "Tweet"}]
        assert check_user_exists(tweets, "testuser") is True
    
    def test_user_not_exists(self):
        """测试用户不存在的情况"""
        tweets = [
            {"author": "otheruser", "text": "Tweet 1"},
            {"author": "anotheruser", "text": "Tweet 2"}
        ]
        assert check_user_exists(tweets, "testuser") is False
    
    def test_empty_tweets(self):
        """测试空推文列表"""
        assert check_user_exists([], "testuser") is False


class TestTweetDataValidation:
    """测试推文数据验证"""
    
    def test_valid_tweet_data(self):
        """测试有效的推文数据"""
        tweets = [
            {"author": "testuser", "text": "Valid tweet"},
            {"author": "testuser", "fullText": "Another valid tweet"}
        ]
        result = validate_tweet_data(tweets, "testuser")
        assert len(result) == 2
    
    def test_no_tweets_error(self):
        """测试无推文错误"""
        with pytest.raises(NoTweetsError) as excinfo:
            validate_tweet_data([], "testuser")
        assert "没有可访问的推文" in str(excinfo.value)
    
    def test_user_not_found_error(self):
        """测试用户不存在错误"""
        tweets = [{"author": "otheruser", "text": "Tweet"}]
        with pytest.raises(UserNotFoundError) as excinfo:
            validate_tweet_data(tweets, "testuser")
        assert "不存在或账号受限" in str(excinfo.value)
    
    def test_filter_invalid_tweets(self):
        """测试过滤无效推文"""
        tweets = [
            {"author": "testuser", "text": "Valid"},
            {"author": "testuser"},  # 无效：缺少文本
            {"author": "testuser", "text": ""},  # 无效：空文本
            {"author": "testuser", "fullText": "Also valid"}
        ]
        result = validate_tweet_data(tweets, "testuser")
        assert len(result) == 2


class TestRetryWithBackoff:
    """测试重试机制"""
    
    def test_success_on_first_try(self):
        """测试第一次就成功"""
        mock_func = Mock(return_value="success")
        decorated = retry_with_backoff(max_retries=3)(mock_func)
        
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_on_rate_limit(self):
        """测试限流时重试"""
        mock_func = Mock(side_effect=[
            RateLimitError("Rate limited", retry_after=1),
            "success"
        ])
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.1)(mock_func)
        
        with patch('time.sleep'):  # 跳过实际等待
            result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        mock_func = Mock(side_effect=APIError("API error"))
        decorated = retry_with_backoff(max_retries=2, initial_delay=0.1)(mock_func)
        
        with patch('time.sleep'):  # 跳过实际等待
            with pytest.raises(APIError):
                decorated()
        
        assert mock_func.call_count == 3  # 初始尝试 + 2次重试


class TestRateLimiter:
    """测试限流器"""
    
    def test_rate_limiter_allows_requests(self):
        """测试限流器允许请求"""
        limiter = RateLimiter(
            max_requests_per_minute=10,
            max_requests_per_hour=100,
            max_requests_per_day=1000
        )
        
        can_request, wait_time = limiter.can_make_request()
        assert can_request is True
        assert wait_time is None
    
    def test_rate_limiter_blocks_after_limit(self):
        """测试达到限制后阻止请求"""
        limiter = RateLimiter(max_requests_per_minute=2)
        
        # 记录两次请求
        limiter.record_request(success=True)
        limiter.record_request(success=True)
        
        # 第三次应该被阻止
        can_request, wait_time = limiter.can_make_request()
        assert can_request is False
        assert wait_time is not None
        assert wait_time > 0
    
    def test_rate_limiter_backoff(self):
        """测试退避机制"""
        limiter = RateLimiter()
        
        # 记录一次限流
        limiter.record_rate_limit_hit(retry_after=10)
        
        # 应该在退避期内
        can_request, wait_time = limiter.can_make_request()
        assert can_request is False
        assert wait_time is not None
        assert 9 <= wait_time <= 10  # 允许小误差
    
    def test_rate_limiter_stats(self):
        """测试统计信息"""
        limiter = RateLimiter(max_requests_per_minute=10)
        
        # 记录几次请求
        limiter.record_request(success=True)
        limiter.record_request(success=True)
        limiter.record_request(success=False)
        
        stats = limiter.get_stats()
        assert stats["minute"]["used"] == 3
        assert stats["minute"]["remaining"] == 7
        assert stats["minute"]["percentage"] == 30.0


class TestErrorHandlingDecorator:
    """测试错误处理装饰器"""
    
    def test_handle_api_errors_success(self):
        """测试成功情况"""
        mock_func = Mock(return_value=[{"text": "Tweet", "author": "user"}])
        decorated = handle_api_errors(mock_func)
        
        result = decorated()
        assert len(result) == 1
        assert result[0]["text"] == "Tweet"
    
    def test_handle_api_errors_user_not_found(self):
        """测试用户不存在错误"""
        mock_func = Mock(return_value=[{"error": "User not found"}])
        decorated = handle_api_errors(mock_func)
        
        with pytest.raises(UserNotFoundError):
            decorated()
    
    def test_handle_api_errors_rate_limit(self):
        """测试限流错误"""
        mock_func = Mock(side_effect=Exception("429 Too Many Requests"))
        decorated = handle_api_errors(mock_func)
        
        with pytest.raises(RateLimitError) as excinfo:
            decorated()
        assert "rate limit exceeded" in str(excinfo.value).lower()