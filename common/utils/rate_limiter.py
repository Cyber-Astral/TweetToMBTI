"""
智能 API 限流处理器
"""

import time
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Optional


class RateLimiter:
    """
    智能限流处理器
    
    支持：
    - 滑动窗口限流
    - 自适应退避
    - 多级限流策略
    """
    
    def __init__(
        self,
        max_requests_per_minute: int = 60,
        max_requests_per_hour: int = 1000,
        max_requests_per_day: int = 10000
    ):
        """
        初始化限流器
        
        Args:
            max_requests_per_minute: 每分钟最大请求数
            max_requests_per_hour: 每小时最大请求数
            max_requests_per_day: 每天最大请求数
        """
        self.limits = {
            "minute": (max_requests_per_minute, timedelta(minutes=1)),
            "hour": (max_requests_per_hour, timedelta(hours=1)),
            "day": (max_requests_per_day, timedelta(days=1)),
        }
        
        # 请求历史（使用双端队列提高性能）
        self.request_history = deque(maxlen=max_requests_per_day)
        
        # 退避状态
        self.backoff_until: Optional[datetime] = None
        self.consecutive_failures = 0
        
    def can_make_request(self) -> tuple[bool, Optional[float]]:
        """
        检查是否可以发起请求
        
        Returns:
            (是否可以请求, 需要等待的秒数)
        """
        now = datetime.now()
        
        # 检查是否在退避期
        if self.backoff_until and now < self.backoff_until:
            wait_seconds = (self.backoff_until - now).total_seconds()
            return False, wait_seconds
        
        # 清理过期的请求记录
        self._cleanup_old_requests()
        
        # 检查各级限流
        for period_name, (limit, window) in self.limits.items():
            count = self._count_requests_in_window(window)
            if count >= limit:
                # 计算需要等待的时间
                if self.request_history:
                    oldest_in_window = self._get_oldest_request_in_window(window)
                    if oldest_in_window:
                        wait_until = oldest_in_window + window
                        wait_seconds = (wait_until - now).total_seconds()
                        return False, max(0, wait_seconds)
                return False, window.total_seconds()
        
        return True, None
    
    def record_request(self, success: bool = True):
        """
        记录一次请求
        
        Args:
            success: 请求是否成功
        """
        now = datetime.now()
        self.request_history.append(now)
        
        if success:
            # 重置连续失败计数
            self.consecutive_failures = 0
            self.backoff_until = None
        else:
            # 增加失败计数
            self.consecutive_failures += 1
            # 计算退避时间（指数退避）
            backoff_seconds = min(300, 2 ** self.consecutive_failures)  # 最多5分钟
            self.backoff_until = now + timedelta(seconds=backoff_seconds)
    
    def record_rate_limit_hit(self, retry_after: Optional[int] = None):
        """
        记录触发限流
        
        Args:
            retry_after: 服务器建议的重试时间（秒）
        """
        now = datetime.now()
        self.consecutive_failures += 1
        
        if retry_after:
            # 使用服务器建议的时间
            self.backoff_until = now + timedelta(seconds=retry_after)
        else:
            # 使用自适应退避
            backoff_seconds = min(600, 30 * self.consecutive_failures)  # 最多10分钟
            self.backoff_until = now + timedelta(seconds=backoff_seconds)
    
    def _cleanup_old_requests(self):
        """清理过期的请求记录"""
        now = datetime.now()
        max_window = max(window for _, window in self.limits.values())
        cutoff = now - max_window
        
        # 移除过期记录
        while self.request_history and self.request_history[0] < cutoff:
            self.request_history.popleft()
    
    def _count_requests_in_window(self, window: timedelta) -> int:
        """统计时间窗口内的请求数"""
        now = datetime.now()
        cutoff = now - window
        return sum(1 for req_time in self.request_history if req_time >= cutoff)
    
    def _get_oldest_request_in_window(self, window: timedelta) -> Optional[datetime]:
        """获取时间窗口内最早的请求时间"""
        now = datetime.now()
        cutoff = now - window
        
        for req_time in self.request_history:
            if req_time >= cutoff:
                return req_time
        return None
    
    def get_stats(self) -> Dict[str, any]:
        """
        获取限流统计信息
        
        Returns:
            包含各级限流使用情况的字典
        """
        self._cleanup_old_requests()
        stats = {}
        
        for period_name, (limit, window) in self.limits.items():
            count = self._count_requests_in_window(window)
            stats[period_name] = {
                "used": count,
                "limit": limit,
                "percentage": (count / limit * 100) if limit > 0 else 0,
                "remaining": max(0, limit - count)
            }
        
        if self.backoff_until:
            now = datetime.now()
            if now < self.backoff_until:
                stats["backoff_seconds"] = (self.backoff_until - now).total_seconds()
            else:
                stats["backoff_seconds"] = 0
        
        return stats


# 全局限流器实例（可选）
_global_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(
    service_name: str = "default",
    max_requests_per_minute: int = 60,
    max_requests_per_hour: int = 1000,
    max_requests_per_day: int = 10000
) -> RateLimiter:
    """
    获取或创建限流器实例
    
    Args:
        service_name: 服务名称（用于区分不同的 API）
        max_requests_per_minute: 每分钟最大请求数
        max_requests_per_hour: 每小时最大请求数  
        max_requests_per_day: 每天最大请求数
        
    Returns:
        限流器实例
    """
    if service_name not in _global_rate_limiters:
        _global_rate_limiters[service_name] = RateLimiter(
            max_requests_per_minute=max_requests_per_minute,
            max_requests_per_hour=max_requests_per_hour,
            max_requests_per_day=max_requests_per_day
        )
    
    return _global_rate_limiters[service_name]