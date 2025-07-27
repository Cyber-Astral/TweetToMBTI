"""
Gemini API 集成
负责调用 Gemini 2.5 Flash 进行 MBTI 分析
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

import google.generativeai as genai

# Add project root to path before imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from common.exceptions import APIError, EmptyResponseError, RateLimitError  # noqa: E402


class GeminiAnalyzer:
    """Gemini API 客户端，用于MBTI分析"""

    def __init__(self, api_key: str):
        """
        初始化 Gemini 客户端

        Args:
            api_key: Gemini API 密钥
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def analyze_mbti(self, tweet_data: Dict) -> Dict:
        """
        分析推文数据，返回MBTI结果

        Args:
            tweet_data: 包含原创推文和回复的数据

        Returns:
            MBTI分析结果
        """
        prompt = self._build_prompt(tweet_data)

        try:
            response = self.model.generate_content(prompt)

            # 尝试获取响应文本
            try:
                response_text = response.text
                if not response_text:
                    raise EmptyResponseError("Gemini API 返回空响应")
            except Exception as e:
                # 如果无法访问 .text，尝试手动提取
                if response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "finish_reason") and candidate.finish_reason == 2:
                        raise APIError("内容被 Gemini 安全过滤器阻止，请尝试其他用户")
                raise APIError(f"Gemini API 调用失败: {str(e)}")

            result = self._parse_response(response_text)
            return result

        except Exception as e:
            if "GEMINI_API_KEY" in str(e):
                raise
            elif "RateLimitError" in str(type(e)) or "429" in str(e):
                raise RateLimitError("Gemini API 限流，请稍后重试", retry_after=60)
            elif isinstance(e, (APIError, EmptyResponseError)):
                raise
            else:
                raise APIError(f"Gemini API 调用失败: {str(e)}")

    def _build_prompt(self, data: Dict) -> str:
        """
        构建分析提示词

        Args:
            data: 推文数据

        Returns:
            格式化的提示词
        """
        # 格式化推文样本
        original_sample = self._format_tweets(data["original_tweets"][:30])
        reply_sample = self._format_tweets(data["reply_tweets"][:30])

        prompt = f"""你是一位专业的心理学家，精通MBTI人格理论。请分析Twitter用户 @{data['username']} 的推文内容，推断其MBTI类型。

## 重要指导原则
1. **避免类型偏见**：MBTI的16种类型在人群中分布相对均匀，不要偏向任何特定类型
   - **特别警告**：当前系统存在过度判断为ISTJ的倾向（占比超过20%），请特别注意平衡判断
   - ISTJ在正常人群中约占11-14%，不应过度出现
2. **考虑社交媒体特性**：
   - Twitter倾向于展示用户的"公开面"，可能掩盖内向特质
   - 理性表达≠T型，很多F型在公开场合也表现理性
   - 具体内容≠S型，N型也会讨论具体事物
   - 有规律发推≠J型，P型也可能有发推习惯
3. **寻找平衡证据**：
   - I/E：不仅看发推频率，更要看能量流向和互动模式
   - S/N：同时寻找具体细节AND抽象思考的证据
   - T/F：同时寻找逻辑分析AND情感表达的证据
   - J/P：同时寻找计划性AND灵活性的证据
4. **人口分布参考**（美国数据）：
   - I型约50-51%，E型约49-50%
   - S型约68%，N型约32%
   - T型约40%（男性60%），F型约60%（女性75%）
   - J型约54%，P型约46%
5. **避免刻板印象**：
   - 不要因为用户讨论投资/技术就判断为T型
   - 不要因为用户发推有规律就判断为J型
   - 不要因为看不到情感表达就判断为T型
   - 不要因为内容具体就判断为S型

## 分析材料
以下是用户的推文样本（包含原创内容和回复他人的内容）。请注意，这些是抽样数据，不要将样本数量作为活跃度的判断依据。

## 原创推文样本
{original_sample}

## 回复他人的内容样本
{reply_sample}

## 分析要求

请基于以下四个维度进行深度分析。

**重要提示**：
1. 在分析中描述行为模式和内容主题时，不要使用"推文#1"、"在第X条推文中"等具体编号引用。而是描述内容的主题，例如"在分享育儿经历时"、"在讨论技术趋势时"等。
2. 不要将原创推文和回复的数量作为判断依据（如"原创和回复各100条"），因为这是抽样数据。应该关注内容质量、表达方式、互动风格等。

### 1. 外向(E) vs 内向(I)
- 能量来源（外部互动 vs 内在思考）
- 表达风格（开放分享 vs 选择性分享）
- 互动的深度vs广度（深入对话 vs 广泛社交）
- **注意**：
  - Twitter本身就是公开平台，发推≠外向
  - 深度长文和系统性思考往往是内向特征
  - 回复频率低、选择性回复可能是内向
  - 外向特征：频繁@他人、参与热门话题、即时反应、享受群体讨论
  - 内向特征：深度原创内容、系统性分享、延迟回复、独立思考
  - **平衡判断**：I/E应该接近50:50分布，不要过度判断为I型

### 2. 感觉(S) vs 直觉(N)
- 关注点（具体事实 vs 抽象概念）
- 思维模式（实际经验 vs 未来可能）
- 语言特征（具体描述 vs 隐喻象征）
- **注意**：
  - **不要过度判断为S型**：讨论具体事物≠S型，N型也会讨论实际案例
  - S型特征：关注当下、重视经验、偏好实用、描述详细、喜欢具体步骤
  - N型特征：关注可能性、重视理论、偏好创新、使用隐喻、喜欢概念框架
  - **关键区别**：S型从具体到具体，N型从具体到抽象或从抽象到具体
  - **平衡判断**：即使在技术/投资领域，N型也可能占30%以上

### 3. 思考(T) vs 情感(F)
- 决策方式（逻辑分析 vs 价值判断）
- 表达风格（客观理性 vs 主观感受）
- 对待批评和冲突的态度
- **注意**：
  - **不要过度判断为T型**：公开平台上的理性表达≠T型
  - T型特征：重视逻辑、客观分析、直接批评、关注效率、较少情感词汇
  - F型特征：重视和谐、考虑感受、委婉表达、关注人际、使用情感词汇
  - **关键线索**：
    - 使用"我觉得"、"我感觉"等词汇暗示F型
    - 关心他人状态、表达同理心暗示F型
    - 即使讨论技术也会考虑用户体验暗示F型
  - **平衡判断**：F型应该占50-60%，即使在技术圈也不应低于40%

### 4. 判断(J) vs 感知(P)
- 生活态度（计划性 vs 灵活性）
- 时间管理（结构化 vs 即兴）
- 对待变化的反应
- **注意**：
  - **不要过度判断为J型**：有规律发推≠J型，P型也可能形成习惯
  - J型特征：喜欢计划、追求完成、偏好确定、讨厌变动、强调截止日期
  - P型特征：保持开放、享受过程、偏好灵活、适应变化、强调可能性
  - **关键区别**：
    - J型倾向于"先决定再探索"
    - P型倾向于"先探索再决定"
  - **平衡判断**：J型约占54%，P型约占46%，不应相差太大

## 输出要求

请严格按照以下JSON格式输出（确保是有效的JSON）。
**重要**：在analysis字段中，使用"该用户"或"其"来指代分析对象，避免使用"他/她/他们"等可能造成性别假设的代词：

```json
{{
    "mbti_type": "XXXX",
    "dimensions": {{
        "E_I": {{
            "type": "I或E",
            "percentage": 数字(50-100),
            "analysis": "详细分析，说明判断依据"
        }},
        "S_N": {{
            "type": "S或N",
            "percentage": 数字(50-100),
            "analysis": "详细分析，说明判断依据"
        }},
        "T_F": {{
            "type": "T或F",
            "percentage": 数字(50-100),
            "analysis": "详细分析，说明判断依据"
        }},
        "J_P": {{
            "type": "J或P",
            "percentage": 数字(50-100),
            "analysis": "详细分析，说明判断依据"
        }}
    }},
    "overall_analysis": "整体人格特征的综合描述，100字左右"
}}
```

注意：
1. percentage表示该维度的倾向程度：
   - 50-60%：轻微倾向，在两种类型间比较平衡
   - 60-70%：中等倾向，有明显偏好但不绝对
   - 70-85%：强烈倾向，特征明显
   - 85-100%：极端倾向，特征非常突出（应该很少见）
   请根据实际表现合理评估，大多数人的倾向应该在55-70%之间
2. analysis要结合推文内容的主题和模式说明，但不要引用具体编号（如"推文#1"），而是描述内容主题
3. 确保输出是有效的JSON格式
4. **最终检查**：在输出前，请确认你的判断没有过度倾向于ISTJ类型（I+S+T+J的组合）"""

        return prompt

    def _format_tweets(self, tweets: List[Dict]) -> str:
        """
        格式化推文列表为可读文本

        Args:
            tweets: 推文列表

        Returns:
            格式化的文本
        """
        if not tweets:
            return "（无数据）"

        # 预分配列表大小以提高性能
        formatted = []

        for i, tweet in enumerate(tweets, 1):
            # 清理文本，移除多余的空格和换行
            text = " ".join(tweet["text"].split())
            # 截断过长的推文
            if len(text) > 200:
                text = text[:200] + "..."

            formatted.append(f"{i}. {text}")

            # 添加互动数据（如果有意义的话）
            metrics = tweet.get("metrics", {})
            likes = metrics.get("likes", 0)
            retweets = metrics.get("retweets", 0)

            if likes > 10 or retweets > 5:
                formatted.append(f"   [赞:{likes} 转:{retweets}]")

        # 使用 join 一次性拼接，比多次字符串拼接更高效
        return "\n".join(formatted)

    def _parse_response(self, response_text: str) -> Dict:
        """
        解析Gemini的响应文本

        Args:
            response_text: Gemini的原始响应

        Returns:
            解析后的MBTI结果
        """
        try:
            # 尝试提取JSON部分
            # 查找```json 和 ``` 之间的内容
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # 如果没有```json标记，尝试找到第一个{和最后一个}
                start = response_text.find("{")
                end = response_text.rfind("}")
                if start != -1 and end != -1:
                    json_text = response_text[start : end + 1]
                else:
                    raise ValueError("响应中未找到JSON数据")

            # 首次尝试解析
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError:
                # 如果失败，尝试修复常见的JSON格式错误
                json_text = self._fix_json_errors(json_text)
                # 再次尝试解析
                result = json.loads(json_text)

            # 验证必要字段
            required_fields = ["mbti_type", "dimensions", "overall_analysis"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"响应缺少必要字段: {field}")

            # 验证MBTI类型格式
            mbti_type = result["mbti_type"]
            if not re.match(r"^[EI][SN][TF][JP]$", mbti_type):
                raise ValueError(f"无效的MBTI类型: {mbti_type}")

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}\n原始响应: {response_text[:500]}...")
        except Exception as e:
            raise ValueError(f"响应解析失败: {str(e)}")

    def _fix_json_errors(self, json_text: str) -> str:
        """
        修复常见的JSON格式错误

        Args:
            json_text: 原始JSON文本

        Returns:
            修复后的JSON文本
        """
        # 使用更强大的方法修复JSON中的字符串值
        # 这个方法会找到所有的 "key": "value" 对，并修复value中的问题
        
        # 1. 首先标记所有的JSON结构位置
        # 临时替换所有的结构字符，避免在字符串中误匹配
        temp_markers = {
            '": "': '§QUOTE_COLON_QUOTE§',
            '": {': '§QUOTE_COLON_BRACE§',
            '": [': '§QUOTE_COLON_BRACKET§',
            '": ': '§QUOTE_COLON_SPACE§',
            '",': '§QUOTE_COMMA§',
            '"}': '§QUOTE_BRACE§',
            '"]': '§QUOTE_BRACKET§',
        }
        
        # 替换结构标记
        for old, new in temp_markers.items():
            json_text = json_text.replace(old, new)
        
        # 2. 处理字符串内容中的换行符
        # 匹配所有的字符串值（在引号之间的内容）
        def fix_string_content(match):
            content = match.group(1)
            # 替换实际的换行符
            content = content.replace('\n', ' ').replace('\r', ' ')
            # 压缩多个空格为一个
            content = ' '.join(content.split())
            # 转义引号
            content = content.replace('"', '\\"')
            return f'"{content}"'
        
        # 处理所有字符串值
        json_text = re.sub(r'"([^"§]*)"', fix_string_content, json_text)
        
        # 3. 恢复结构标记
        for old, new in temp_markers.items():
            json_text = json_text.replace(new, old)
        
        # 4. 修复其他常见问题
        # 修复缺少逗号的情况
        json_text = re.sub(r'(\d+)\s*\n\s*"', r'\1,\n"', json_text)
        json_text = re.sub(r'}\s*\n\s*"', r'},\n"', json_text)
        json_text = re.sub(r']\s*\n\s*"', r'],\n"', json_text)
        
        # 修复多余的逗号
        json_text = re.sub(r',\s*}', r'}', json_text)
        json_text = re.sub(r',\s*]', r']', json_text)
        
        # 确保JSON对象和数组的结束符号前没有逗号
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)

        return json_text
