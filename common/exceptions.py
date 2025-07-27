"""
向后兼容的异常模块
将导入重定向到新的validation.exceptions模块
"""

from .validation.exceptions import *  # noqa: F401, F403