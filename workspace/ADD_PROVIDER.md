# 添加 Provider 流程指南

> 记录添加 OpenAI 兼容 API Provider（如 longcat）的完整流程

## 1. 更新配置 Schema

**文件**: `nanobot/config/schema.py`

### 1.1 添加 Provider 配置类

```python
class ProviderConfig(BaseModel):
    apiKey: str = ""
    apiBase: str | None = None
```

### 1.2 在 ProvidersConfig 中注册

```python
class ProvidersConfig(BaseModel):
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig)
    openai: ProviderConfig = Field(default_factory=ProviderConfig)
    openrouter: ProviderConfig = Field(default_factory=ProviderConfig)
    groq: ProviderConfig = Field(default_factory=ProviderConfig)
    zhipu: ProviderConfig = Field(default_factory=ProviderConfig)
    vllm: ProviderConfig = Field(default_factory=ProviderConfig)
    gemini: ProviderConfig = Field(default_factory=ProviderConfig)
    longcat: ProviderConfig = Field(default_factory=ProviderConfig)  # 新增
```

### 1.3 更新 get_api_key() 方法

```python
def get_api_key(self) -> str | None:
    """Get the first available API key from configured providers."""
    # 按优先级顺序检查
    providers = ["longcat", "openrouter", "anthropic", "openai", "groq", "zhipu", "gemini"]
    for name in providers:
        if key := getattr(self.providers, name).apiKey:
            return key
    return None
```

### 1.4 更新 get_api_base() 方法

```python
def get_api_base(self) -> str | None:
    """Get the API base URL from configured providers."""
    # 按优先级顺序检查
    providers = ["longcat", "openrouter", "vllm", "anthropic", "openai", "groq", "zhipu", "gemini"]
    for name in providers:
        if api_base := getattr(self.providers, name).apiBase:
            return api_base
    return None
```

---

## 2. 更新 LiteLLM Provider

**文件**: `nanobot/providers/litellm_provider.py`

### 2.1 检测 Provider 类型

```python
# 在 __init__ 中添加检测逻辑
self.is_longcat = bool(api_base) and "longcat" in api_base.lower()
```

### 2.2 创建 OpenAI Client（针对 OpenAI 兼容端点）

```python
if self.is_longcat or self.is_vllm:
    self._openai_client = openai.AsyncOpenAI(
        api_key=api_key or "not-needed",
        base_url=api_base
    )
else:
    self._openai_client = None
```

### 2.3 在 chat() 方法中使用直接调用

```python
async def chat(self, messages, tools=None, model=None, ...):
    # ... model 前缀处理 ...
    
    # 使用原生 OpenAI client 调用
    if self._openai_client:
        try:
            create_kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if tools:
                create_kwargs["tools"] = tools
                create_kwargs["tool_choice"] = "auto"

            response = await self._openai_client.chat.completions.create(**create_kwargs)
            return self._parse_openai_response(response)
        except Exception as e:
            return LLMResponse(content=f"Error: {str(e)}", finish_reason="error")
```

---

## 3. 更新 CLI Status 命令

**文件**: `nanobot/cli/commands.py`

在 `status()` 函数中添加 provider 检查：

```python
has_longcat = bool(config.providers.longcat.api_key)
console.print(f"LongCat API: {'✓' if has_longcat else '[dim]not set[/dim]'}")
```

---

## 4. 测试步骤

### 4.1 清除缓存和会话

```bash
# 删除会话文件
rm ~/.nanobot/sessions/cli_direct.jsonl

# 清除 Python 缓存
rm -rf nanobot/__pycache__ nanobot/*/__pycache__
```

### 4.2 验证配置加载

```python
from nanobot.config.loader import load_config
c = load_config()
print(c.providers.longcat.apiKey)  # 应显示 API Key
print(c.get_api_key())               # 应返回第一个可用的 key
```

### 4.3 验证 Provider 创建

```python
from nanobot.providers.litellm_provider import LiteLLMProvider
p = LiteLLMProvider(api_key="xxx", api_base="https://api.xxx.com", default_model="xxx")
print(p.is_longcat)      # 应为 True
print(p._openai_client)  # 应不为 None
```

### 4.4 测试 API 调用

```bash
# 直接测试
python -c "
import httpx, asyncio
async def test():
    resp = await httpx.post('https://api.xxx.com/chat/completions',
        headers={'Authorization': 'Bearer YOUR_KEY'},
        json={'model': 'model-name', 'messages': [{'role': 'user', 'content': 'hi'}]})
    print(resp.status_code, resp.text[:200])
asyncio.run(test())
"
```

---

## 5. 添加新 Provider 检查清单

- [ ] 在 `ProvidersConfig` 添加 ProviderConfig 字段
- [ ] 更新 `get_api_key()` 方法
- [ ] 更新 `get_api_base()` 方法
- [ ] 在 `LiteLLMProvider.__init__` 添加检测逻辑
- [ ] 在 `LiteLLMProvider.chat` 添加调用逻辑
- [ ] 在 `status()` 命令添加状态显示
- [ ] 测试验证

---

## 常见问题

### 问题: "LLM Provider NOT provided"
**原因**: LiteLLM 的 acompletion 无法识别 provider
**解决**: 对 OpenAI 兼容端点使用原生 `openai.AsyncOpenAI` client

### 问题: 会话历史累积错误响应
**解决**: 清除 `~/.nanobot/sessions/cli_direct.jsonl`

### 问题: Model prefix 不兼容
**解决**: OpenAI 兼容端点直接使用模型名称，不添加任何前缀

---

## 6. 示例配置 (config.json)

```json
{
  "agents": {
    "defaults": {
      "model": "LongCat-Flash-Chat"
    }
  },
  "providers": {
    "longcat": {
      "apiKey": "ak_xxx",
      "apiBase": "https://api.longcat.chat/openai"
    }
  }
}
```
