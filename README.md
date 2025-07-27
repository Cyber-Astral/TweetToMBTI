# TweetToMBTI 🧠

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Cyber-Astral/TweetToMBTI/pulls)

**基于 AI 的 Twitter/X 用户 MBTI 人格类型分析工具**

[中文](#chinese) | [English](#english) | [报告问题](https://github.com/Cyber-Astral/TweetToMBTI/issues)

</div>

---

<a name="chinese"></a>
## 🌏 中文

### 🎯 概述

TweetToMBTI 是一款创新的 Python 工具，利用人工智能技术根据推文内容分析 Twitter/X 用户的人格类型。通过结合先进的自然语言处理和心理学分析，它能够洞察用户的 MBTI（迈尔斯-布里格斯性格分类）人格类型。

### ✨ 核心功能

- **🐦 智能推文收集**：使用 Apify API 高效抓取推文，支持智能速率限制
- **🤖 AI 驱动分析**：利用 Google Gemini AI 进行精准的人格分析
- **📊 精美可视化**：生成终端风格的 HTML 报告，包含详细的人格分析
- **📸 可分享结果**：将报告导出为高质量 PNG 图片，便于分享

### 📸 效果展示

<details>
<summary>📊 查看分析报告示例（Elon Musk 真实分析结果）</summary>

```
╔══════════════════════════════════════════════════════════════════════╗
║                        MBTI 人格分析报告                            ║
║                      @elonmusk - ENTJ 型                            ║
╚══════════════════════════════════════════════════════════════════════╝

【人格类型：ENTJ - 指挥官】
大胆、有想象力的领导者。总是能找到或创造解决办法。

【维度分析】

外向 (E) vs 内向 (I)
████████████████████████░░░░░░░░  [E] 76%
分析：通过外部活动和交流来表达自己并获取能量

直觉 (N) vs 感觉 (S)
████████████████████████████░░░░  [N] 88%
分析：关注未来可能性、创新概念和宏大愿景

思考 (T) vs 情感 (F)
███████████████████████████░░░░░  [T] 85%
分析：运用逻辑和分析来解决问题，注重客观事实

判断 (J) vs 感知 (P)
████████████████████████░░░░░░░░  [J] 75%
分析：通过计划性和执行力来实现其前瞻性的目标

【推文分析摘要】
基于 100 条原创推文和 100 条回复分析：
- 主要内容：Tesla、SpaceX、AI、可持续能源、技术创新
- 沟通风格：直接、自信、带有幽默感、愿景驱动
- 关键特征：目标导向、系统性思维、推动大规模创新

报告生成时间：2025-07-27 14:12:05
```

</details>

> 📄 完整 HTML 报告示例：[examples/mbti_report_elonmusk_20250727_141205.html](examples/mbti_report_elonmusk_20250727_141205.html)  
> 🖼️ PNG 图片示例：[查看分析图片](examples/mbti_report_elonmusk_20250727_141205.png)

<details>
<summary>📈 查看统计仪表板</summary>

```
╔══════════════════════════════════════════════════════════════════════╗
║                     MBTI 分布统计                                   ║
║                    总分析用户数: 156                                ║
╚══════════════════════════════════════════════════════════════════════╝

【类型分布】
INTJ  ████████████░░░░░░░░  20 用户 (12.8%)
INTP  ██████████░░░░░░░░░░  18 用户 (11.5%)
ENTJ  █████████░░░░░░░░░░░  16 用户 (10.3%)
ENTP  ████████░░░░░░░░░░░░  14 用户 (9.0%)
...

【维度偏好】
内向: 54.5% | 外向: 45.5%
直觉: 61.5% | 感觉: 38.5%
思考: 58.3% | 情感: 41.7%
判断: 52.6% | 感知: 47.4%
```

</details>

### 🚀 快速开始

#### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- Git

#### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/Cyber-Astral/TweetToMBTI.git
   cd TweetToMBTI
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 系统：venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   playwright install chromium  # 图片导出功能必需
   ```

4. **配置 API 密钥**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的 API 密钥
   ```

5. **验证安装**
   ```bash
   python cli.py --version
   ```

### 📖 使用指南

#### 命令行界面

工具提供统一的 CLI，包含多个命令：

```bash
# 显示帮助和所有可用命令
python cli.py --help

# 分析单个用户（默认：100 条原创推文 + 100 条回复 = 共 200 条）
python cli.py analyze 用户名

# 分析并保存图片
# --save-image: 将 HTML 报告转换为 PNG 图片保存
python cli.py analyze 用户名 --save-image

# 非交互模式分析
# --no-interactive: 跳过图片生成后的浏览器打开提示
python cli.py analyze 用户名 --save-image --no-interactive

# 仅抓取推文，不进行 MBTI 分析
# 参数：用户名 [推文数量]
# 默认抓取 100 条
python cli.py scrape 用户名
# 指定抓取 200 条
python cli.py scrape 用户名 200

# 生成所有历史分析的 MBTI 类型分布统计
python cli.py stats

# 查看今日的分析统计（仅统计当天的分析结果）
python cli.py today-stats

# 检查 API 配置是否正确
python cli.py check-config
```

**常用参数说明：**
- `--save-image`: 生成 PNG 图片格式的报告（需要安装 playwright）
- `--no-interactive`: 静默模式，不打开浏览器预览
- `--help`: 查看详细帮助信息

**报告保存位置：**
- HTML 报告：`mbti_analyzer/reports/mbti_report_用户名_时间戳.html`
- PNG 图片：`mbti_analyzer/images/mbti_report_用户名_时间戳.png`
- 抓取数据：`scraper/scraped_data/user_tweets/用户名_tweets.json`

#### 高级用法

<details>
<summary>🔧 配置选项</summary>

你可以通过设置环境变量来自定义分析行为：

```bash
# 分析设置
export MBTI_ANALYSIS_MIN_TWEETS=100  # 分析所需的最少推文数
export MBTI_ANALYSIS_MAX_TWEETS=1000 # 分析的最大推文数

# 输出设置
export MBTI_REPORT_FORMAT="html"     # 输出格式 (html/json/text)
export MBTI_AUTO_SAVE_IMAGE=true     # 自动保存为图片

# API 设置
export GEMINI_MODEL="gemini-pro"     # 使用的 Gemini 模型
export APIFY_TIMEOUT=300             # API 超时时间（秒）
```

</details>

<details>
<summary>🐍 Python API 使用</summary>

你也可以将 TweetToMBTI 作为 Python 库使用：

```python
from mbti_analyzer import analyze_user, generate_report
from scraper import scrape_tweets

# 抓取推文
tweets = scrape_tweets("elonmusk", count=500)

# 分析人格
result = analyze_user(tweets)
print(f"人格类型: {result['type']}")
print(f"置信度: {result['confidence']}%")

# 生成报告
report_path = generate_report(result, format="html", save_image=True)
print(f"报告已保存到: {report_path}")
```

</details>

### 🔑 API 密钥设置

本项目需要两个 API 密钥：

#### 1. Gemini API 密钥（有免费额度）
- **用途**：驱动 AI 人格分析
- **获取地址**：[Google AI Studio](https://makersuite.google.com/app/apikey)
- **免费额度**：每分钟 60 次请求
- **配置**：在 `.env` 中设置 `GEMINI_API_KEY`

#### 2. Apify API Token
- **用途**：处理 Twitter 数据收集
- **使用的 Actor**：[🏯 Tweet Scraper V2 - X / Twitter Scraper](https://apify.com/apidojo/tweet-scraper)
- **获取地址**：[Apify Console](https://console.apify.com/account/integrations)
- **价格**：每 1000 条推文 $0.40
- **免费额度**：新用户有 $5 免费额度
- **配置**：在 `.env` 中设置 `APIFY_API_TOKEN`

### 🐛 故障排除

<details>
<summary>常见问题和解决方案</summary>

#### API 密钥错误
```
Error: GEMINI_API_KEY environment variable is not set
```
**解决方案**: 确保 `.env` 文件存在并包含有效的 API 密钥。

#### Playwright 安装问题
```
Error: Browser not found
```
**解决方案**: 运行 `playwright install chromium` 安装所需的浏览器。

#### 速率限制
```
Error: API rate limit exceeded
```
**解决方案**: 等待几分钟或升级 API 计划以获得更高的限制。

#### 导入错误
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案**: 确保已激活虚拟环境并安装了所有依赖。

</details>

### 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- [Apify](https://apify.com/) 提供 Twitter 抓取基础设施
- [Google Gemini](https://deepmind.google/technologies/gemini/) 提供 AI 驱动的分析
- [Playwright](https://playwright.dev/) 提供跨浏览器自动化
- 所有贡献者和本项目的用户

### 📧 联系方式

- **作者**：Cyber Astral
- **邮箱**：cyber.astral029@gmail.com
- **GitHub**：[@Cyber-Astral](https://github.com/Cyber-Astral)
- **问题反馈**：[提交 Issue](https://github.com/Cyber-Astral/TweetToMBTI/issues)

### ⚠️ 免责声明

本工具仅供教育和娱乐目的使用。基于社交媒体帖子的 MBTI 人格分析不应被视为科学准确，也不应用于专业心理评估。结果是 AI 生成的解释，可能无法反映实际的人格类型。

---

<a name="english"></a>
## 🌍 English

### 🎯 Overview

TweetToMBTI is an innovative Python tool that leverages artificial intelligence to analyze Twitter/X users' personality types based on their tweet content. By combining advanced natural language processing with psychological profiling, it provides insights into users' MBTI (Myers-Briggs Type Indicator) personality types.

### ✨ Key Features

- **🐦 Smart Tweet Collection**: Efficiently scrapes tweets using the Apify API with intelligent rate limiting
- **🤖 AI-Powered Analysis**: Utilizes Google's Gemini AI for sophisticated personality analysis
- **📊 Beautiful Visualizations**: Generates terminal-style HTML reports with detailed personality breakdowns
- **📸 Shareable Results**: Exports reports as high-quality PNG images for easy sharing

### 📸 Screenshots

<details>
<summary>📊 View Example Analysis Report (Elon Musk Real Analysis)</summary>

```
╔══════════════════════════════════════════════════════════════════════╗
║                      MBTI Personality Analysis                       ║
║                        @elonmusk - ENTJ                              ║
╚══════════════════════════════════════════════════════════════════════╝

【Personality Type: ENTJ - The Commander】
Bold, imaginative and strong-willed leaders, always finding a way or making one.

【Dimension Analysis】

Extraversion (E) vs Introversion (I)
████████████████████████░░░░░░░░  [E] 76%
Analysis: Gains energy from external interactions and public communication

Intuition (N) vs Sensing (S)
████████████████████████████░░░░  [N] 88%
Analysis: Focuses on future possibilities, innovation and grand visions

Thinking (T) vs Feeling (F)
███████████████████████████░░░░░  [T] 85%
Analysis: Uses logic and analysis to solve problems, focuses on objective facts

Judging (J) vs Perceiving (P)
████████████████████████░░░░░░░░  [J] 75%
Analysis: Achieves forward-thinking goals through planning and execution

【Tweet Analysis Summary】
Based on analysis of 100 original tweets and 100 replies:
- Main topics: Tesla, SpaceX, AI, sustainable energy, tech innovation
- Communication style: Direct, confident, humorous, vision-driven
- Key traits: Goal-oriented, systematic thinking, driving large-scale innovation

Report generated: 2025-07-27 14:12:05
```

</details>

> 📄 Full HTML Report Example: [examples/mbti_report_elonmusk_20250727_141205.html](examples/mbti_report_elonmusk_20250727_141205.html)  
> 🖼️ PNG Image Example: [View Analysis Image](examples/mbti_report_elonmusk_20250727_141205.png)

<details>
<summary>📈 View Statistics Dashboard</summary>

```
╔══════════════════════════════════════════════════════════════════════╗
║                     MBTI Distribution Statistics                     ║
║                    Total Analyzed Users: 156                         ║
╚══════════════════════════════════════════════════════════════════════╝

【Type Distribution】
INTJ  ████████████░░░░░░░░  20 users (12.8%)
INTP  ██████████░░░░░░░░░░  18 users (11.5%)
ENTJ  █████████░░░░░░░░░░░  16 users (10.3%)
ENTP  ████████░░░░░░░░░░░░  14 users (9.0%)
...

【Dimension Preferences】
Introversion: 54.5% | Extraversion: 45.5%
Intuition: 61.5%    | Sensing: 38.5%
Thinking: 58.3%     | Feeling: 41.7%
Judging: 52.6%      | Perceiving: 47.4%
```

</details>

### 🚀 Quick Start

#### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Cyber-Astral/TweetToMBTI.git
   cd TweetToMBTI
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium  # Required for image export
   ```

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Verify installation**
   ```bash
   python cli.py --version
   ```

### 📖 Usage Guide

#### Command Line Interface

The tool provides a unified CLI with multiple commands:

```bash
# Display help and all available commands
python cli.py --help

# Analyze a single user (default: 100 original tweets + 100 replies = 200 total)
python cli.py analyze username

# Analyze and save as image
# --save-image: Convert HTML report to PNG image
python cli.py analyze username --save-image

# Non-interactive analysis
# --no-interactive: Skip browser open prompt after image generation
python cli.py analyze username --save-image --no-interactive

# Scrape tweets only, without MBTI analysis
# Parameters: username [tweet_count]
# Default: 100 tweets
python cli.py scrape username
# Specify count: 200 tweets
python cli.py scrape username 200

# Generate MBTI type distribution statistics from all historical analyses
python cli.py stats

# View today's analysis statistics (only current day results)
python cli.py today-stats

# Check API configuration
python cli.py check-config
```

**Common Parameters:**
- `--save-image`: Generate PNG image format report (requires playwright)
- `--no-interactive`: Silent mode, don't open browser preview
- `--help`: View detailed help information

**Report Save Locations:**
- HTML Report: `mbti_analyzer/reports/mbti_report_username_timestamp.html`
- PNG Image: `mbti_analyzer/images/mbti_report_username_timestamp.png`
- Scraped Data: `scraper/scraped_data/user_tweets/username_tweets.json`

#### Advanced Usage

<details>
<summary>🔧 Configuration Options</summary>

You can customize the analysis behavior by setting environment variables:

```bash
# Analysis settings
export MBTI_ANALYSIS_MIN_TWEETS=100  # Minimum tweets for analysis
export MBTI_ANALYSIS_MAX_TWEETS=1000 # Maximum tweets to analyze

# Output settings
export MBTI_REPORT_FORMAT="html"     # Output format (html/json/text)
export MBTI_AUTO_SAVE_IMAGE=true     # Automatically save as image

# API settings
export GEMINI_MODEL="gemini-pro"     # Gemini model to use
export APIFY_TIMEOUT=300             # API timeout in seconds
```

</details>

<details>
<summary>🐍 Python API Usage</summary>

You can also use TweetToMBTI as a Python library:

```python
from mbti_analyzer import analyze_user, generate_report
from scraper import scrape_tweets

# Scrape tweets
tweets = scrape_tweets("elonmusk", count=500)

# Analyze personality
result = analyze_user(tweets)
print(f"Personality Type: {result['type']}")
print(f"Confidence: {result['confidence']}%")

# Generate report
report_path = generate_report(result, format="html", save_image=True)
print(f"Report saved to: {report_path}")
```

</details>

### 🔑 API Keys Setup

This project requires two API keys:

#### 1. Gemini API Key (Free tier available)
- **Purpose**: Powers the AI personality analysis
- **Get it from**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Free tier**: 60 requests per minute
- **Setup**: Add to `.env` as `GEMINI_API_KEY`

#### 2. Apify API Token
- **Purpose**: Handles Twitter data collection
- **Actor Used**: [🏯 Tweet Scraper V2 - X / Twitter Scraper](https://apify.com/apidojo/tweet-scraper)
- **Get it from**: [Apify Console](https://console.apify.com/account/integrations)
- **Pricing**: $0.40 per 1000 tweets
- **Free tier**: $5 free credit for new users
- **Setup**: Add to `.env` as `APIFY_API_TOKEN`

### 🐛 Troubleshooting

<details>
<summary>Common Issues and Solutions</summary>

#### API Key Errors
```
Error: GEMINI_API_KEY environment variable is not set
```
**Solution**: Ensure your `.env` file exists and contains valid API keys.

#### Playwright Installation Issues
```
Error: Browser not found
```
**Solution**: Run `playwright install chromium` to install required browsers.

#### Rate Limiting
```
Error: API rate limit exceeded
```
**Solution**: Wait a few minutes or upgrade your API plan for higher limits.

#### Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**: Ensure you've activated your virtual environment and installed all dependencies.

</details>

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Apify](https://apify.com/) for providing the Twitter scraping infrastructure
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI-powered analysis
- [Playwright](https://playwright.dev/) for cross-browser automation
- All contributors and users of this project

### 📧 Contact

- **Author**: Cyber Astral
- **Email**: cyber.astral029@gmail.com
- **GitHub**: [@Cyber-Astral](https://github.com/Cyber-Astral)
- **Issues**: [Report a bug](https://github.com/Cyber-Astral/TweetToMBTI/issues)

### ⚠️ Disclaimer

This tool is for educational and entertainment purposes only. MBTI personality analysis based on social media posts should not be considered scientifically accurate or used for professional psychological assessment. The results are AI-generated interpretations and may not reflect actual personality types.

---

<div align="center">

Made with ❤️ by [Cyber Astral](https://github.com/Cyber-Astral)

⭐ Star us on GitHub — it helps!

[🔝 返回顶部 / Back to top](#)

</div>