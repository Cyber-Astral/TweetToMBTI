#!/usr/bin/env python
"""
命令行抓取工具 - 兼容性脚本
使用方法: python scrape.py <username> [count]

注意: 此脚本已整合到 cli.py
推荐使用: python cli.py scrape <username> [count]
"""

import subprocess
import sys

if __name__ == "__main__":
    # 将参数转发到新的 CLI
    args = ["python", "cli.py", "scrape"] + sys.argv[1:]
    sys.exit(subprocess.call(args))
