# CMDLLM

[中文](./README-zh.md)

CMDLLM is an intelligent interface for interacting with command-line tools using natural language. It supports **any** command-line tool, such as bash, kubectl, ros2, etc. It leverages Large Language Models (LLM) to translate your natural language queries into corresponding commands and provides options to execute these commands.

> The original purpose of developing this tool was to help myself quickly use the podman command line. Since my new company doesn't allow the use of docker commands, I was struggling to adapt from docker to podman. So I tried to develop this tool, and after several updates, I decided to open-source it. I hope it will be useful to you.

## Features

* **Multi-tool Support**: Works with any command-line tool, such as Bash, kubectl, ros2, docker, etc.
* **Natural Language Processing**: Translates everyday language into corresponding tool commands.
* **Command Execution**: Offers the option to directly execute suggested commands.
* **Context Management**: Maintains conversation history to support more complex interactions.
* **Safety Prompts**: Provides warnings and confirmations for potentially dangerous operations (like deleting data).
* **Interactive Sessions**: Supports both interactive session mode and one-time query mode.
* **Command-line Configuration**: Provides convenient command-line configuration management without the need to manually edit configuration files.
* **Multiple LLM Providers**: Supports OpenAI API-compatible services and Azure OpenAI services (such as OpenAI, DeepSeek, etc.).

## Installation

### From PyPI

```bash
pip install cmdllm
```

### From Source Code

```bash
git clone https://github.com/yexia553/cmdllm.git
cd cmdllm
pip install -e .
```

## Usage

### Basic Usage

CMDLLM provides an interactive session mode:

#### Interactive Session Mode

Start an interactive session with a specific tool:

```bash
cmdllm chat -t bash
```

This will start an interactive session where you can input multiple queries continuously, and the program will maintain the context. Type `exit` or `quit` to end the session.

#### Bash Interactive Session Example

```bash
$ cmdllm chat -t bash

Starting interactive bash session. Type 'exit' or 'quit' to end.
-----------------------------------------------------
bash> List all files in the current directory
Processing your query...

Suggested command:
  ls -la

Execution result:
total 64
drwxr-xr-x  15 user  staff   480  5 Jun 15:30 .
drwxr-xr-x  25 user  staff   800  5 Jun 14:22 ..
-rw-r--r--   1 user  staff  1550  5 Jun 15:30 LICENSE
-rw-r--r--   1 user  staff   133  5 Jun 15:30 MANIFEST.in
-rw-r--r--   1 user  staff  3122  5 Jun 15:30 README.md
...

-----------------------------------------------------
bash> Create a directory named test

Processing your query...

Suggested command:
  mkdir test

Execution result:

-----------------------------------------------------
bash> exit
Exiting chat session.
```

#### Kubectl Interactive Session Example

```bash
$ cmdllm chat -t kubectl

Starting interactive kubectl session. Type 'exit' or 'quit' to end.
-----------------------------------------------------
kubectl> List all namespaces
Processing your query...

Suggested command:
  kubectl get namespaces

Execution result:
NAME              STATUS   AGE
default           Active   45d
kube-node-lease   Active   45d
kube-public       Active   45d
kube-system       Active   45d
-----------------------------------------------------
kubectl> Show all pods in the default namespace
Processing your query...

Suggested command:
  kubectl get pods -n default

Execution result:
NAME                           READY   STATUS    RESTARTS   AGE
nginx-deployment-66b6c48dd5-8ph2j   1/1     Running   0          24h
nginx-deployment-66b6c48dd5-vb6l8   1/1     Running   0          24h
-----------------------------------------------------
kubectl> Describe the first nginx pod

Processing your query...

Suggested command:
  kubectl describe pod nginx-deployment-66b6c48dd5-8ph2j -n default

Execution result:
Name:             nginx-deployment-66b6c48dd5-8ph2j
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Thu, 21 Mar 2024 09:30:42 +0800
...
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  24h   default-scheduler  Successfully assigned default/nginx-deployment-66b6c48dd5-8ph2j to minikube
  Normal  Pulled     24h   kubelet            Container image "nginx:1.14.2" already present on machine
  Normal  Created    24h   kubelet            Created container nginx
  Normal  Started    24h   kubelet            Started container nginx
-----------------------------------------------------
kubectl> exit
Exiting chat session.
```

## Configuration

CMDLLM provides convenient command-line configuration management without the need to manually edit configuration files.

### Interactive Configuration

The simplest way is to use the interactive configuration command to set up the LLM provider:

```bash
cmdllm config setup
```

This will guide you through setting up all necessary LLM configuration items, such as API keys, endpoints, model or deployment names. You can choose to use either OpenAI API-compatible services or Azure OpenAI services.

### Command-line Tool Management

CMDLLM provides dedicated commands for managing available command-line tools:

```bash
# View all available tools
cmdllm tools list

# Add a new tool
cmdllm tools add kubectl

# Remove a tool
cmdllm tools del kubectl
```

### Configuring Azure OpenAI

`cmdllm config setup` can help you configure interactively, but if you want to configure or modify a single option, you can use the following commands to configure manually:

```bash
# Set LLM provider to Azure
cmdllm config set llm_provider azure

# Configure Azure OpenAI parameters, remember to replace the values with your actual values
cmdllm config set azure.api_key YOUR_AZURE_API_KEY
cmdllm config set azure.endpoint https://your-resource-name.openai.azure.com
cmdllm config set azure.deployment your-deployment-name
cmdllm config set azure.api_version 2023-05-15
```

### Configuring OpenAI API-compatible Services

If you want to use OpenAI API-compatible services (such as OpenAI, DeepSeek, etc.):

```bash
# Set LLM provider to OpenAI compatible
cmdllm config set llm_provider openai_compatible

# Configure OpenAI compatible parameters, remember to replace the values with your actual values
cmdllm config set openai_compatible.api_key YOUR_API_KEY
cmdllm config set openai_compatible.base_url https://api.openai.com/v1
cmdllm config set openai_compatible.model gpt-3.5-turbo
```

### Managing Context Message Count

You can set the maximum number of messages carried in the conversation, default is 20:

```bash
# Set context message count
cmdllm config set-context-messages 10

# View current context message setting
cmdllm config get-context-messages
```

### View Current Configuration

```bash
cmdllm config list
```

### Get Individual Configuration Item

```bash
cmdllm config get llm_provider
cmdllm config get azure.endpoint
```

### Reset Configuration

```bash
cmdllm config init
```

### Manually Edit Configuration File

If you still want to manually edit the configuration file, CMDLLM's configuration file is located at `~/.cmdllm/config.yaml`:

```yaml
tools:
- bash
- kubectl
- ros2

llm_provider: openai_compatible  # LLM provider being used: openai_compatible or azure

openai_compatible:
  base_url: https://api.openai.com/v1  # OpenAI compatible API endpoint
  api_key: your_API_key  # API key
  model: gpt-3.5-turbo  # Model being used

azure:
  api_key: your_Azure_key  # Azure OpenAI API key
  endpoint: https://your-resource-name.openai.azure.com  # Azure endpoint
  deployment: your-deployment-name  # Azure model deployment name
  api_version: 2023-05-15  # Azure API version

context:
  max_messages: 10  # Maximum number of messages saved in context
```

Supported LLM services:
- OpenAI API-compatible services (such as OpenAI, DeepSeek, etc.)
- Azure OpenAI

## Clearing Context

```bash
$ cmdllm clear
Context has been successfully cleared.
```

## Notes

- Before use, ensure that the corresponding command-line tools are installed on your system and available in the PATH.
- Some operations may require administrator privileges.
- **Commands generated by large language models are assessed for risk by the model itself before execution, but this process has certain security issues**

## Blog

here is my personal blog: [https://panzhixiang.cn](https://panzhixiang.cn)

## Other products/tools I've developed.

1. 这P班上的值不值

   <img src="./images/preview.jpg" alt="这P班上的值不值" style="width: 30%; height: auto;">
 
   网页版：[https://jobworth.panzhixiang.cn/](https://jobworth.panzhixiang.cn/)  
   微信小程序版：   
   <img src="./images/miniprogram_code.png" alt="这P班上的值不值" style="width: 30%; height: auto;">

2. 大模型多智能体信息网站

    [https://llmmultiagents.com/](https://llmmultiagents.com/)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](./LICENSE) file for details. 