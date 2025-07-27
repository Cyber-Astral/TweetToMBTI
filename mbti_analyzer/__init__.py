"""
MBTI 人格分析器包
基于推文内容分析用户的MBTI人格类型
"""

import os

from dotenv import load_dotenv

from .analyzer import collect_tweet_data
from .gemini_api import GeminiAnalyzer
from .report_generator import ReportGenerator

# 加载环境变量
load_dotenv()


def analyze_user_mbti(username: str) -> tuple:
    """
    分析用户MBTI的主函数

    Args:
        username: Twitter用户名（不带@）

    Returns:
        tuple: (报告路径, 图片路径, 分析结果)
    """
    # 1. 收集推文数据
    print(f"[1/4] 正在收集 @{username} 的推文数据...")
    tweet_data = collect_tweet_data(username)

    if not tweet_data["original_tweets"] and not tweet_data["reply_tweets"]:
        raise ValueError(f"未能获取用户 @{username} 的推文数据")

    print(f"    ✓ 收集到 {len(tweet_data['original_tweets'])} 条原创推文")
    print(f"    ✓ 收集到 {len(tweet_data['reply_tweets'])} 条回复推文")

    # 2. 调用Gemini分析
    print("[2/4] 正在进行AI人格分析...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("请设置 GEMINI_API_KEY 环境变量")

    analyzer = GeminiAnalyzer(api_key)
    mbti_result = analyzer.analyze_mbti(tweet_data)
    print(f"    ✓ 分析结果：{mbti_result['mbti_type']}")

    # 3. 生成报告
    print("[3/4] 正在生成HTML报告...")
    generator = ReportGenerator()
    report_path = generator.generate(
        username,
        mbti_result,
        stats=tweet_data.get("stats"),
        display_name=tweet_data.get("display_name"),
    )

    # 4. 完成
    print("[4/4] 分析完成！")
    
    # 返回报告路径、图片路径（None，因为还没生成）和分析结果
    return report_path, None, mbti_result


__all__ = ["analyze_user_mbti", "collect_tweet_data", "GeminiAnalyzer", "ReportGenerator"]
