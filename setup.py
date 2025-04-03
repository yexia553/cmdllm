#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# 读取 README.md 作为长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 从 requirements.txt 读取依赖
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="cmdllm",
    version="0.1.0",
    author="CMDLLM Team",
    author_email="pzx553@gmail.com",  # 请替换为实际的邮箱
    description="使用自然语言与命令行工具交互的智能接口",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yexia553/cmdllm",  # 请替换为实际的仓库 URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 请确认使用的许可证
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cmdllm=cmdllm.cli:cli",
        ],
    },
    include_package_data=True,
    keywords="cli, command-line, llm, ai",
) 