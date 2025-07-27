"""
TweetToMBTI 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="TweetToMBTI",
    version="1.0.0",
    author="Cyber Astral",
    author_email="cyber.astral029@gmail.com",
    description="基于 Twitter 推文分析用户 MBTI 人格类型的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cyber-Astral/TweetToMBTI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tweettombti=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mbti_analyzer": ["templates/*.html"],
    },
)