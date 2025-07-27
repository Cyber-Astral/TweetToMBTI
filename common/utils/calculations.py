"""
通用计算工具函数
避免代码重复的计算逻辑
"""

from typing import Dict, List, Tuple, Union


def calculate_percentage(
    value: Union[int, float], 
    total: Union[int, float], 
    decimal_places: int = 1,
    min_value: float = 0.0,
    max_value: float = 100.0
) -> float:
    """
    计算百分比
    
    Args:
        value: 当前值
        total: 总值
        decimal_places: 小数位数
        min_value: 最小值限制
        max_value: 最大值限制
        
    Returns:
        百分比值
    """
    if total <= 0:
        return 0.0
    
    percentage = (value / total) * 100
    percentage = max(min_value, min(percentage, max_value))
    
    return round(percentage, decimal_places)


def calculate_percentage_bar(
    percentage: float,
    bar_length: int = 20,
    fill_char: str = "█",
    empty_char: str = "░"
) -> str:
    """
    生成百分比进度条
    
    Args:
        percentage: 百分比（0-100）
        bar_length: 进度条长度
        fill_char: 填充字符
        empty_char: 空白字符
        
    Returns:
        进度条字符串
    """
    filled = int(percentage * bar_length / 100)
    filled = max(0, min(filled, bar_length))
    
    return fill_char * filled + empty_char * (bar_length - filled)


def calculate_distribution(
    items: List[any],
    key_func: callable = None,
    sort_by_count: bool = True,
    decimal_places: int = 1
) -> List[Tuple[any, int, float]]:
    """
    计算分布统计
    
    Args:
        items: 项目列表
        key_func: 提取键的函数
        sort_by_count: 是否按数量排序
        
    Returns:
        [(项目, 数量, 百分比)] 列表
    """
    if not items:
        return []
    
    # 统计
    counts: Dict[any, int] = {}
    for item in items:
        key = key_func(item) if key_func else item
        counts[key] = counts.get(key, 0) + 1
    
    total = len(items)
    results = []
    
    for key, count in counts.items():
        percentage = calculate_percentage(count, total, decimal_places)
        results.append((key, count, percentage))
    
    # 排序
    if sort_by_count:
        results.sort(key=lambda x: x[1], reverse=True)
    else:
        results.sort(key=lambda x: x[0])
    
    return results


def calculate_dimension_percentage(
    score: float,
    dimension_type: str,
    opposite_type: str,
    total_length: int = 20
) -> Dict[str, any]:
    """
    计算 MBTI 维度百分比和进度条
    
    Args:
        score: 倾向分数（50-100）
        dimension_type: 当前维度类型（如 'I'）
        opposite_type: 对立维度类型（如 'E'）
        total_length: 进度条总长度
        
    Returns:
        包含进度条和百分比信息的字典
    """
    # 确保分数在合理范围内
    score = max(50, min(100, score))
    
    # 计算填充长度
    filled = round(score * total_length / 100)
    filled = max(0, min(filled, total_length))
    
    # 生成进度条
    if score >= 50:
        # 当前类型占优
        bar = "█" * filled + "░" * (total_length - filled)
        left_label = f"[{dimension_type}]"
        right_label = f"[{opposite_type}]"
        percentage_text = f"{score}%"
    else:
        # 对立类型占优（理论上不应该出现，但为了完整性）
        opposite_score = 100 - score
        filled = round(opposite_score * total_length / 100)
        bar = "░" * (total_length - filled) + "█" * filled
        left_label = f"[{dimension_type}]"
        right_label = f"[{opposite_type}]"
        percentage_text = f"{opposite_score}%"
    
    return {
        "bar": bar,
        "left_label": left_label,
        "right_label": right_label,
        "percentage": score,
        "percentage_text": percentage_text,
        "dominant_type": dimension_type if score >= 50 else opposite_type
    }


def calculate_stats_summary(
    data: List[Dict],
    value_key: str,
    group_key: str = None
) -> Dict[str, any]:
    """
    计算统计摘要
    
    Args:
        data: 数据列表
        value_key: 值字段名
        group_key: 分组字段名（可选）
        
    Returns:
        统计摘要字典
    """
    if not data:
        return {
            "total": 0,
            "sum": 0,
            "average": 0,
            "min": 0,
            "max": 0,
            "groups": {}
        }
    
    values = [item.get(value_key, 0) for item in data]
    total_sum = sum(values)
    
    summary = {
        "total": len(data),
        "sum": total_sum,
        "average": total_sum / len(data) if data else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
        "groups": {}
    }
    
    # 分组统计
    if group_key:
        groups = {}
        for item in data:
            group = item.get(group_key, "unknown")
            if group not in groups:
                groups[group] = []
            groups[group].append(item.get(value_key, 0))
        
        for group, group_values in groups.items():
            summary["groups"][group] = {
                "count": len(group_values),
                "sum": sum(group_values),
                "average": sum(group_values) / len(group_values) if group_values else 0,
                "percentage": calculate_percentage(len(group_values), len(data))
            }
    
    return summary


def format_percentage_display(
    percentage: float,
    include_bar: bool = True,
    bar_length: int = 10,
    include_number: bool = True
) -> str:
    """
    格式化百分比显示
    
    Args:
        percentage: 百分比值
        include_bar: 是否包含进度条
        bar_length: 进度条长度
        include_number: 是否包含数字
        
    Returns:
        格式化的字符串
    """
    parts = []
    
    if include_number:
        parts.append(f"{percentage:5.1f}%")
    
    if include_bar:
        bar = calculate_percentage_bar(percentage, bar_length)
        parts.append(bar)
    
    return " ".join(parts)