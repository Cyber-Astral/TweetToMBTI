.PHONY: help install install-dev test lint format clean pre-commit

help:  ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装项目依赖
	pip install -r requirements.txt
	playwright install chromium

install-dev:  ## 安装开发依赖
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## 运行所有测试
	pytest

test-unit:  ## 只运行单元测试
	pytest tests/unit -v

test-cov:  ## 运行测试并生成覆盖率报告
	pytest --cov=. --cov-report=html --cov-report=term-missing

lint:  ## 运行代码检查
	flake8 .
	pylint scraper mbti_analyzer common --errors-only
	mypy . --ignore-missing-imports

format:  ## 格式化代码
	black .
	isort .

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

pre-commit:  ## 运行 pre-commit 检查
	pre-commit run --all-files

scrape:  ## 抓取推文示例
	@echo "使用方法: make scrape USER=username COUNT=100"
	python scrape.py $(USER) $(COUNT)

analyze:  ## 分析 MBTI 示例
	@echo "使用方法: make analyze USER=username"
	python analyze_mbti.py $(USER) --save-image --no-interactive