# CMDLLM

cmdllm 是一个使用自然语言与命令行工具交互的智能接口。它支持**任何**命令行工具，如 bash、kubectl、ros2 等。它利用大型语言模型 (LLM) 将你的自然语言查询转换为相应的命令，并提供执行这些命令的选项。

> 开发这个工具最初的目的是为了帮助我自己快速使用podman命令行而开发的，由于新公司不能使用 docker命令行，从 docker 切换成 podman 一直不太习惯，就尝试开发这个工具，经过几次更新之后决定开源出来，希望正在阅读这段文字的你也会有用。

## 功能

* **多工具支持**: 支持任何命令行工具，如 Bash、kubectl、ros2、docker 等。
* **自然语言处理**: 将日常语言翻译成对应工具的命令。
* **命令执行**: 可以选择直接执行建议的命令。
* **上下文管理**: 维护对话历史，以支持更复杂的交互。
* **安全提示**: 对可能危险的操作（如删除数据）进行警告和确认。
* **交互式会话**: 支持交互式会话模式和单次查询模式。
* **命令行配置**: 提供方便的命令行配置管理，无需手动编辑配置文件。
* **多 LLM 提供商**: 支持兼容 OpenAI API 的服务和 Azure OpenAI 服务（如 OpenAI、DeepSeek 等）。

## 安装

### 从 PyPI 安装

```bash
pip install cmdllm
```

### 从源代码安装

```bash
git clone https://github.com/yexia553/cmdllm.git
cd cmdllm
pip install -e .
```

## 使用

### 基本使用

CMDLLM 提供了交互式会话模式：

#### 交互式会话模式

启动一个与特定工具的交互式会话：

```bash
cmdllm chat -t bash
```

这将启动一个交互式会话，你可以连续输入多个查询，程序会保持上下文。输入 `exit` 或 `quit` 退出会话。

#### bash 交互式会话示例

```bash
$ cmdllm chat -t bash
Starting interactive bash session. Type 'exit' or 'quit' to end.
-----------------------------------------------------
bash> 列出当前目录中的所有文件
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
bash> 创建一个名为test的目录
Processing your query...

Suggested command:
  mkdir test

Execution result:

-----------------------------------------------------
bash> exit
Exiting chat session.
```

#### kubectl 交互式会话示例

```bash
$ cmdllm chat -t kubectl
Starting interactive kubectl session. Type 'exit' or 'quit' to end.
-----------------------------------------------------
kubectl> 列出所有的命名空间
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
kubectl> 查看 default 命名空间中的所有 pod
Processing your query...

Suggested command:
  kubectl get pods -n default

Execution result:
NAME                           READY   STATUS    RESTARTS   AGE
nginx-deployment-66b6c48dd5-8ph2j   1/1     Running   0          24h
nginx-deployment-66b6c48dd5-vb6l8   1/1     Running   0          24h
-----------------------------------------------------
kubectl> 描述第一个 nginx pod
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

## 配置

CMDLLM 提供了便捷的命令行配置管理，无需手动编辑配置文件。

### 交互式配置

最简单的方式是使用交互式配置命令来设置 LLM 提供商：

```bash
cmdllm config setup
```

这将引导你设置所有必要的 LLM 配置项，如 API 密钥、端点、模型或部署名称。你可以选择使用兼容 OpenAI API 的服务或 Azure OpenAI 服务。

### 命令行工具管理

CMDLLM 提供了专门的命令用于管理可用的命令行工具:

```bash
# 查看所有可用的工具
cmdllm tools list

# 添加新工具
cmdllm tools add kubectl

# 删除工具
cmdllm tools del kubectl
```

### 配置 Azure OpenAI

`cmdllm config setup` 可以帮助你交互是配置，但是如果你想单独配置或者修改某一个选项，可以使用以下命令手动配置：

```bash
# 设置 LLM 提供商为 Azure
cmdllm config set llm_provider azure

# 配置 Azure OpenAI 参数，记得把最后的值换成你的真实值
cmdllm config set azure.api_key YOUR_AZURE_API_KEY
cmdllm config set azure.endpoint https://your-resource-name.openai.azure.com
cmdllm config set azure.deployment your-deployment-name
cmdllm config set azure.api_version 2023-05-15
```

### 配置兼容 OpenAI API 的服务

如果你想使用兼容 OpenAI API 的服务（如 OpenAI、DeepSeek 等）：

```bash
# 设置 LLM 提供商为 OpenAI 兼容
cmdllm config set llm_provider openai_compatible

# 配置 OpenAI 兼容参数，记得把最后的值换成你的真实值
cmdllm config set openai_compatible.api_key YOUR_API_KEY
cmdllm config set openai_compatible.base_url https://api.openai.com/v1
cmdllm config set openai_compatible.model gpt-3.5-turbo
```

### 管理上下文消息数量

你可以设置对话中携带的最大消息数量，默认是 20：

```bash
# 设置上下文消息数量
cmdllm config set-context-messages 10

# 查看当前上下文消息设置
cmdllm config get-context-messages
```

### 查看当前配置

```bash
cmdllm config list
```

### 获取单个配置项

```bash
cmdllm config get llm_provider
cmdllm config get azure.endpoint
```

### 重置配置

```bash
cmdllm config init
```

### 手动编辑配置文件

如果你仍然想手动编辑配置文件，CMDLLM 的配置文件位于 `~/.cmdllm/config.yaml`：

```yaml
tools:
- bash
- kubectl
- ros2

llm_provider: openai_compatible  # 使用的 LLM 提供商: openai_compatible 或 azure

openai_compatible:
  base_url: https://api.openai.com/v1  # OpenAI 兼容 API 端点
  api_key: 你的API密钥  # API 密钥
  model: gpt-3.5-turbo  # 使用的模型

azure:
  api_key: 你的Azure密钥  # Azure OpenAI API 密钥
  endpoint: https://your-resource-name.openai.azure.com  # Azure 端点
  deployment: your-deployment-name  # Azure 模型部署名称
  api_version: 2023-05-15  # Azure API 版本

context:
  max_messages: 10  # 保存在上下文中的最大消息数量
```

支持的 LLM 服务：
- 兼容 OpenAI API 的服务（如 OpenAI、DeepSeek 等）
- Azure OpenAI


## 清除上下文

```bash
$ cmdllm clear
Context has been successfully cleared.
```

## 注意事项

- 使用前需确保相应的命令行工具已经安装在你的系统上并在 PATH 中可用。
- 某些操作可能需要管理员权限。
- **大模型生成的命令在执行之前由大模型判断是否具有危险，这个过程存在一定的安全问题**

## 博客

这是我的个人博客: [https://panzhixiang.cn](https://panzhixiang.cn)

## 其他我开发的产品/工具

1. 这P班上的值不值

   <img src="./images/preview.jpg" alt="这P班上的值不值" style="width: 30%; height: auto;">
 
   网页版：[https://jobworth.panzhixiang.cn/](https://jobworth.panzhixiang.cn/)  
   微信小程序版：   
   <img src="./images/miniprogram_code.png" alt="这P班上的值不值" style="width: 30%; height: auto;">

2. 大模型多智能体信息网站

    [https://llmmultiagents.com/](https://llmmultiagents.com/)

## 许可证

本项目采用 Apache 2.0 许可证 - 详情请见 [LICENSE](./LICENSE) 文件。
