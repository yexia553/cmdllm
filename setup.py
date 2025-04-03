#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="cmdllm",
    version="0.1.2",
    author="Zhixiang Pan",
    author_email="pzx553@gmail.com", 
    description="Use natural language to operate all command-line tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yexia553/cmdllm",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
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