"""
配置验证工具
"""

import os
import sys
from typing import Dict, List, Tuple

from config.settings import get_config


def validate_environment() -> Tuple[bool, List[str]]:
    """
    验证环境配置
    
    Returns:
        (是否有效, 错误列表)
    """
    errors = []
    warnings = []
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        errors.append(f"Python 版本太低: {sys.version}，需要 3.8+")
    
    # 检查必要的环境变量
    required_env_vars = [
        "GEMINI_API_KEY",
        "APIFY_API_TOKEN"
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"环境变量 {var} 未设置")
    
    # 检查可选的环境变量
    optional_env_vars = [
        "DEFAULT_MAX_TWEETS",
        "TIMEOUT_SECONDS",
        "RETRY_ATTEMPTS"
    ]
    
    for var in optional_env_vars:
        value = os.getenv(var)
        if value:
            try:
                int(value)
            except ValueError:
                warnings.append(f"环境变量 {var} 应该是整数: {value}")
    
    return len(errors) == 0, errors, warnings


def validate_config(config=None) -> Tuple[bool, List[str], List[str]]:
    """
    验证配置对象
    
    Args:
        config: 配置对象（如果为 None，使用全局配置）
        
    Returns:
        (是否有效, 错误列表, 警告列表)
    """
    if config is None:
        config = get_config()
    
    errors = []
    warnings = []
    
    # 使用配置自带的验证
    valid, config_errors = config.validate()
    errors.extend(config_errors)
    
    # 额外的验证逻辑
    
    # 检查路径是否可写
    try:
        test_file = config.storage.data_dir / ".test_write"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        errors.append(f"数据目录不可写: {config.storage.data_dir} - {e}")
    
    # 检查限流配置的合理性
    if config.rate_limit.max_requests_per_minute > config.rate_limit.max_requests_per_hour / 60:
        warnings.append("每分钟请求数超过了每小时平均值")
    
    if config.rate_limit.max_requests_per_hour > config.rate_limit.max_requests_per_day / 24:
        warnings.append("每小时请求数超过了每天平均值")
    
    # 检查爬虫配置的合理性
    if config.scraper.default_max_tweets > config.validation.max_tweet_count:
        warnings.append(
            f"默认推文数 ({config.scraper.default_max_tweets}) "
            f"超过了最大限制 ({config.validation.max_tweet_count})"
        )
    
    if config.scraper.retry_delay * (2 ** config.scraper.retry_attempts) > 300:
        warnings.append("重试延迟可能过长（超过 5 分钟）")
    
    # 检查分析器配置
    if config.analyzer.original_tweets_count + config.analyzer.reply_tweets_count > 500:
        warnings.append("分析推文总数较多，可能导致 API 成本增加")
    
    return len(errors) == 0, errors, warnings


def print_config_status(verbose: bool = False):
    """
    打印配置状态
    
    Args:
        verbose: 是否显示详细信息
    """
    print("=" * 60)
    print("配置验证报告")
    print("=" * 60)
    
    # 验证环境
    env_valid, env_errors, env_warnings = validate_environment()
    
    if env_errors:
        print("\n❌ 环境错误:")
        for error in env_errors:
            print(f"  - {error}")
    else:
        print("\n✅ 环境配置正常")
    
    if env_warnings:
        print("\n⚠️  环境警告:")
        for warning in env_warnings:
            print(f"  - {warning}")
    
    # 验证配置
    config = get_config()
    config_valid, config_errors, config_warnings = validate_config(config)
    
    if config_errors:
        print("\n❌ 配置错误:")
        for error in config_errors:
            print(f"  - {error}")
    else:
        print("\n✅ 配置验证通过")
    
    if config_warnings:
        print("\n⚠️  配置警告:")
        for warning in config_warnings:
            print(f"  - {warning}")
    
    # 显示配置摘要
    if verbose:
        print("\n📋 配置摘要:")
        print(f"  - API 密钥已配置: {'是' if config.api.gemini_api_key else '否'}")
        print(f"  - 默认抓取数量: {config.scraper.default_max_tweets}")
        print(f"  - 重试次数: {config.scraper.retry_attempts}")
        print(f"  - 限流设置: {config.rate_limit.max_requests_per_minute}/分钟")
        print(f"  - 数据目录: {config.storage.data_dir}")
        print(f"  - 报告目录: {config.storage.reports_dir}")
    
    print("\n" + "=" * 60)
    
    # 返回总体状态
    all_valid = env_valid and config_valid
    return all_valid


def create_config_template():
    """创建配置模板文件"""
    template = """# TweetToMBTI 配置文件
# 复制此文件为 .env 并填入实际值

# API 密钥（必需）
GEMINI_API_KEY=your_gemini_api_key_here
APIFY_API_TOKEN=your_apify_api_token_here

# API 配置（可选）
APIFY_ACTOR_ID=apidojo/tweet-scraper
GEMINI_MODEL=gemini-2.5-flash

# 爬虫配置（可选）
DEFAULT_MAX_TWEETS=100
MAX_TWEETS_PER_REQUEST=300
TIMEOUT_SECONDS=120
RETRY_ATTEMPTS=3
RETRY_DELAY=1.0
BACKOFF_FACTOR=2.0

# 分析器配置（可选）
ORIGINAL_TWEETS_COUNT=100
REPLY_TWEETS_COUNT=100
MIN_TWEETS_REQUIRED=10
MAX_TWEET_LENGTH=200
ANALYSIS_TIMEOUT=30

# 限流配置（可选）
MAX_REQUESTS_PER_MINUTE=60
MAX_REQUESTS_PER_HOUR=1000
MAX_REQUESTS_PER_DAY=10000
GEMINI_REQUESTS_PER_MINUTE=60
GEMINI_REQUESTS_PER_DAY=1500

# 显示配置（可选）
TERMINAL_WIDTH=60
PROGRESS_BAR_LENGTH=20
PERCENTAGE_DECIMAL_PLACES=1
MBTI_BAR_LENGTH=20
MBTI_BAR_FILL_CHAR=█
MBTI_BAR_EMPTY_CHAR=░

# 验证配置（可选）
MIN_USERNAME_LENGTH=1
MAX_USERNAME_LENGTH=15
MAX_TWEET_COUNT=1000
MAX_FILENAME_LENGTH=200
"""
    
    env_example_path = ".env.example"
    with open(env_example_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"✅ 配置模板已创建: {env_example_path}")
    print("请复制为 .env 并填入实际的 API 密钥")


if __name__ == "__main__":
    # 命令行工具
    import argparse
    
    parser = argparse.ArgumentParser(description="配置验证工具")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("-t", "--template", action="store_true", help="创建配置模板")
    
    args = parser.parse_args()
    
    if args.template:
        create_config_template()
    else:
        valid = print_config_status(verbose=args.verbose)
        sys.exit(0 if valid else 1)