# Provider 实现模式

本文档描述向 nanobot 添加新 LLM Provider 的标准模式和最佳实践。

## 核心概念

### 1. Provider 分类

根据 API 兼容性，provider 分为两类：

#### OpenAI 兼容 Provider
- 使用标准 OpenAI API 格式
- 示例：LongCat, vLLM, 自定义 OpenAI 代理
- 实现：使用 `_openai_client` 直接调用

#### LiteLLM Provider
- 通过 LiteLLM 统一接口调用
- 示例：OpenAI, Anthropic, Gemini, DeepSeek
- 实现：使用 `litellm.acompletion()`

## 代码修改模式

### 模式 1: 添加配置字段

在 `nanobot/config/schema.py` 的 `ProvidersConfig` 类中添加：

```python
class ProvidersConfig(BaseModel):
    """Configuration for LLM providers."""
    # ... 现有 providers ...
    provider_name: ProviderConfig = Field(default_factory=ProviderConfig)
```

### 模式 2: 添加 Provider 映射

在 `_match_provider` 方法的 `providers` 字典中添加：

```python
def _match_provider(self, model: str | None = None) -> ProviderConfig | None:
    providers = {
        # ... 现有映射 ...
        "provider_name": self.providers.provider_name,
    }
```

### 模式 3: 添加 API Key 遍历

在 `get_api_key` 方法中添加：

```python
def get_api_key(self, model: str | None = None) -> str | None:
    # ... 匹配逻辑 ...
    for provider in [
        # ... 现有 providers ...
        self.providers.provider_name,
    ]:
        if provider.api_key:
            return provider.api_key
```

### 模式 4: 添加 API Base 判断

在 `get_api_base` 方法中添加：

```python
def get_api_base(self, model: str | None = None) -> str | None:
    model = (model or self.agents.defaults.model).lower()
    if "provider_name" in model:
        return self.providers.provider_name.api_base
    # ... 其他条件 ...
```

## LiteLLM Provider 实现

### 模式 1: 添加检测逻辑

在 `__init__` 方法中：

```python
# Detect ProviderName by api_base
self.is_provider_name = bool(api_base) and "provider_keyword" in api_base.lower()
```

### 模式 2: 更新 OpenAI Client 条件

```python
# Create OpenAI client for OpenAI-compatible endpoints
if self.is_longcat or self.is_vllm or self.is_provider_name:
    self._openai_client = openai.AsyncOpenAI(
        api_key=api_key or "not-needed",
        base_url=api_base
    )
```

### 模式 3: 添加模型名称处理

在 `chat` 方法中（如果需要）：

```python
# For provider_name, remove any provider prefix and use raw model name
if self.is_provider_name:
    if model.startswith("openai/"):
        model = model[7:]
```

## 命名约定

### Provider 名称
- 小写，短名称：`longcat`, `openai`, `anthropic`
- 使用连字符：`open-router`（不是 `openrouter`）

### 变量名
- 检测变量：`is_provider_name`
- 配置变量：`self.providers.provider_name`

### 模型名称
- 遵循 provider 的命名规范
- 示例：`gpt-4`, `claude-3-opus`, `longcat-flash`

## 测试清单

### 代码级测试
- [ ] Python 语法检查：`python -m py_compile`
- [ ] 导入测试：`python -c "from nanobot.config.schema import Config"`
- [ ] 实例化测试：`python -c "from nanobot.providers.litellm_provider import LiteLLMProvider"`

### 功能测试
- [ ] 配置加载：使用新 provider 的 API Key
- [ ] API 调用：测试实际模型调用
- [ ] 错误处理：测试无效 API Key

### 集成测试
- [ ] CLI 命令：`nanobot agent -m "provider_name/model-name"`
- [ ] 多 provider：同时配置多个 provider
- [ ] 回滚测试：移除 provider 后重新添加

## 常见问题

### Q: 如何处理 provider 特殊认证？

A: 在 `litellm_provider.py` 的 `__init__` 方法中添加特殊逻辑：

```python
if "provider_name" in default_model:
    # 特殊认证逻辑
    headers = {"Authorization": f"Bearer {api_key}"}
    os.environ["PROVIDER_AUTH"] = api_key
```

### Q: 如何支持代理？

A: 在配置中添加代理设置：

```python
class ProviderConfig(BaseModel):
    api_key: str = ""
    api_base: str | None = None
    proxy_url: str | None = None  # 新增
```

### Q: 如何处理不同的 API 版本？

A: 在 `get_api_base` 中添加版本检测：

```python
if "provider_name" in model:
    # 检测版本并返回不同的 base URL
    if "v2" in model:
        return "https://api.v2.example.com"
    return self.providers.provider_name.api_base
```

## 示例

### 完整示例：添加 LongCat

参见以下文件的 `longcat` 相关代码：
- `nanobot/config/schema.py` - 配置模型
- `nanobot/providers/litellm_provider.py` - Provider 实现
- `README.md` - 文档

### 最小化示例：添加简单 API

如果只需要支持一个模型，最小修改：

1. `schema.py`: 添加字段和映射
2. `litellm_provider.py`: 添加检测和 client 创建
3. `config.json`: 配置 API Key

不需要修改 README 或生成补丁脚本。

## 扩展点

### 1. 添加自定义验证

在 `schema.py` 中：

```python
@field_validator('api_key')
def validate_api_key(cls, v):
    if v and not v.startswith('sk_'):
        raise ValueError('API key must start with sk_')
    return v
```

### 2. 添加健康检查

在 `litellm_provider.py` 中：

```python
async def health_check(self) -> bool:
    """检查 provider 是否可用"""
    try:
        response = await self._openai_client.models.list()
        return True
    except Exception:
        return False
```

### 3. 添加速率限制

在 `chat` 方法中：

```python
from datetime import datetime

@dataclass
class RateLimiter:
    last_call: datetime = None
    min_interval: float = 1.0  # 秒

rate_limiter = RateLimiter()
```

## 参考资料

- LiteLLM 文档：https://docs.litellm.ai/
- OpenAI API 参考：https://platform.openai.com/docs/api-reference
- Pydantic 文档：https://docs.pydantic.dev/
