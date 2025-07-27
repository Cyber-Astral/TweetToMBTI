"""
自定义异常类
"""


class TwitterScraperError(Exception):
    """Twitter爬虫基础异常"""

    pass


class APIError(TwitterScraperError):
    """API调用异常"""

    pass


class RateLimitError(APIError):
    """API限流异常"""

    def __init__(self, message="API rate limit exceeded", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class TimeoutError(APIError):
    """API超时异常"""

    pass


class AuthenticationError(APIError):
    """认证失败异常"""

    pass


class DataValidationError(TwitterScraperError):
    """数据验证异常"""

    pass


class EmptyResponseError(DataValidationError):
    """空响应异常"""

    pass


class UserNotFoundError(DataValidationError):
    """用户不存在异常"""

    pass


class NoTweetsError(DataValidationError):
    """用户无推文异常"""

    pass


class ResourceCleanupError(TwitterScraperError):
    """资源清理失败异常"""

    pass
