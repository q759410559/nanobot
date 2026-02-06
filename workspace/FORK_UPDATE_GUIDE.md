# Fork 更新指南

## 问题描述

本项目是从开源项目 fork 而来，原项目每天都更新。我新增了 `longcat` provider 配置，每次更新时可能出现代码冲突。

## 解决方案

### 1. 配置文件保护

`config.json` 已经在 `.gitignore` 中，因此本地配置不会被 git 跟踪：

```gitignore
config.json  # 本地配置文件，不提交到仓库
```

**这确保了你的 longcat 配置永远不会被提交到仓库。**

### 2. 保持 longcat provider 支持

每次从上游合并时，如果上游删除了 longcat 相关代码，需要重新添加以下修改：

#### 修改 1: `nanobot/config/schema.py`

在 `ProvidersConfig` 类中添加 longcat 配置：

```python
class ProvidersConfig(BaseModel):
    """Configuration for LLM providers."""
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig)
    openai: ProviderConfig = Field(default_factory=ProviderConfig)
    openrouter: ProviderConfig = Field(default_factory=ProviderConfig)
    deepseek: ProviderConfig = Field(default_factory=ProviderConfig)
    groq: ProviderConfig = Field(default_factory=ProviderConfig)
    zhipu: ProviderConfig = Field(default_factory=ProviderConfig)
    vllm: ProviderConfig = Field(default_factory=ProviderConfig)
    gemini: ProviderConfig = Field(default_factory=ProviderConfig)
    longcat: ProviderConfig = Field(default_factory=ProviderConfig)  # 添加这一行
    moonshot: ProviderConfig = Field(default_factory=ProviderConfig)
```

在 `_match_provider` 方法中添加 longcat 映射：

```python
providers = {
    "openrouter": self.providers.openrouter,
    "deepseek": self.providers.deepseek,
    "anthropic": self.providers.anthropic,
    "claude": self.providers.anthropic,
    "openai": self.providers.openai,
    "gpt": self.providers.openai,
    "gemini": self.providers.gemini,
    "zhipu": self.providers.zhipu,
    "glm": self.providers.zhipu,
    "zai": self.providers.zhipu,
    "groq": self.providers.groq,
    "moonshot": self.providers.moonshot,
    "kimi": self.providers.moonshot,
    "vllm": self.providers.vllm,
    "longcat": self.providers.longcat,  # 添加这一行
}
```

在 `get_api_key` 方法中添加 longcat：

```python
for provider in [
    self.providers.openrouter, self.providers.deepseek,
    self.providers.anthropic, self.providers.openai,
    self.providers.gemini, self.providers.zhipu,
    self.providers.moonshot, self.providers.vllm,
    self.providers.groq, self.providers.longcat,  # 添加这一行
]:
```

在 `get_api_base` 方法中添加 longcat：

```python
if "longcat" in model:
    return self.providers.longcat.api_base
```

#### 修改 2: `nanobot/providers/litellm_provider.py`

在 `__init__` 方法中添加 longcat 检测：

```python
# Detect Longcat by api_base
self.is_longcat = bool(api_base) and "longcat" in api_base.lower()

# Track if using custom endpoint (vLLM, etc.) - excludes OpenRouter and Longcat
self.is_vllm = bool(api_base) and not self.is_openrouter and not self.is_longcat
```

```python
# Create OpenAI client for OpenAI-compatible endpoints (longcat, vLLM)
if self.is_longcat or self.is_vllm:
    self._openai_client = openai.AsyncOpenAI(
        api_key=api_key or "not-needed",
        base_url=api_base
    )
else:
    self._openai_client = None
```

### 3. 从上游更新的标准流程

```bash
# 1. 添加上游远程仓库（如果还没有）
git remote add upstream https://github.com/original-owner/nanobot.git

# 2. 获取上游更新
git fetch upstream

# 3. 合并上游更新到你的分支
git merge upstream/main

# 4. 如果有冲突，解决冲突
# - 查看冲突文件：git status
# - 手动编辑冲突文件，保留 longcat 相关代码
# - 标记冲突已解决：git add <file>

# 5. 提交合并
git commit -m "Merge upstream changes"

# 6. 推送到你的远程仓库
git push origin lwk
```

### 4. 处理合并冲突

如果上游更新删除了 longcat 相关代码，按照上面的"修改 1"和"修改 2"重新添加。

**重要提示**：
- `config.json` 永远不会被提交，所以你的 longcat 配置是安全的
- 只需要确保代码中保留了 longcat provider 的支持即可
- 你的本地 `config.json` 中的 longcat 配置不会受 git 操作影响

### 5. 配置文件示例

你的 `config.json` 可以这样配置（本地文件，不会被跟踪）：

```json
{
  "agents": {
    "defaults": {
      "workspace": "D:/Develop/PyCharmProject/nanobot/workspace",
      "model": "LongCat-Flash-Chat",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 20
    }
  },
  "providers": {
    "longcat": {
      "apiKey": "ak_1MI49U23U8if7tu8L31vc9qS6WV9p",
      "apiBase": "https://api.longcat.chat/openai"
    },
    "anthropic": {
      "apiKey": "",
      "apiBase": null
    },
    ...
  },
  ...
}
```

## 总结

1. ✅ `config.json` 在 `.gitignore` 中，本地配置安全
2. ✅ 代码中添加 longcat provider 支持
3. ✅ 每次从上游更新后，检查并保留 longcat 相关代码
4. ✅ 推送时不会包含敏感配置信息

这样你就可以持续从上游获取更新，同时保留你的 longcat 配置！
