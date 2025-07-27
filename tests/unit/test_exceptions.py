"""
异常模块的单元测试
"""

import pytest

from common.exceptions import (
    APIError,
    AuthenticationError,
    DataValidationError,
    EmptyResponseError,
    RateLimitError,
    TimeoutError,
    TwitterScraperError,
)


class TestExceptionHierarchy:
    """测试异常层次结构"""

    def test_base_exception(self):
        """测试基础异常"""
        with pytest.raises(TwitterScraperError):
            raise TwitterScraperError("基础异常")

    def test_api_exceptions(self):
        """测试 API 相关异常"""
        # APIError 是 TwitterScraperError 的子类
        with pytest.raises(TwitterScraperError):
            raise APIError("API 错误")

        # 具体的 API 异常
        with pytest.raises(APIError):
            raise RateLimitError("限流")

        with pytest.raises(APIError):
            raise TimeoutError("超时")

        with pytest.raises(APIError):
            raise AuthenticationError("认证失败")

    def test_data_exceptions(self):
        """测试数据相关异常"""
        with pytest.raises(TwitterScraperError):
            raise DataValidationError("数据验证失败")

        with pytest.raises(DataValidationError):
            raise EmptyResponseError("空响应")


class TestRateLimitError:
    """测试限流异常"""

    def test_default_retry_after(self):
        """测试默认重试时间"""
        error = RateLimitError()
        assert error.retry_after is None
        assert str(error) == "API rate limit exceeded"

    def test_custom_retry_after(self):
        """测试自定义重试时间"""
        error = RateLimitError("请等待", retry_after=60)
        assert error.retry_after == 60
        assert str(error) == "请等待"


class TestExceptionMessages:
    """测试异常消息"""

    def test_exception_messages(self):
        """测试各种异常的消息"""
        exceptions = [
            (TwitterScraperError("基础错误"), "基础错误"),
            (APIError("API 错误"), "API 错误"),
            (RateLimitError("限流错误"), "限流错误"),
            (TimeoutError("超时错误"), "超时错误"),
            (AuthenticationError("认证错误"), "认证错误"),
            (DataValidationError("验证错误"), "验证错误"),
            (EmptyResponseError("空响应"), "空响应"),
        ]

        for exception, expected_message in exceptions:
            assert str(exception) == expected_message
