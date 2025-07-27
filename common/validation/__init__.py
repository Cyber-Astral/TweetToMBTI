"""
验证和异常处理模块
"""

from .exceptions import (
    APIError,
    AuthenticationError,
    DataValidationError,
    EmptyResponseError,
    NoTweetsError,
    RateLimitError,
    ResourceCleanupError,
    TimeoutError,
    TwitterScraperError,
    UserNotFoundError,
)
from .validators import (
    sanitize_filename,
    sanitize_username,
    validate_api_key,
    validate_count_arg,
    validate_file_path,
    validate_tweet_count,
    validate_username,
    validate_username_arg,
)

__all__ = [
    # exceptions
    "APIError",
    "AuthenticationError",
    "DataValidationError",
    "EmptyResponseError",
    "NoTweetsError",
    "RateLimitError",
    "ResourceCleanupError",
    "TimeoutError",
    "TwitterScraperError",
    "UserNotFoundError",
    # validators
    "sanitize_filename",
    "sanitize_username",
    "validate_api_key",
    "validate_count_arg",
    "validate_file_path",
    "validate_tweet_count",
    "validate_username",
    "validate_username_arg",
]