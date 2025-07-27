#!/usr/bin/env python
"""
MBTI 人格分析器命令行工具 - 兼容性脚本
基于Twitter推文分析用户的MBTI人格类型

使用方法: python analyze_mbti.py <username>

注意: 此脚本已整合到 cli.py
推荐使用: python cli.py analyze <username> [options]
"""

import subprocess
import sys

if __name__ == "__main__":
    # 将参数转发到新的 CLI
    args = ["python", "cli.py", "analyze"] + sys.argv[1:]
    sys.exit(subprocess.call(args))