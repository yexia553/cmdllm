"""
Configuration management for cmdllm.

This module handles loading and managing configuration settings from the
.cmdllm/config.yaml file, including LLM API keys and tool settings.
"""

import os
import yaml

class Config:
    """Configuration manager for cmdllm."""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.cmdllm")
        self.config_file = os.path.join(self.config_dir, "config.yaml")
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def _create_default_config(self):
        """Create default configuration file if it doesn't exist."""
        default_config = {
            'tools': ['bash'],
            'llm_provider': 'openai_compatible',   # Options: 'openai_compatible' or 'azure'
            'openai_compatible': {
                'base_url': 'https://api.deepseek.com/v1',
                'api_key': 'your_api_key_here',  # User needs to fill this
                'model': 'deepseek-chat'
            },
            'azure': {
                'api_key': 'your_azure_api_key_here',  # Azure OpenAI API key
                'endpoint': 'https://youe-endpoint.openai.azure.com',  # Azure OpenAI endpoint
                'deployment': 'your-deployment-name',  # Model deployment name
                'api_version': '2023-05-15'  # API version
            },
            'context': {
                'max_messages': 20  # Maximum number of messages to keep in context
            }
        }

        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f)

    def get_llm_provider(self):
        """Get the configured LLM provider.
        
        Returns:
            str: The LLM provider ('openai_compatible' or 'azure')
        """
        return self.config.get('llm_provider', 'openai_compatible')
    
    def get_openai_compatible_config(self):
        """Get OpenAI-compatible service configuration."""
        return self.config.get('openai_compatible', {})
    
    def get_azure_config(self):
        """Get Azure OpenAI-related configuration."""
        return self.config.get('azure', {})
        
    def get_tool_config(self, tool_type=None):
        """Get tool-related configuration.
        
        Args:
            tool_type (str): Optional tool type to get specific config
            
        Returns:
            dict: Tool configuration
        """
        tools = self.config.get('tools', ['bash'])
        
        if tool_type and tool_type not in tools:
            raise ValueError(f"Tool {tool_type} is not available")
            
        return {'type': tool_type}
        
    def get_tools(self):
        """Get list of all available tools.
        
        Returns:
            list: List of available tools
        """
        return self.config.get('tools', ['bash'])
        
    def add_tool(self, tool_name):
        """Add a tool to the available tools list.
        
        Args:
            tool_name (str): Name of the tool to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        tools = self.get_tools()
        if tool_name in tools:
            return False  # Tool already exists
            
        tools.append(tool_name)
        self.config['tools'] = tools
        
        try:
            self.save_config()
            return True
        except Exception:
            return False
            
    def remove_tool(self, tool_name):
        """Remove a tool from the available tools list.
        
        Args:
            tool_name (str): Name of the tool to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        tools = self.get_tools()
        if tool_name not in tools:
            return False  # Tool doesn't exist
            
        tools.remove(tool_name)
        self.config['tools'] = tools
        
        try:
            self.save_config()
            return True
        except Exception:
            return False
        
    def get_value(self, key):
        """
        Get a configuration value by dot-notation key.
        
        Args:
            key (str): The configuration key in dot notation (e.g., 'openai_compatible.api_key').
            
        Returns:
            The configuration value, or None if not found.
        """
        parts = key.split('.')
        value = self.config
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return None
            
    def set_value(self, key, value):
        """
        Set a configuration value by dot-notation key.
        
        Args:
            key (str): The configuration key in dot notation (e.g., 'openai_compatible.api_key').
            value: The value to set.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        parts = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Set the value
        config[parts[-1]] = value
        
        # Save the configuration
        try:
            self.save_config()
            return True
        except Exception:
            return False
    
    def save_config(self):
        """Save the current configuration to the config file."""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
    
    def list_config(self):
        """
        List all configuration values in a flat format.
        
        Returns:
            dict: A dictionary mapping dot-notation keys to their values.
        """
        result = {}
        
        def _flatten(d, prefix=''):
            for k, v in d.items():
                key = f"{prefix}{k}" if prefix else k
                if isinstance(v, dict):
                    _flatten(v, f"{key}.")
                else:
                    result[key] = v
        
        _flatten(self.config)
        return result

    def get_context_config(self):
        """Get context-related configuration.
        
        Returns:
            dict: Context configuration
        """
        return self.config.get('context', {'max_messages': 20})
        
    def get_max_context_messages(self):
        """Get maximum number of messages to keep in context.
        
        Returns:
            int: Maximum number of messages
        """
        context_config = self.get_context_config()
        return context_config.get('max_messages', 20)
