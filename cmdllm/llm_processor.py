"""
LLM Processing module for cmdllm.

This module handles the interaction with the Language Model API,
processing natural language queries and generating appropriate
commands based on the user's input and the configured tool.
"""

from openai import OpenAI, AzureOpenAI

class LLMProcessor:
    """Processes natural language queries using LLM for the configured tool."""

    def __init__(self, config, tool_type):
        """Initialize LLM processor with configuration and specified tool type."""
        self.provider = config.get_llm_provider()
        self.openai_compatible_config = config.get_openai_compatible_config()
        self.azure_config = config.get_azure_config()
        self.tool_type = tool_type
        
        # Initialize different clients based on provider type
        if self.provider == 'azure':
            self._init_azure_client()
        else:
            self._init_openai_compatible_client()

    def _init_openai_compatible_client(self):
        """Initialize OpenAI-compatible client."""
        # Ensure standard API key exists
        api_key = self.openai_compatible_config.get('api_key')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("API key not found in configuration. Please set it using: cmdllm config set openai_compatible.api_key YOUR_API_KEY")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=api_key, 
            base_url=self.openai_compatible_config.get('base_url')
        )
        self.model = self.openai_compatible_config.get('model', 'deepseek-chat')

    def _init_azure_client(self):
        """Initialize Azure OpenAI client."""
        # Check if Azure configuration is complete
        api_key = self.azure_config.get('api_key')
        endpoint = self.azure_config.get('endpoint')
        deployment = self.azure_config.get('deployment')
        
        if not api_key or api_key == 'your_azure_api_key_here':
            raise ValueError("Azure API key not found. Please set it using: cmdllm config set azure.api_key YOUR_AZURE_API_KEY")
        
        if not endpoint or endpoint == 'https://your-resource-name.openai.azure.com':
            raise ValueError("Azure endpoint not configured. Please set it using: cmdllm config set azure.endpoint YOUR_ENDPOINT")
            
        if not deployment or deployment == 'your-deployment-name':
            raise ValueError("Azure deployment name not configured. Please set it using: cmdllm config set azure.deployment YOUR_DEPLOYMENT_NAME")
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=self.azure_config.get('api_version', '2023-05-15')
        )
        self.model = deployment  # Azure uses deployment name instead of model

    def _get_system_prompt(self):
        """
        Generate a system prompt based on the configured tool.
        
        Returns:
            str: The system prompt for the LLM.
        """
        return f"""You are a {self.tool_type} expert. Analyze the user's query and respond appropriately:

            1. If the user is asking for a {self.tool_type} command or operation:
            - Convert the query into the appropriate {self.tool_type} command.
            - If the command is potentially dangerous (e.g., removes data, deletes resources, modifies system files), set DANGEROUS to true.
            - Format your response exactly as:
            COMMAND: <the {self.tool_type} command>
            DANGEROUS: <true/false>

            2. If the user is asking a general question about {self.tool_type}:
            - Provide a clear and concise answer.
            - Format your response exactly as:
            ANSWER: <your detailed explanation>

            IMPORTANT: Only provide the command or the answer, following the exact format. Do not add extra explanations unless asked.
            Respond in Chinese.
            """

    def process_query(self, query, context=None):
        """
        Process a natural language query and return the corresponding command or answer.

        Args:
            query (str): The natural language query.
            context (str, optional): Previous conversation context.

        Returns:
            tuple: (response_type, response)
                - response_type (str): Either 'command' or 'answer'.
                - response (str or tuple): The generated command (with danger flag) or answer.
        """
        # Construct the prompt with dynamic tool information
        system_prompt = self._get_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # context is now expected to be a list of message dictionaries or None
        if context:
            # Extend the messages list with the history from context_manager
            messages.extend(context)

        # Add the current user query
        messages.append({"role": "user", "content": query})

        try:
            # Get response from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Keep low for consistency
            )

            # Parse the response
            response_text = response.choices[0].message.content.strip()

            # More robust parsing
            command = None
            is_dangerous = False
            answer = None

            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('COMMAND:'):
                    command = line.replace('COMMAND:', '').strip()
                elif line.startswith('DANGEROUS:'):
                    is_dangerous = line.replace('DANGEROUS:', '').strip().lower() == 'true'
                elif line.startswith('ANSWER:'):
                    answer = line.replace('ANSWER:', '').strip()

            if command:
                # Basic validation: ensure command is not empty
                if not command:
                    return 'answer', "LLM returned an empty command."
                return 'command', (command, is_dangerous)
            elif answer:
                 # Basic validation: ensure answer is not empty
                if not answer:
                    return 'answer', "LLM returned an empty answer."
                return 'answer', answer
            else:
                # If parsing fails, return the raw response as an answer
                return 'answer', f"LLM response did not follow the expected format:\n{response_text}"

        except Exception as e:
            # Handle potential API errors or other issues
            return 'answer', f"Error processing query with LLM: {str(e)}" 