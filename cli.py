#!/usr/bin/env python
"""
统一的命令行接口入口
整合所有功能到一个CLI工具
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def cmd_scrape(args):
    """抓取推文命令"""
    from scraper import save_user_tweets, scrape_user_tweets
    
    print(f"抓取 @{args.username} 的 {args.count} 条推文...")
    tweets = scrape_user_tweets(args.username, args.count)
    
    if tweets:
        saved = save_user_tweets(args.username, tweets)
        print(f"✓ 成功抓取 {len(tweets)} 条推文")
        print(f"✓ 已保存到 {saved['json']}")
    else:
        print("✗ 未找到推文")


def cmd_analyze(args):
    """MBTI分析命令"""
    import webbrowser
    from common.exceptions import (
        APIError,
        EmptyResponseError,
        NoTweetsError,
        RateLimitError,
        UserNotFoundError,
    )
    from common.logger import get_module_logger
    from common.validators import sanitize_username, validate_username
    from mbti_analyzer import analyze_user_mbti
    from mbti_analyzer.html_to_image import convert_html_to_image
    
    logger = get_module_logger("cli.analyze")
    
    # 验证用户名
    username = args.username.replace("@", "")
    valid, error = validate_username(username)
    if not valid:
        print(f"错误: {error}")
        logger.error(f"用户名验证失败: {username} - {error}")
        sys.exit(1)
    
    username = sanitize_username(username)
    
    print(f"\n{'='*60}")
    print(f" MBTI 人格分析器 - 分析目标: @{username}")
    print(f"{'='*60}\n")
    
    logger.info(f"开始分析用户: {username}")
    
    try:
        # 执行分析
        report_path, image_path, result = analyze_user_mbti(username)
        
        print(f"\n✓ 分析完成!")
        print(f"  MBTI 类型: {result.get('mbti_type', 'Unknown')}")
        
        # 计算整体置信度（各维度平均值）
        if 'dimensions' in result:
            confidences = []
            for dim in result['dimensions'].values():
                if 'percentage' in dim:
                    confidences.append(dim['percentage'])
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"  置信度: {avg_confidence:.1f}%")
        print(f"\n📄 报告已保存: {report_path}")
        
        # 如果指定了保存图片
        if args.save_image:
            try:
                print("📸 正在生成图片...")
                img_path = convert_html_to_image(report_path)
                print(f"✓ 图片已保存: {img_path}")
            except Exception as e:
                print(f"✗ 图片生成失败: {e}")
                logger.error(f"图片生成失败: {e}")
        
        # 询问是否打开报告
        if not args.no_interactive:
            response = input("\n是否在浏览器中查看报告? (y/n): ")
            if response.lower() in ["y", "yes", ""]:
                webbrowser.open(f"file://{report_path}")
                print("✓ 已在浏览器中打开报告")
    
    except UserNotFoundError:
        print(f"\n✗ 错误: 用户 @{username} 不存在或已被封禁")
        logger.error(f"用户不存在: {username}")
        sys.exit(1)
    except NoTweetsError:
        print(f"\n✗ 错误: 用户 @{username} 没有足够的推文进行分析")
        logger.error(f"推文不足: {username}")
        sys.exit(1)
    except RateLimitError as e:
        print(f"\n✗ 错误: API 限流 - {e}")
        logger.error(f"API限流: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"\n✗ 错误: API 调用失败 - {e}")
        logger.error(f"API错误: {e}")
        sys.exit(1)
    except EmptyResponseError:
        print("\n✗ 错误: AI 分析返回空结果，请稍后重试")
        logger.error("AI分析返回空结果")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 未知错误: {e}")
        logger.exception("未知错误")
        sys.exit(1)


def cmd_stats(args):
    """MBTI统计命令"""
    import glob
    import re
    from collections import Counter
    from common.calculations import (
        calculate_percentage,
        calculate_percentage_bar,
        format_percentage_display,
    )
    from config import get_config
    
    # 使用配置获取报告目录
    config = get_config()
    reports_pattern = str(config.storage.reports_dir / "*.html")
    reports = glob.glob(reports_pattern)
    
    mbti_types = []
    users = {}
    
    for report in reports:
        # 提取用户名和MBTI类型
        filename = report.split("/")[-1]
        username_match = re.search(r"mbti_report_(.+?)_\d+", filename)
        if username_match:
            username = username_match.group(1)
            
            with open(report, "r", encoding="utf-8") as f:
                content = f.read()
                mbti_match = re.search(r"分析结论:.*?([A-Z]{4})", content)
                if mbti_match:
                    mbti_type = mbti_match.group(1)
                    mbti_types.append(mbti_type)
                    users[username] = mbti_type
    
    # 统计分析
    type_count = Counter(mbti_types)
    total = len(mbti_types)
    
    print("=== MBTI 类型分布统计 ===")
    print(f"总测试人数: {total}")
    print(f"不同用户数: {len(set(users.keys()))}")
    print("\n各类型分布:")
    print("-" * 30)
    
    # 按数量排序输出
    for mbti_type, count in type_count.most_common():
        percentage = calculate_percentage(count, total)
        bar = calculate_percentage_bar(percentage, bar_length=30)
        print(f"{mbti_type}: {count:3d} {format_percentage_display(percentage, include_bar=True, bar_length=30)}")
    
    # 维度统计
    print("\n各维度分布:")
    print("-" * 30)
    
    dimensions = {"E/I": Counter(), "S/N": Counter(), "T/F": Counter(), "J/P": Counter()}
    
    for mbti in mbti_types:
        dimensions["E/I"][mbti[0]] += 1
        dimensions["S/N"][mbti[1]] += 1
        dimensions["T/F"][mbti[2]] += 1
        dimensions["J/P"][mbti[3]] += 1
    
    for dim, counts in dimensions.items():
        print(f"\n{dim}:")
        for letter, count in sorted(counts.items()):
            percentage = calculate_percentage(count, total)
            display = format_percentage_display(percentage, include_bar=False)
            print(f"  {letter}: {count:3d} {display}")
    
    # 最常见的组合
    print("\n最常见的类型组合:")
    print("-" * 30)
    for mbti_type, count in type_count.most_common(5):
        print(f"{mbti_type}: {count} 人")


def cmd_today_stats(args):
    """今日MBTI统计命令"""
    import glob
    import re
    from collections import Counter
    from datetime import datetime
    from common.calculations import calculate_percentage, format_percentage_display
    from config import get_config
    
    # 获取今天的日期
    today = datetime.now().strftime("%Y%m%d")
    
    # 使用配置获取报告目录
    config = get_config()
    reports_pattern = str(config.storage.reports_dir / f"*_{today}_*.html")
    reports = glob.glob(reports_pattern)
    
    mbti_types = []
    users = []
    
    for report in reports:
        # 提取用户名和MBTI类型
        filename = report.split("/")[-1]
        username_match = re.search(r"mbti_report_(.+?)_\d+", filename)
        if username_match:
            username = username_match.group(1)
            users.append(username)
            
            with open(report, "r", encoding="utf-8") as f:
                content = f.read()
                mbti_match = re.search(r"分析结论:.*?([A-Z]{4})", content)
                if mbti_match:
                    mbti_type = mbti_match.group(1)
                    mbti_types.append(mbti_type)
    
    # 统计分析
    type_count = Counter(mbti_types)
    total = len(mbti_types)
    
    print(f"=== 今日 MBTI 分析统计 ({today}) ===")
    print(f"分析人数: {total}")
    
    if total == 0:
        print("\n今天还没有进行任何分析")
        return
    
    print("\n今日用户:")
    for user in sorted(set(users)):
        print(f"  @{user}")
    
    print("\n类型分布:")
    print("-" * 30)
    
    # 按数量排序输出
    for mbti_type, count in type_count.most_common():
        percentage = calculate_percentage(count, total)
        display = format_percentage_display(percentage, include_bar=True, bar_length=20)
        print(f"{mbti_type}: {count:2d} {display}")
    
    # 维度偏好
    print("\n维度偏好:")
    print("-" * 30)
    
    dimensions = {"E/I": Counter(), "S/N": Counter(), "T/F": Counter(), "J/P": Counter()}
    
    for mbti in mbti_types:
        dimensions["E/I"][mbti[0]] += 1
        dimensions["S/N"][mbti[1]] += 1
        dimensions["T/F"][mbti[2]] += 1
        dimensions["J/P"][mbti[3]] += 1
    
    for dim, counts in dimensions.items():
        parts = []
        for letter in sorted(counts.keys()):
            count = counts[letter]
            percentage = calculate_percentage(count, total)
            parts.append(f"{letter}:{percentage:.0f}%")
        print(f"{dim}: {' vs '.join(parts)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="TweetToMBTI",
        description="基于推文分析 MBTI 人格类型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s scrape elonmusk                    # 抓取推文
  %(prog)s analyze taylorswift13              # 分析MBTI
  %(prog)s analyze @naval --save-image        # 分析并保存图片
  %(prog)s stats                              # 查看所有统计
  %(prog)s today-stats                        # 查看今日统计
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # scrape 命令
    parser_scrape = subparsers.add_parser("scrape", help="抓取用户推文")
    parser_scrape.add_argument("username", help="Twitter用户名")
    parser_scrape.add_argument("count", type=int, nargs="?", default=100, 
                              help="抓取数量 (默认: 100)")
    
    # analyze 命令
    parser_analyze = subparsers.add_parser("analyze", help="分析用户MBTI类型")
    parser_analyze.add_argument("username", help="Twitter用户名")
    parser_analyze.add_argument("--no-interactive", action="store_true",
                               help="跳过交互式提示")
    parser_analyze.add_argument("--save-image", action="store_true",
                               help="将报告保存为图片")
    
    # stats 命令
    parser_stats = subparsers.add_parser("stats", help="查看MBTI统计数据")
    
    # today-stats 命令
    parser_today = subparsers.add_parser("today-stats", help="查看今日MBTI统计")
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行对应命令
    commands = {
        "scrape": cmd_scrape,
        "analyze": cmd_analyze,
        "stats": cmd_stats,
        "today-stats": cmd_today_stats,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()