"""
Context Manager module for cmdllm.

This module manages the conversation context between the user and the LLM,
storing and retrieving previous interactions to maintain context awareness
during the conversation.
"""

import os
import json

class ContextManager:
    """Manages conversation context for cmdllm."""

    def __init__(self, config):
        """Initialize context manager with configuration."""
        self.config = config
        self.context_file = os.path.expanduser("~/.cmdllm/context.json") 
        self._ensure_context_file()

    def _ensure_context_file(self):
        """Ensure context file exists."""
        os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
        if not os.path.exists(self.context_file):
            self._save_context([])

    def _load_context(self):
        """Load context from file."""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle cases where file doesn't exist or is empty/corrupt
            return []

    def _save_context(self, context):
        """Save context to file."""
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2) # Improved saving

    def get_context(self):
        """
        Get the current conversation context as a list of messages.
        
        Returns:
            list | None: A list of message dictionaries (OpenAI format) 
                         representing the recent conversation history, or None.
        """
        context = self._load_context()
        max_messages = self.config.get_max_context_messages()
        # Return the last n messages to limit context size based on configuration
        return context[-max_messages:] if context else None

    def update_context(self, query, command, result):
        """
        Update context with new interaction.
        
        Args:
            query (str): User's natural language query.
            command (str): Executed command.
            result (str): Command execution result.
        """
        context = self._load_context()
        
        # Add user message
        context.append({
            "role": "user", 
            "content": query
        })
        
        # Create assistant response combining command and result if available
        assistant_content = ""
        if command and command != "N/A":
            assistant_content += f"{command}\n\n"
        
        if result:
            assistant_content += result
        
        # Add assistant message
        context.append({
            "role": "assistant",
            "content": assistant_content.strip()
        })
        
        # Limit context based on configuration
        max_messages = self.config.get_max_context_messages()
        context = context[-max_messages:] 
        self._save_context(context)

    def clear(self):
        """Clear all context."""
        try:
            # More robust clearing by removing the file
            os.remove(self.context_file)
        except FileNotFoundError:
            pass # File already gone, no need to do anything
        # Ensure directory still exists for next time
        os.makedirs(os.path.dirname(self.context_file), exist_ok=True) 