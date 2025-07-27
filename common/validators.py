"""
向后兼容的验证器模块
将导入重定向到新的validation.validators模块
"""

from .validation.validators import *  # noqa: F401, F403