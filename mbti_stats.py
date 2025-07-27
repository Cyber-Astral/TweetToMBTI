#!/usr/bin/env python
"""
MBTI 统计分析脚本 - 兼容性脚本

注意: 此脚本已整合到 cli.py
推荐使用: python cli.py stats
"""

import subprocess
import sys

if __name__ == "__main__":
    # 将参数转发到新的 CLI
    args = ["python", "cli.py", "stats"]
    sys.exit(subprocess.call(args))