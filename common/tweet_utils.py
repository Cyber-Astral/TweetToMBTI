"""
向后兼容的推文工具模块
将导入重定向到新的data.tweet_utils模块
"""

from .data.tweet_utils import *  # noqa: F401, F403