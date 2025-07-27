"""
输入验证模块
提供各种输入数据的验证功能
"""

import re
from typing import Optional, Tuple

from .exceptions import DataValidationError


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    验证 Twitter 用户名

    Args:
        username: 用户名

    Returns:
        (是否有效, 错误信息)
    """
    if not username:
        return False, "用户名不能为空"

    # 移除可能的 @ 前缀
    username = username.lstrip("@")

    # Twitter 用户名规则：
    # 1. 长度 1-15 个字符
    # 2. 只能包含字母、数字和下划线
    # 3. 不能全是数字

    if len(username) < 1 or len(username) > 15:
        return False, "用户名长度必须在 1-15 个字符之间"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "用户名只能包含字母、数字和下划线"

    if username.isdigit():
        return False, "用户名不能全是数字"

    return True, None


def validate_tweet_count(count: int) -> Tuple[bool, Optional[str]]:
    """
    验证推文数量

    Args:
        count: 推文数量

    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(count, int):
        return False, "推文数量必须是整数"

    if count < 1:
        return False, "推文数量必须大于 0"

    if count > 1000:
        return False, "推文数量不能超过 1000（API 限制）"

    return True, None


def validate_api_key(api_key: str, key_type: str = "generic") -> Tuple[bool, Optional[str]]:
    """
    验证 API 密钥格式

    Args:
        api_key: API 密钥
        key_type: 密钥类型 (gemini, apify, generic)

    Returns:
        (是否有效, 错误信息)
    """
    if not api_key:
        return False, "API 密钥不能为空"

    # 移除可能的空白字符
    api_key = api_key.strip()

    if key_type == "gemini":
        # Gemini API key 通常以 "AIza" 开头
        if not api_key.startswith("AIza"):
            return False, "Gemini API 密钥格式不正确"
        if len(api_key) < 39:
            return False, "Gemini API 密钥长度不正确"

    elif key_type == "apify":
        # Apify API token 通常以 "apify_api_" 开头
        if not api_key.startswith("apify_api_"):
            return False, "Apify API token 格式不正确"
        if len(api_key) < 48:
            return False, "Apify API token 长度不正确"

    # 检查是否包含非法字符
    if not re.match(r"^[a-zA-Z0-9_-]+$", api_key):
        return False, "API 密钥包含非法字符"

    return True, None


def validate_file_path(path: str, must_exist: bool = False) -> Tuple[bool, Optional[str]]:
    """
    验证文件路径

    Args:
        path: 文件路径
        must_exist: 文件是否必须存在

    Returns:
        (是否有效, 错误信息)
    """
    if not path:
        return False, "文件路径不能为空"

    # 检查路径中是否包含危险字符
    dangerous_patterns = ["../", "...", "~/", "${", "%("]
    for pattern in dangerous_patterns:
        if pattern in path:
            return False, f"文件路径包含潜在危险字符: {pattern}"

    if must_exist:
        from pathlib import Path

        if not Path(path).exists():
            return False, f"文件不存在: {path}"

    return True, None


def sanitize_username(username: str) -> str:
    """
    清理和标准化用户名

    Args:
        username: 原始用户名

    Returns:
        清理后的用户名
    """
    # 移除 @ 前缀
    username = username.lstrip("@")

    # 移除空白字符
    username = username.strip()

    # 转小写（Twitter 用户名不区分大小写）
    username = username.lower()

    return username


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        安全的文件名
    """
    # 替换不安全字符
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    # 移除控制字符
    filename = "".join(char for char in filename if ord(char) >= 32)

    # 限制长度
    max_length = 200
    if len(filename) > max_length:
        # 保留扩展名
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[: max_length - len(ext) - 1] + "." + ext if ext else name[:max_length]

    return filename


# 装饰器：自动验证函数参数
def validate_username_arg(func):
    """装饰器：验证用户名参数"""

    def wrapper(username: str, *args, **kwargs):
        valid, error = validate_username(username)
        if not valid:
            raise DataValidationError(f"用户名验证失败: {error}")
        # 使用清理后的用户名
        username = sanitize_username(username)
        return func(username, *args, **kwargs)

    return wrapper


def validate_count_arg(func):
    """装饰器：验证数量参数"""

    def wrapper(*args, **kwargs):
        # 假设 count 是第二个参数
        if len(args) >= 2:
            count = args[1]
            valid, error = validate_tweet_count(count)
            if not valid:
                raise DataValidationError(f"数量验证失败: {error}")
        return func(*args, **kwargs)

    return wrapper
