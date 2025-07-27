"""
日志配置模块
提供统一的日志记录功能
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logger(
    name: str, level: str = "INFO", log_file: Optional[str] = None, console: bool = True
) -> logging.Logger:
    """
    设置并返回一个配置好的 logger

    Args:
        name: Logger 名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        console: 是否输出到控制台

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    # 控制台输出
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取已配置的 logger，如果不存在则创建一个默认配置的

    Args:
        name: Logger 名称

    Returns:
        Logger 实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# 创建项目默认 logger
def create_project_logger() -> logging.Logger:
    """
    创建项目默认的 logger，包含文件和控制台输出

    Returns:
        配置好的项目 logger
    """
    from .path_utils import PROJECT_ROOT

    # 创建日志目录
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # 生成日志文件名（按日期）
    log_file = log_dir / f"TweetToMBTI_{datetime.now().strftime('%Y%m%d')}.log"

    return setup_logger(name="TweetToMBTI", level="INFO", log_file=str(log_file), console=True)


# 便捷函数：获取模块专用 logger
def get_module_logger(module_name: str) -> logging.Logger:
    """
    为特定模块获取 logger

    Args:
        module_name: 模块名称

    Returns:
        模块专用的 logger
    """
    return get_logger(f"TweetToMBTI.{module_name}")
