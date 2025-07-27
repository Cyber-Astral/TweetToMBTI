"""
向后兼容的速率限制模块
将导入重定向到新的utils.rate_limiter模块
"""

from .utils.rate_limiter import *  # noqa: F401, F403