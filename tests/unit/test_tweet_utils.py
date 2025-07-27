"""
推文工具模块的单元测试
"""

import pytest

from common.tweet_utils import (
    calculate_tweet_stats,
    filter_original_tweets,
    filter_reply_tweets,
    filter_retweets,
    filter_tweets,
    get_user_display_name,
    simplify_tweet,
    simplify_tweets,
    validate_tweet_data,
)


class TestTweetFiltering:
    """测试推文过滤功能"""

    @pytest.fixture
    def sample_tweets(self):
        """示例推文数据"""
        return [
            {"id": 1, "text": "原创推文", "is_reply": False, "is_retweet": False},
            {"id": 2, "text": "回复推文", "is_reply": True, "is_retweet": False},
            {"id": 3, "text": "转推", "is_reply": False, "is_retweet": True},
            {"id": 4, "text": "另一条原创", "is_reply": False, "is_retweet": False},
        ]

    def test_filter_tweets_basic(self, sample_tweets):
        """测试基础过滤功能"""
        # 过滤 ID > 2 的推文
        result = filter_tweets(sample_tweets, lambda t: t["id"] > 2)
        assert len(result) == 2
        assert result[0]["id"] == 3
        assert result[1]["id"] == 4

    def test_filter_original_tweets(self, sample_tweets):
        """测试原创推文过滤"""
        result = filter_original_tweets(sample_tweets)
        assert len(result) == 2
        assert all(not t["is_reply"] and not t["is_retweet"] for t in result)

    def test_filter_reply_tweets(self, sample_tweets):
        """测试回复推文过滤"""
        result = filter_reply_tweets(sample_tweets)
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filter_retweets(self, sample_tweets):
        """测试转推过滤"""
        result = filter_retweets(sample_tweets)
        assert len(result) == 1
        assert result[0]["id"] == 3

    def test_filter_empty_list(self):
        """测试空列表过滤"""
        assert filter_tweets([], lambda t: True) == []
        assert filter_original_tweets([]) == []


class TestTweetSimplification:
    """测试推文简化功能"""

    def test_simplify_tweet(self):
        """测试单条推文简化"""
        tweet = {
            "text": "测试推文",
            "created_at": "2024-01-01",
            "in_reply_to_screen_name": "user123",
            "favorite_count": 100,
            "retweet_count": 50,
            "reply_count": 10,
            "extra_field": "应该被忽略",
        }

        result = simplify_tweet(tweet)

        assert result["text"] == "测试推文"
        assert result["created_at"] == "2024-01-01"
        assert result["reply_to"] == "user123"
        assert result["metrics"]["likes"] == 100
        assert result["metrics"]["retweets"] == 50
        assert result["metrics"]["replies"] == 10
        assert "extra_field" not in result

    def test_simplify_tweet_missing_fields(self):
        """测试缺少字段的推文简化"""
        tweet = {"text": "只有文本"}
        result = simplify_tweet(tweet)

        assert result["text"] == "只有文本"
        assert result["created_at"] == ""
        assert result["reply_to"] == ""
        assert result["metrics"]["likes"] == 0
        assert result["metrics"]["retweets"] == 0
        assert result["metrics"]["replies"] == 0

    def test_simplify_tweets_batch(self):
        """测试批量推文简化"""
        tweets = [
            {"text": "推文1", "favorite_count": 10},
            {"text": "推文2", "favorite_count": 20},
        ]

        results = simplify_tweets(tweets)
        assert len(results) == 2
        assert results[0]["text"] == "推文1"
        assert results[1]["metrics"]["likes"] == 20


class TestTweetValidation:
    """测试推文验证功能"""

    def test_valid_tweet(self):
        """测试有效推文"""
        valid_tweets = [
            {"text": "正常推文"},
            {"text": "a"},  # 最短
            {"text": "x" * 1000},  # 长推文
        ]

        for tweet in valid_tweets:
            assert validate_tweet_data(tweet) is True

    def test_invalid_tweet(self):
        """测试无效推文"""
        invalid_tweets = [
            {},  # 没有 text 字段
            {"text": ""},  # 空文本
            {"text": "   "},  # 只有空格
            {"text": "x" * 10001},  # 太长
        ]

        for tweet in invalid_tweets:
            assert validate_tweet_data(tweet) is False


class TestUserDisplayName:
    """测试用户显示名称提取"""

    def test_get_display_name_from_first_tweet(self):
        """测试从第一条推文获取显示名称"""
        tweets = [
            {"author_name": "Elon Musk"},
            {"author_name": "Should be ignored"},
        ]

        assert get_user_display_name(tweets) == "Elon Musk"

    def test_get_display_name_empty_list(self):
        """测试空列表"""
        assert get_user_display_name([]) == ""

    def test_get_display_name_no_author(self):
        """测试没有作者名称的推文"""
        tweets = [
            {"text": "推文1"},
            {"text": "推文2"},
        ]

        assert get_user_display_name(tweets) == ""


class TestTweetStats:
    """测试推文统计功能"""

    def test_calculate_stats_normal(self):
        """测试正常的统计计算"""
        tweets = [
            {
                "text": "Hello",  # 5 chars
                "favorite_count": 100,
                "retweet_count": 50,
                "reply_count": 10,
            },
            {
                "text": "World!",  # 6 chars
                "favorite_count": 200,
                "retweet_count": 100,
                "reply_count": 20,
            },
        ]

        stats = calculate_tweet_stats(tweets)

        assert stats["total"] == 2
        assert stats["avg_length"] == 5  # (5+6)//2
        assert stats["total_likes"] == 300
        assert stats["total_retweets"] == 150
        assert stats["total_replies"] == 30

    def test_calculate_stats_empty(self):
        """测试空列表的统计"""
        stats = calculate_tweet_stats([])

        assert stats["total"] == 0
        assert stats["avg_length"] == 0
        assert stats["total_likes"] == 0
        assert stats["total_retweets"] == 0
        assert stats["total_replies"] == 0
