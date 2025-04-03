# -*- coding: utf-8 -*-
"""
CMDLLM - Interact with command-line tools using natural language.

This package provides an interface to use natural language to generate
and execute commands for various command-line tools.
"""

__version__ = '0.1.0'
__author__ = 'CMDLLM Team'

# Make main components easily importable (optional)
from .cli import cli
from .config import Config
from .llm_processor import LLMProcessor
from .command_executor import CommandExecutor
from .context_manager import ContextManager 