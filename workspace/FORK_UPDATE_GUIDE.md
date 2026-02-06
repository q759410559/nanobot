# Fork 更新指南

## 问题描述

本项目是从开源项目 fork 而来，原项目每天都更新。我新增了 `longcat` provider 配置，每次更新时可能出现代码冲突。

## 🚀 解决方案：自动补丁脚本

### 方案说明

为了避免每次手动修改代码，创建了自动化补丁脚本。每次从上游更新后，只需运行脚本即可自动重新添加 longcat 支持。

**核心优势：**
- ✅ `config.json` 在 `.gitignore` 中，本地配置不会被跟踪
- ✅ 自动化脚本一键应用所有补丁
- ✅ 智能检测，避免重复应用
- ✅ 支持跨平台（Linux/Mac/Windows）

---

## 📋 快速开始

### 第一次配置（已完成）

1. ✅ `config.json` 已在 `.gitignore` 中
2. ✅ longcat 支持已添加到代码中
3. ✅ 自动补丁脚本已创建

### 日常更新流程

```bash
# 1. 从上游获取最新更新
git fetch upstream

# 2. 合并上游更新
git merge upstream/main

# 3. 一键应用 longcat 补丁
# Linux/Mac:
python scripts/apply_longcat_patch.py

# Windows:
python scripts\apply_longcat_patch.py

# 4. 提交修改
git add .
git commit -m "Apply longcat provider support patch"

# 5. 推送到你的远程仓库
git push origin lwk
```

---

## 🔧 补丁脚本说明

### 脚本位置
- **Python 版本**（推荐）：`scripts/apply_longcat_patch.py`
- **Shell 版本**（Linux/Mac）：`scripts/apply_longcat_patch.sh`
- **Batch 版本**（Windows）：`scripts/apply_longcat_patch.bat`

### 补丁内容

脚本会自动修改以下文件：

#### 1. `nanobot/providers/litellm_provider.py`
- 添加 `is_longcat` 检测逻辑
- 更新 OpenAI 客户端创建条件
- 添加 longcat 模型名称处理

#### 2. `nanobot/config/schema.py`
- 在 `ProvidersConfig` 中添加 `longcat` 字段
- 在 `_match_provider` 中添加映射
- 在 `get_api_key` 和 `get_api_base` 中添加支持

#### 3. `README.md`（可选）
- 在 providers 表格中添加 longcat 说明

---

## 📝 手动补丁（备用方案）

如果脚本运行失败，可以手动按照以下步骤添加：

### 修改 1: `nanobot/config/schema.py`

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

### 修改 2: `nanobot/providers/litellm_provider.py`

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

在 `chat` 方法中添加 longcat 模型处理：

```python
# For longcat, remove any provider prefix and use raw model name
if self.is_longcat:
    # Remove openai/ prefix if present
    if model.startswith("openai/"):
        model = model[7:]
```

---

## 📂 配置文件

### `config.json`（本地，不跟踪）

你的 `config.json` 示例：

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

**重要**：`config.json` 在 `.gitignore` 中，不会被提交到 git。

---

## 🔍 故障排除

### 问题 1：脚本运行失败

**解决方案**：
1. 检查 Python 是否安装：`python --version`
2. 确保在项目根目录运行
3. 手动应用补丁（参考上面的"手动补丁"章节）

### 问题 2：合并冲突

**解决方案**：
1. 查看冲突文件：`git status`
2. 解决冲突时，保留 longcat 相关代码
3. 运行补丁脚本确保所有修改都已应用
4. 标记冲突已解决：`git add <file>`

### 问题 3：补丁脚本找不到文件

**解决方案**：
- 确保在项目根目录运行脚本
- 检查文件路径是否正确

---

## 📚 最佳实践

### 定期更新

建议每天或每周定期从上游更新：

```bash
# 添加一个便捷别名到 ~/.bashrc 或 ~/.zshrc
alias update-nanobot='cd ~/nanobot && git fetch upstream && git merge upstream/main && python scripts/apply_longcat_patch.py'
```

### 提交前检查

每次应用补丁后，检查修改：

```bash
git diff
git status
```

### 备份配置

虽然 `config.json` 不会被跟踪，但建议定期备份：

```bash
cp config.json config.json.backup
```

---

## 🎯 总结

| 项目 | 状态 |
|------|------|
| `config.json` 在 `.gitignore` | ✅ 已保护 |
| 自动补丁脚本 | ✅ 已创建 |
| 中文语言支持 | ✅ 已配置 |
| 文档 | ✅ 已完善 |

**优势：**
- ✅ 自动化，避免手动重复操作
- ✅ 智能检测，避免重复应用
- ✅ 跨平台支持
- ✅ 配置安全，不会泄露 API Key
- ✅ 持续跟进上游更新

**工作流程：**
```
上游更新 → git merge → 运行补丁脚本 → 检查 → 提交 → 推送
```

这样你就可以持续从上游获取更新，同时保持 longcat provider 支持！
