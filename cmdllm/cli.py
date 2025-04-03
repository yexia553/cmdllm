"""
Command Line Interface for cmdllm.

This module provides the main entry point for the cmdllm command-line tool.
It handles command-line arguments, configuration management, and orchestrates
the interaction between different components of the system for command-line operations.
"""

import click
import sys
import yaml
# Import from cmdllm package
from .config import Config
from .llm_processor import LLMProcessor
from .command_executor import CommandExecutor
from .context_manager import ContextManager

@click.group()
@click.pass_context
def cli(ctx):
    """Intelligent interface to interact with command-line tools using natural language."""
    # Pass, as clear-context is now a separate command
    pass

@cli.command()
@click.option('-t', '--tool', 'tool_type', required=True, help='Specify the tool type for the chat session (e.g., bash, kubectl).')
def chat(tool_type):
    """Start an interactive chat session for a specific tool type."""
    config = Config() # Load configuration first

    try:
        # Validate tool type is available
        config.get_tool_config(tool_type) # Will raise ValueError if not available
    except ValueError as e:
        click.echo(click.style(f"Configuration error: {e}", fg='red'))
        return # Exit if config fails

    context_manager = ContextManager(config)

    # Initialize components outside the loop, passing the tool_type
    try:
        # Pass tool_type to LLMProcessor
        llm_processor = LLMProcessor(config, tool_type)
    except ValueError as e: # Catch potential init errors (like missing API key)
        click.echo(click.style(f"LLM initialization error: {e}", fg='red'))
        return

    command_executor = CommandExecutor(tool_type)

    click.echo(f"Starting interactive {tool_type} session. Type 'exit' or 'quit' to end.")
    click.echo("-----------------------------------------------------")

    while True:
        # Use click.prompt for interactive input inside the loop
        final_query = click.prompt(click.style(f'{tool_type}> ', fg='cyan'), prompt_suffix='')

        if final_query.lower() in ['exit', 'quit']:
            click.echo("Exiting chat session.")
            break

        if not final_query: # Handle empty input
            continue

        # Process the query using LLM
        click.echo(click.style("Processing your query...", fg='yellow'))
        try:
            response_type, response = llm_processor.process_query(final_query, context_manager.get_context())
        except Exception as e:
             click.echo(click.style(f"Error during LLM processing: {e}", fg='red'))
             continue # Continue the loop on processing error

        command_to_log = "N/A" # Initialize command for logging for this turn
        result_to_log = "N/A" # Initialize result for logging for this turn

        if response_type == 'command':
            command, is_dangerous = response
            command_to_log = command # Store command for context

            # Display the proposed command
            click.echo("\nSuggested command:")
            command_style = {'fg': 'red', 'bold': True} if is_dangerous else {'fg': 'green', 'bold': True}
            click.echo(click.style(f"  {command}", **command_style))
            if is_dangerous:
                click.echo(click.style("  (Potentially dangerous operation!)", fg='yellow'))
            click.echo()

            # Execute the command with confirmation logic
            try:
                result, requires_confirmation = command_executor.execute(command, is_dangerous)

                if requires_confirmation:
                    # Display the confirmation prompt from the executor
                    click.echo(click.style(result, fg='yellow'))
                    # Use click's confirmation prompt
                    if click.confirm(click.style("Are you sure you want to proceed?", bold=True)):
                        click.echo(click.style("Executing confirmed command...", fg='yellow'))
                        final_result = command_executor.execute_confirmed(command)
                    else:
                        final_result = "Operation cancelled by user."
                else:
                    final_result = result # Use the direct result if no confirmation needed

                result_to_log = final_result # Store final result for context

                # Display the execution result
                click.echo(click.style("\nExecution result:", bold=True))
                click.echo(final_result)

            except Exception as e:
                click.echo(click.style(f"Error during command execution: {e}", fg='red'))
                result_to_log = f"Error executing command: {e}" # Log execution error


        elif response_type == 'answer':
            answer = response
            result_to_log = answer # Log the answer
            click.echo(click.style("\nAnswer:", bold=True))
            click.echo(answer)

        else: # Handle unexpected response types
            error_message = f"LLM processor returned an unexpected response type or format: {response}"
            click.echo(click.style(error_message, fg='red'))
            result_to_log = error_message

        # Update context after processing each query
        context_manager.update_context(final_query, command_to_log, result_to_log)

        click.echo("\n-----------------------------------------------------") # Separator for next prompt

@cli.command('clear')
def clear_context_command():
    """Clear the conversation context history."""
    try:
        config = Config() # Need config to init context manager
        context_manager = ContextManager(config)
        context_manager.clear()
        click.echo(click.style("Context has been successfully cleared.", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error clearing context: {e}", fg='red'))
        sys.exit(1) # Exit with error if clearing fails

@cli.group()
def config():
    """Manage LLM configuration."""
    pass

@config.command()
@click.argument('key')
def get(key):
    """Get the value of a configuration item."""
    # Check if key starts with 'tools' to prevent direct tools access through config commands
    if key.startswith('tools'):
        click.echo(click.style(f"Please use 'cmdllm tools' commands to manage tools.", fg='yellow'))
        return
        
    config = Config()
    value = config.get_value(key)
    
    if value is None:
        click.echo(click.style(f"Configuration item not found: {key}", fg='yellow'))
    else:
        if isinstance(value, dict):
            click.echo(yaml.dump(value, default_flow_style=False))
        else:
            click.echo(value)

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set the value of a configuration item."""
    # Check if key starts with 'tools' to prevent direct tools access through config commands
    if key.startswith('tools'):
        click.echo(click.style(f"Please use 'cmdllm tools' commands to manage tools.", fg='yellow'))
        return
        
    config = Config()
    
    # Try to convert string values to appropriate types
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
        value = float(value)
    
    if config.set_value(key, value):
        click.echo(click.style(f"Set {key} = {value}", fg='green'))
    else:
        click.echo(click.style(f"Failed to set configuration item: {key}", fg='red'))

@config.command(name='list')
def list_config():
    """List all configuration items."""
    config = Config()
    items = config.list_config()
    
    if not items:
        click.echo("Configuration is empty")
        return
    
    max_key_length = max(len(k) for k in items.keys())
    
    for key, value in sorted(items.items()):
        # Skip tools configuration
        if key.startswith('tools'):
            continue
            
        # Special handling for sensitive information
        if 'api_key' in key and value and value not in ['your_api_key_here', 'your_azure_api_key_here']:
            displayed_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
        else:
            displayed_value = value
            
        click.echo(f"{key.ljust(max_key_length + 2)}: {displayed_value}")

@config.command()
def init():
    """Initialize default configuration file."""
    if click.confirm(click.style("This will reset all configuration to default values. Continue?", fg='yellow')):
        config = Config()
        config._create_default_config()
        config = Config()  # Reload configuration
        click.echo(click.style("Default configuration initialized", fg='green'))
        list_config()
    else:
        click.echo("Operation cancelled")

@config.command()
def setup():
    """Interactive setup for LLM provider configuration."""
    config = Config()
    
    # Prompt for provider selection
    provider = click.prompt(
        'Please select LLM provider (openai_compatible/azure)', 
        type=click.Choice(['openai_compatible', 'azure']), 
        default=config.get_value('llm_provider') or 'openai_compatible'
    )
    config.set_value('llm_provider', provider)

    if provider == 'openai_compatible':
        base_url = click.prompt(
            'Please enter OpenAI-compatible API Base URL', 
            default=config.get_value('openai_compatible.base_url') or 'https://api.openai.com/v1'
        )
        api_key = click.prompt(
            'Please enter OpenAI-compatible API Key', 
            default=config.get_value('openai_compatible.api_key') or ''
        )
        model = click.prompt(
            'Please enter model name', 
            default=config.get_value('openai_compatible.model') or 'gpt-3.5-turbo'
        )
        
        config.set_value('openai_compatible.api_key', api_key)
        config.set_value('openai_compatible.base_url', base_url)
        config.set_value('openai_compatible.model', model)
        
    elif provider == 'azure':
        azure_endpoint = click.prompt(
            'Please enter Azure OpenAI Endpoint URL', 
            default=config.get_value('azure.endpoint') or 'https://your-resource-name.openai.azure.com'
        )
        azure_api_key = click.prompt(
            'Please enter Azure OpenAI API Key', 
            default=config.get_value('azure.api_key') or ''
        )
        azure_deployment = click.prompt(
            'Please enter Azure OpenAI deployment name', 
            default=config.get_value('azure.deployment') or 'your-deployment-name'
        )
        azure_api_version = click.prompt(
            'Please enter Azure OpenAI API Version', 
            default=config.get_value('azure.api_version') or '2023-05-15'
        )
        
        config.set_value('azure.api_key', azure_api_key)
        config.set_value('azure.endpoint', azure_endpoint)
        config.set_value('azure.deployment', azure_deployment)
        config.set_value('azure.api_version', azure_api_version)
        
        # Clear any existing OpenAI-compatible configurations (optional, avoids confusion)
        config.set_value('openai_compatible.api_key', '')
        config.set_value('openai_compatible.base_url', '')
        config.set_value('openai_compatible.model', '')

    click.echo(click.style("LLM configuration updated!", fg='green'))
    click.echo("\nCurrent LLM configuration:")
    
    # Display updated relevant configuration
    items = config.list_config()
    max_key_length = 0
    filtered_items = {}
    if provider == 'openai_compatible':
        keys_to_show = ['llm_provider', 'openai_compatible.api_key', 'openai_compatible.base_url', 'openai_compatible.model']
    else: # azure
        keys_to_show = ['llm_provider', 'azure.api_key', 'azure.endpoint', 'azure.deployment', 'azure.api_version']
        
    for key in keys_to_show:
        if key in items:
             filtered_items[key] = items[key]
             max_key_length = max(max_key_length, len(key))
             
    for key, value in sorted(filtered_items.items()):
        if 'api_key' in key and value and value not in ['your_api_key_here', 'your_azure_api_key_here']:
            displayed_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
        else:
            displayed_value = value
        click.echo(f"{key.ljust(max_key_length + 2)}: {displayed_value}")

@config.command(name="set-context-messages")
@click.argument('count', type=int)
def set_context_messages(count):
    """Set the maximum number of messages to keep in context.
    
    COUNT is the number of messages to keep (minimum: 1).
    """
    if count < 1:
        click.echo(click.style("Error: Message count must be at least 1.", fg='red'))
        return
        
    config = Config()
    if config.set_value('context.max_messages', count):
        click.echo(click.style(f"Maximum context messages set to {count}", fg='green'))
    else:
        click.echo(click.style("Failed to update configuration", fg='red'))

@config.command(name="get-context-messages")
def get_context_messages():
    """Get the current maximum number of messages kept in context."""
    config = Config()
    max_messages = config.get_max_context_messages()
    click.echo(f"Maximum context messages: {max_messages}")

@cli.group()
def tools():
    """Manage available tools."""
    pass
    
@tools.command('list')
def list_tools():
    """List all available tools."""
    config = Config()
    tools = config.get_tools()
    
    if not tools:
        click.echo("No tools configured.")
        return
        
    click.echo("Available tools:")
    for tool in tools:
        click.echo(f"  - {tool}")
        
@tools.command('add')
@click.argument('tool_name')
def add_tool(tool_name):
    """Add a tool to the available tools list."""
    config = Config()
    if config.add_tool(tool_name):
        click.echo(click.style(f"Tool '{tool_name}' added successfully.", fg='green'))
    else:
        click.echo(click.style(f"Tool '{tool_name}' already exists or could not be added.", fg='yellow'))
        
@tools.command('del')
@click.argument('tool_name')
def delete_tool(tool_name):
    """Remove a tool from the available tools list."""
    config = Config()
    if config.remove_tool(tool_name):
        click.echo(click.style(f"Tool '{tool_name}' removed successfully.", fg='green'))
    else:
        click.echo(click.style(f"Tool '{tool_name}' does not exist or could not be removed.", fg='yellow'))

# Make the script executable
if __name__ == '__main__':
    cli()
