"""
向后兼容的日志模块
将导入重定向到新的logging.logger模块
"""

from .logging.logger import *  # noqa: F401, F403