"""
Command Executor module for cmdllm.

This module is responsible for executing commands for different tools
and handling their results. It provides a safe interface for
running commands generated from natural language queries.
"""

import subprocess
import shlex

class CommandExecutor:
    """Executes tool commands and handles their output."""
    
    def __init__(self, config):
        """
        Initialize the command executor.
        
        Args:
            config (Config): The configuration object.
        """
        self.tool_config = config.get_tool_config()
        self.tool_type = self.tool_config['type']  # Will raise KeyError if invalid

    def execute(self, command, is_dangerous=False):
        """
        Execute a command and return its output.

        Args:
            command (str): The command to execute
            is_dangerous (bool): Whether the command is potentially dangerous

        Returns:
            tuple: (output, requires_confirmation)
                - output (str): Command output or message
                - requires_confirmation (bool): Whether user confirmation is needed
        """
        try:
            # Add tool prefix if not present and not bash
            if self.tool_type != 'bash' and not command.startswith(f'{self.tool_type} '):
                # Basic check, might need refinement depending on command structure
                command = f'{self.tool_type} {command}'

            if is_dangerous:
                # Return a confirmation request
                return (
                    f"⚠️ This is a potentially dangerous operation!\n"
                    f"Command to execute: {command}\n"
                    f"Please confirm if you want to proceed (y/n): ",
                    True
                )

            # Execute the command and capture output
            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )

            # Combine stdout and stderr, with stdout first
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"  # Add newline separator if both stdout/stderr exist
                output += result.stderr

            return output, False

        except FileNotFoundError:
            return f"Error: '{self.tool_type}' command not found. Please ensure {self.tool_type} is installed and in your PATH.", False
        except Exception as e:
            return f"Error executing command: {str(e)}", False

    def execute_confirmed(self, command):
        """
        Execute a confirmed dangerous command.

        Args:
            command (str): The command to execute

        Returns:
            str: The command output or error message
        """
        try:
            # Ensure command starts with tool type if needed
            if self.tool_type != 'bash' and not command.startswith(f'{self.tool_type} '):
                command = f'{self.tool_type} {command}'

            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )

            # Combine stdout and stderr, with stdout first
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"  # Add newline separator if both stdout/stderr exist
                output += result.stderr

            return output

        except FileNotFoundError:
            return f"Error: '{self.tool_type}' command not found. Please ensure {self.tool_type} is installed and in your PATH."
        except Exception as e:
            return f"Error executing confirmed command: {str(e)}"
