"""
验证器模块的单元测试
"""

import pytest

from common.validators import (
    sanitize_filename,
    sanitize_username,
    validate_api_key,
    validate_file_path,
    validate_tweet_count,
    validate_username,
)


class TestUsernameValidation:
    """用户名验证测试"""

    def test_valid_usernames(self):
        """测试有效的用户名"""
        valid_usernames = [
            "elonmusk",
            "user123",
            "test_user",
            "_underscore",
            "a",  # 最短
            "abcdefghijklmno",  # 15字符
        ]

        for username in valid_usernames:
            valid, error = validate_username(username)
            assert valid is True, f"用户名 '{username}' 应该是有效的"
            assert error is None

    def test_invalid_usernames(self):
        """测试无效的用户名"""
        invalid_cases = [
            ("", "用户名不能为空"),
            ("abcdefghijklmnop", "用户名长度必须在 1-15 个字符之间"),  # 16字符
            ("user-name", "用户名只能包含字母、数字和下划线"),
            ("user@name", "用户名只能包含字母、数字和下划线"),
            ("user name", "用户名只能包含字母、数字和下划线"),
            ("123456", "用户名不能全是数字"),
        ]

        for username, expected_error in invalid_cases:
            valid, error = validate_username(username)
            assert valid is False, f"用户名 '{username}' 应该是无效的"
            assert error == expected_error

    def test_username_with_at_symbol(self):
        """测试带 @ 符号的用户名"""
        # validate_username 会自动移除 @ 前缀
        valid, error = validate_username("@username")
        assert valid is True  # 移除 @ 后是有效的
        assert error is None

        # 但如果 @ 在中间，则无效
        valid, error = validate_username("user@name")
        assert valid is False
        assert "只能包含字母、数字和下划线" in error


class TestTweetCountValidation:
    """推文数量验证测试"""

    def test_valid_counts(self):
        """测试有效的数量"""
        valid_counts = [1, 10, 100, 500, 1000]

        for count in valid_counts:
            valid, error = validate_tweet_count(count)
            assert valid is True
            assert error is None

    def test_invalid_counts(self):
        """测试无效的数量"""
        invalid_cases = [
            (0, "推文数量必须大于 0"),
            (-1, "推文数量必须大于 0"),
            (1001, "推文数量不能超过 1000（API 限制）"),
            ("100", "推文数量必须是整数"),
            (100.5, "推文数量必须是整数"),
        ]

        for count, expected_error in invalid_cases:
            valid, error = validate_tweet_count(count)
            assert valid is False
            assert error == expected_error


class TestAPIKeyValidation:
    """API 密钥验证测试"""

    def test_gemini_api_key(self):
        """测试 Gemini API 密钥验证"""
        # 有效的 Gemini key
        valid_key = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        valid, error = validate_api_key(valid_key, "gemini")
        assert valid is True
        assert error is None

        # 无效的 Gemini key
        invalid_cases = [
            ("", "API 密钥不能为空"),
            ("invalid", "Gemini API 密钥格式不正确"),
            ("AIza", "Gemini API 密钥长度不正确"),
            ("AIzaSy@#$%", "Gemini API 密钥长度不正确"),  # 长度检查优先于字符检查
        ]

        for key, expected_error in invalid_cases:
            valid, error = validate_api_key(key, "gemini")
            assert valid is False
            assert error == expected_error

    def test_apify_api_token(self):
        """测试 Apify API token 验证"""
        # 有效的 Apify token (48个字符)
        valid_token = "apify_api_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX1234"
        valid, error = validate_api_key(valid_token, "apify")
        assert valid is True
        assert error is None

        # 无效的 Apify token
        invalid_cases = [
            ("", "API 密钥不能为空"),
            ("invalid", "Apify API token 格式不正确"),
            ("apify_api_", "Apify API token 长度不正确"),
        ]

        for token, expected_error in invalid_cases:
            valid, error = validate_api_key(token, "apify")
            assert valid is False
            assert error == expected_error


class TestSanitization:
    """数据清理测试"""

    def test_sanitize_username(self):
        """测试用户名清理"""
        test_cases = [
            ("@username", "username"),
            ("  USERNAME  ", "username"),
            ("User_Name", "user_name"),
            ("user123", "user123"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_username(input_name)
            assert result == expected

    def test_sanitize_filename(self):
        """测试文件名清理"""
        test_cases = [
            ("file<name>.txt", "file_name_.txt"),
            ("file:name|test", "file_name_test"),
            ("a" * 250 + ".txt", "a" * 196 + ".txt"),  # 长度限制
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected


class TestFilePathValidation:
    """文件路径验证测试"""

    def test_valid_paths(self):
        """测试有效的路径"""
        valid_paths = [
            "/home/user/file.txt",
            "relative/path/file.txt",
            "file.txt",
        ]

        for path in valid_paths:
            valid, error = validate_file_path(path)
            assert valid is True
            assert error is None

    def test_dangerous_paths(self):
        """测试危险的路径"""
        dangerous_paths = [
            "../../../etc/passwd",
            "~/sensitive/file",
            "${HOME}/file",
            "%(HOME)s/file",
        ]

        for path in dangerous_paths:
            valid, error = validate_file_path(path)
            assert valid is False
            assert "危险字符" in error
