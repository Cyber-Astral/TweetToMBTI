"""
HTML报告生成器
负责生成终端风格的MBTI分析报告
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from jinja2 import Environment, FileSystemLoader

from common.calculations import calculate_percentage
from config import get_config


class ReportGenerator:
    """HTML报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        config = get_config()
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.reports_dir = str(config.storage.reports_dir)
        self.config = config
        
        # 确保报告目录存在
        os.makedirs(self.reports_dir, exist_ok=True)

        # 设置Jinja2环境
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.env.filters["mbti_dimension_name"] = self._mbti_dimension_name
        self.env.globals["progress_bar"] = self._progress_bar

    def generate(
        self, username: str, mbti_result: Dict, stats: Dict = None, display_name: str = None
    ) -> str:
        """
        生成HTML报告

        Args:
            username: Twitter用户名
            mbti_result: MBTI分析结果
            stats: 统计信息
            display_name: 用户显示名称

        Returns:
            生成的HTML文件路径
        """
        # 加载模板
        template = self.env.get_template("terminal_report.html")

        # 准备模板数据
        context = {
            "username": username,
            "display_name": display_name or "",
            "mbti_type": mbti_result["mbti_type"],
            "mbti_description": self._get_mbti_description(mbti_result["mbti_type"]),
            "dimensions": mbti_result["dimensions"],
            "overall_analysis": mbti_result.get("overall_analysis", ""),
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ascii_art": self._get_mbti_ascii_art(mbti_result["mbti_type"]),
            "stats": stats or {"total_original": 0, "total_replies": 0},
        }

        # 渲染HTML
        html_content = template.render(**context)

        # 保存报告
        filename = f"mbti_report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = os.path.join(self.reports_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def _mbti_dimension_name(self, dimension_type: str, dimension: str) -> str:
        """
        获取MBTI维度的中文名称

        Args:
            dimension_type: 维度类型（E/I/S/N/T/F/J/P）
            dimension: 维度名称（E_I/S_N/T_F/J_P）

        Returns:
            中文名称
        """
        names = {
            "E_I": {"E": "外向 (Extraversion)", "I": "内向 (Introversion)"},
            "S_N": {"S": "感觉 (Sensing)", "N": "直觉 (Intuition)"},
            "T_F": {"T": "思考 (Thinking)", "F": "情感 (Feeling)"},
            "J_P": {"J": "判断 (Judging)", "P": "感知 (Perceiving)"},
        }
        return names.get(dimension, {}).get(dimension_type, dimension_type)

    def _progress_bar(self, percentage: int, dimension_type: str, dimension: str) -> str:
        """
        生成进度条

        Args:
            percentage: 百分比（50-100）
            dimension_type: 当前维度类型（E/I/S/N/T/F/J/P）
            dimension: 维度名称（E_I/S_N/T_F/J_P）

        Returns:
            进度条字符串
        """
        # 使用配置的进度条长度
        total_length = 10
        
        # 直接将百分比转换为星号数量
        # 80% = 8个星号，70% = 7个星号
        filled = round(percentage * total_length / 100)
        filled = max(0, min(filled, total_length))  # 确保在0-10范围内

        # 生成进度条
        return "*" * filled + "-" * (total_length - filled)

    def _get_mbti_description(self, mbti_type: str) -> str:
        """
        获取MBTI类型的描述

        Args:
            mbti_type: MBTI类型

        Returns:
            类型描述
        """
        descriptions = {
            "INTJ": "建筑师 - 富有想象力的战略思想家",
            "INTP": "逻辑学家 - 创新的发明家",
            "ENTJ": "指挥官 - 大胆、有想象力的领导者",
            "ENTP": "辩论家 - 聪明好奇的思想家",
            "INFJ": "提倡者 - 安静而神秘的理想主义者",
            "INFP": "调停者 - 诗意、善良的利他主义者",
            "ENFJ": "主人公 - 有魅力、鼓舞人心的领导者",
            "ENFP": "竞选者 - 热情、有创造力的自由精神",
            "ISTJ": "物流师 - 实际、注重事实的管理者",
            "ISFJ": "守卫者 - 专注、热心的保护者",
            "ESTJ": "总经理 - 出色的管理者",
            "ESFJ": "执政官 - 关怀他人、受欢迎的助人者",
            "ISTP": "鉴赏家 - 大胆实际的实验家",
            "ISFP": "探险家 - 灵活有魅力的艺术家",
            "ESTP": "企业家 - 聪明、精力充沛的感知者",
            "ESFP": "表演者 - 自发、精力充沛的享乐者",
        }
        return descriptions.get(mbti_type, "独特的人格类型")

    def _get_mbti_ascii_art(self, mbti_type: str) -> str:
        """
        根据MBTI类型返回对应的ASCII艺术

        Args:
            mbti_type: MBTI类型

        Returns:
            ASCII艺术字符串
        """
        # 生成大字的 MBTI 类型
        mbti_upper = mbti_type.upper()

        # 根据4个字母生成ASCII艺术
        art_map = {
            "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
            "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
            "N": [
                "███╗   ██╗",
                "████╗  ██║",
                "██╔██╗ ██║",
                "██║╚██╗██║",
                "██║ ╚████║",
                "╚═╝  ╚═══╝",
            ],
            "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
            "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
            "F": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "██║     ", "╚═╝     "],
            "J": ["     ██╗", "     ██║", "     ██║", "██   ██║", "╚█████╔╝", " ╚════╝ "],
            "P": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔═══╝ ", "██║     ", "╚═╝     "],
        }

        lines = [""] * 6
        for letter in mbti_upper:
            if letter in art_map:
                for i in range(6):
                    lines[i] += art_map[letter][i] + "  "

        return "\n".join(lines)
