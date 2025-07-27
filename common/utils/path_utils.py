"""
路径管理工具
提供项目路径的统一管理
"""

import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        项目根目录的 Path 对象
    """
    # 从当前文件位置向上查找，直到找到包含特定标志文件的目录
    current = Path(__file__).resolve()

    # 向上查找直到找到项目根目录（包含 requirements.txt 或 .git）
    for parent in current.parents:
        if (parent / "requirements.txt").exists() or (parent / ".git").exists():
            return parent

    # 如果找不到，返回当前文件的祖父目录作为默认值
    return current.parent.parent


def add_project_to_path():
    """
    将项目根目录添加到 Python 路径
    这样可以从项目任何位置导入模块
    """
    project_root = str(get_project_root())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


# 项目目录常量
PROJECT_ROOT = get_project_root()
SCRAPER_DIR = PROJECT_ROOT / "scraper"
MBTI_DIR = PROJECT_ROOT / "mbti_analyzer"
COMMON_DIR = PROJECT_ROOT / "common"

# 数据目录
DATA_DIR = SCRAPER_DIR / "scraped_data"
USER_TWEETS_DIR = DATA_DIR / "user_tweets"
REPORTS_DIR = MBTI_DIR / "reports"
IMAGES_DIR = MBTI_DIR / "images"

# 确保必要的目录存在
for directory in [DATA_DIR, USER_TWEETS_DIR, REPORTS_DIR, IMAGES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
