"""测试计算工具函数"""

import pytest
from common.calculations import (
    calculate_percentage,
    calculate_distribution,
    calculate_percentage_bar,
    format_percentage_display,
    calculate_dimension_percentage,
)


class TestCalculatePercentage:
    """测试百分比计算"""
    
    def test_basic_percentage(self):
        """测试基本百分比计算"""
        assert calculate_percentage(50, 100) == 50.0
        assert calculate_percentage(1, 3) == 33.3
        assert calculate_percentage(2, 3, decimal_places=2) == 66.67
    
    def test_edge_cases(self):
        """测试边界情况"""
        assert calculate_percentage(0, 100) == 0.0
        assert calculate_percentage(100, 100) == 100.0
        assert calculate_percentage(0, 0) == 0.0
        assert calculate_percentage(5, 0) == 0.0
    
    def test_decimal_places(self):
        """测试小数位数"""
        assert calculate_percentage(1, 3, decimal_places=0) == 33
        assert calculate_percentage(1, 3, decimal_places=1) == 33.3
        assert calculate_percentage(1, 3, decimal_places=3) == 33.333


class TestCalculateDistribution:
    """测试分布计算"""
    
    def test_basic_distribution(self):
        """测试基本分布计算"""
        data = ['A', 'B', 'A', 'C', 'A', 'B']
        result = calculate_distribution(data)
        
        # 结果应该按计数降序排列
        assert len(result) == 3
        assert result[0][0] == 'A'  # 项目
        assert result[0][1] == 3     # 计数
        assert result[0][2] == 50.0  # 百分比
        
        assert result[1][0] == 'B'
        assert result[1][1] == 2
        assert result[1][2] == 33.3
        
        assert result[2][0] == 'C'
        assert result[2][1] == 1
        assert result[2][2] == 16.7
    
    def test_empty_data(self):
        """测试空数据"""
        result = calculate_distribution([])
        assert result == []
    
    def test_decimal_places(self):
        """测试小数位数"""
        data = ['A', 'B', 'C']
        result = calculate_distribution(data, decimal_places=2)
        assert result[0][2] == 33.33  # 百分比应该有2位小数
    
    def test_sort_by_count(self):
        """测试按计数排序"""
        data = ['C', 'A', 'B', 'A', 'B', 'B']
        result = calculate_distribution(data, sort_by_count=True)
        assert result[0][0] == 'B'  # B出现3次，应该排第一
        assert result[1][0] == 'A'  # A出现2次
        assert result[2][0] == 'C'  # C出现1次
    
    def test_sort_by_key(self):
        """测试按键排序"""
        data = ['C', 'A', 'B', 'A', 'B', 'B']
        result = calculate_distribution(data, sort_by_count=False)
        assert result[0][0] == 'A'  # 按字母顺序
        assert result[1][0] == 'B'
        assert result[2][0] == 'C'


class TestCalculatePercentageBar:
    """测试进度条生成"""
    
    def test_basic_bar(self):
        """测试基本进度条"""
        assert calculate_percentage_bar(50) == "██████████░░░░░░░░░░"
        assert calculate_percentage_bar(100) == "████████████████████"
        assert calculate_percentage_bar(0) == "░░░░░░░░░░░░░░░░░░░░"
    
    def test_custom_length(self):
        """测试自定义长度"""
        assert calculate_percentage_bar(50, bar_length=10) == "█████░░░░░"
        assert calculate_percentage_bar(75, bar_length=8) == "██████░░"
    
    def test_custom_chars(self):
        """测试自定义字符"""
        assert calculate_percentage_bar(50, fill_char='*', empty_char='-') == "**********----------"
        assert calculate_percentage_bar(25, bar_length=4, fill_char='#', empty_char='.') == "#..."


class TestFormatPercentageDisplay:
    """测试百分比显示格式化"""
    
    def test_basic_format(self):
        """测试基本格式"""
        assert format_percentage_display(50.0) == " 50.0% █████░░░░░"
        assert format_percentage_display(33.33, include_bar=False) == " 33.3%"
        assert format_percentage_display(50.0, include_number=False) == "█████░░░░░"
    
    def test_with_bar(self):
        """测试带进度条的格式"""
        result = format_percentage_display(50.0, include_bar=True)
        assert " 50.0%" in result
        assert "█" in result
    
    def test_custom_format(self):
        """测试自定义格式"""
        result = format_percentage_display(
            75.5,
            include_bar=True,
            bar_length=10
        )
        assert " 75.5%" in result
        assert "█" in result


class TestCalculateDimensionPercentage:
    """测试MBTI维度百分比计算"""
    
    def test_basic_dimension(self):
        """测试基本维度计算"""
        result = calculate_dimension_percentage(80, "I", "E")
        assert result["percentage"] == 80
        assert "bar" in result
        assert "left_label" in result
        assert result["left_label"] == "[I]"
        assert result["right_label"] == "[E]"
    
    def test_edge_cases(self):
        """测试边界情况"""
        result = calculate_dimension_percentage(50, "T", "F")
        assert result["percentage"] == 50
        
        result = calculate_dimension_percentage(100, "J", "P")
        assert result["percentage"] == 100
        
        # 测试超出范围的值
        result = calculate_dimension_percentage(120, "S", "N")
        assert result["percentage"] == 100  # 应该被限制在100
        
        result = calculate_dimension_percentage(30, "E", "I")
        assert result["percentage"] == 50  # 应该被限制在50