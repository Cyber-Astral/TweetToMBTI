"""
集中配置管理
所有配置项的单一来源
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class APIConfig:
    """API 配置"""
    gemini_api_key: str
    apify_api_token: str
    apify_actor_id: str = "apidojo/tweet-scraper"


@dataclass
class ScraperConfig:
    """爬虫配置"""
    default_max_tweets: int = 100
    max_tweets_per_request: int = 300
    timeout_seconds: int = 120
    retry_attempts: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0


@dataclass
class AnalyzerConfig:
    """分析器配置"""
    model_name: str = "gemini-2.5-flash"
    original_tweets_count: int = 100
    reply_tweets_count: int = 100
    min_tweets_required: int = 10
    max_tweet_length: int = 200
    analysis_timeout: int = 30


@dataclass
class RateLimitConfig:
    """限流配置"""
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_requests_per_day: int = 10000
    
    # Gemini 特定限流
    gemini_requests_per_minute: int = 60
    gemini_requests_per_day: int = 1500


@dataclass
class StorageConfig:
    """存储配置"""
    project_root: Path
    data_dir: Path
    reports_dir: Path
    images_dir: Path
    logs_dir: Path
    
    def __post_init__(self):
        """确保目录存在"""
        for dir_path in [self.data_dir, self.reports_dir, self.images_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class DisplayConfig:
    """显示配置"""
    terminal_width: int = 60
    progress_bar_length: int = 20
    percentage_decimal_places: int = 1
    
    # MBTI 报告配置
    mbti_bar_length: int = 20
    mbti_bar_fill_char: str = "█"
    mbti_bar_empty_char: str = "░"


@dataclass
class ValidationConfig:
    """验证配置"""
    min_username_length: int = 1
    max_username_length: int = 15
    max_tweet_count: int = 1000
    max_filename_length: int = 200
    
    # API 密钥格式
    gemini_key_prefix: str = "AIza"
    gemini_key_min_length: int = 39
    apify_token_prefix: str = "apify_api_"
    apify_token_min_length: int = 48


class Config:
    """主配置类"""
    
    def __init__(self):
        # 路径配置
        project_root = Path(__file__).parent.parent
        
        # 初始化各个配置
        self.api = APIConfig(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            apify_api_token=os.getenv("APIFY_API_TOKEN", ""),
            apify_actor_id=os.getenv("APIFY_ACTOR_ID", "apidojo/tweet-scraper")
        )
        
        self.scraper = ScraperConfig(
            default_max_tweets=int(os.getenv("DEFAULT_MAX_TWEETS", "100")),
            max_tweets_per_request=int(os.getenv("MAX_TWEETS_PER_REQUEST", "300")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "120")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
            backoff_factor=float(os.getenv("BACKOFF_FACTOR", "2.0"))
        )
        
        self.analyzer = AnalyzerConfig(
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            original_tweets_count=int(os.getenv("ORIGINAL_TWEETS_COUNT", "100")),
            reply_tweets_count=int(os.getenv("REPLY_TWEETS_COUNT", "100")),
            min_tweets_required=int(os.getenv("MIN_TWEETS_REQUIRED", "10")),
            max_tweet_length=int(os.getenv("MAX_TWEET_LENGTH", "200")),
            analysis_timeout=int(os.getenv("ANALYSIS_TIMEOUT", "30"))
        )
        
        self.rate_limit = RateLimitConfig(
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")),
            max_requests_per_hour=int(os.getenv("MAX_REQUESTS_PER_HOUR", "1000")),
            max_requests_per_day=int(os.getenv("MAX_REQUESTS_PER_DAY", "10000")),
            gemini_requests_per_minute=int(os.getenv("GEMINI_REQUESTS_PER_MINUTE", "60")),
            gemini_requests_per_day=int(os.getenv("GEMINI_REQUESTS_PER_DAY", "1500"))
        )
        
        self.storage = StorageConfig(
            project_root=project_root,
            data_dir=project_root / "data",
            reports_dir=project_root / "mbti_analyzer" / "reports",
            images_dir=project_root / "mbti_analyzer" / "images",
            logs_dir=project_root / "logs"
        )
        
        self.display = DisplayConfig(
            terminal_width=int(os.getenv("TERMINAL_WIDTH", "60")),
            progress_bar_length=int(os.getenv("PROGRESS_BAR_LENGTH", "20")),
            percentage_decimal_places=int(os.getenv("PERCENTAGE_DECIMAL_PLACES", "1")),
            mbti_bar_length=int(os.getenv("MBTI_BAR_LENGTH", "20")),
            mbti_bar_fill_char=os.getenv("MBTI_BAR_FILL_CHAR", "█"),
            mbti_bar_empty_char=os.getenv("MBTI_BAR_EMPTY_CHAR", "░")
        )
        
        self.validation = ValidationConfig(
            min_username_length=int(os.getenv("MIN_USERNAME_LENGTH", "1")),
            max_username_length=int(os.getenv("MAX_USERNAME_LENGTH", "15")),
            max_tweet_count=int(os.getenv("MAX_TWEET_COUNT", "1000")),
            max_filename_length=int(os.getenv("MAX_FILENAME_LENGTH", "200"))
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        验证配置的有效性
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 验证 API 密钥
        if not self.api.gemini_api_key:
            errors.append("GEMINI_API_KEY 未设置")
        elif not self.api.gemini_api_key.startswith(self.validation.gemini_key_prefix):
            errors.append("GEMINI_API_KEY 格式不正确")
        elif len(self.api.gemini_api_key) < self.validation.gemini_key_min_length:
            errors.append("GEMINI_API_KEY 长度不正确")
        
        if not self.api.apify_api_token:
            errors.append("APIFY_API_TOKEN 未设置")
        elif not self.api.apify_api_token.startswith(self.validation.apify_token_prefix):
            errors.append("APIFY_API_TOKEN 格式不正确")
        elif len(self.api.apify_api_token) < self.validation.apify_token_min_length:
            errors.append("APIFY_API_TOKEN 长度不正确")
        
        # 验证数值配置
        if self.scraper.default_max_tweets <= 0:
            errors.append("default_max_tweets 必须大于 0")
        
        if self.scraper.timeout_seconds <= 0:
            errors.append("timeout_seconds 必须大于 0")
        
        if self.scraper.retry_attempts < 0:
            errors.append("retry_attempts 不能为负数")
        
        if self.rate_limit.max_requests_per_minute <= 0:
            errors.append("max_requests_per_minute 必须大于 0")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "api": {
                "gemini_api_key": "***" if self.api.gemini_api_key else "",
                "apify_api_token": "***" if self.api.apify_api_token else "",
                "apify_actor_id": self.api.apify_actor_id
            },
            "scraper": self.scraper.__dict__,
            "analyzer": self.analyzer.__dict__,
            "rate_limit": self.rate_limit.__dict__,
            "storage": {
                "project_root": str(self.storage.project_root),
                "data_dir": str(self.storage.data_dir),
                "reports_dir": str(self.storage.reports_dir),
                "images_dir": str(self.storage.images_dir),
                "logs_dir": str(self.storage.logs_dir)
            },
            "display": self.display.__dict__,
            "validation": self.validation.__dict__
        }
    
    def get_scraper_config_dict(self) -> Dict[str, str]:
        """获取 scraper 兼容的配置字典"""
        return {
            "api_token": self.api.apify_api_token,
            "actor_id": self.api.apify_actor_id
        }


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """重新加载配置"""
    global _config
    load_dotenv(override=True)
    _config = Config()
    return _config