---
name: provider-manager
description: 管理和添加新的 LLM Provider 的自动化工具。当需要添加新的 LLM provider（如 OpenAI、Anthropic、自定义 API 等）到 nanobot 项目时，应使用此 skill。此技能提供完整的 workflow，包括配置文件修改、代码生成、文档更新和自动化补丁脚本生成。
---

# Provider Manager Skill

此技能提供完整的 LLM Provider 管理功能，简化向 nanobot 添加新 provider 的流程。

## 何时使用

当需要执行以下任一任务时，应使用此技能：

- 添加新的 LLM provider（如自定义 API 端点）
- 修改现有 provider 配置
- 生成 provider 相关的自动化补丁脚本
- 更新 provider 文档

## 核心工作流程

### 步骤 1: 收集 Provider 信息

通过交互式方式收集以下信息：

1. **基本信息**
   - Provider 名称（小写，如 "longcat"）
   - Provider 显示名称（如 "LongCat"）
   - Provider 描述（如 "自定义 API"）
   - API 端点 URL（如 "https://api.longcat.chat/openai"）

2. **技术特性**
   - 是否使用 OpenAI 兼容接口？(Y/N)
   - 模型命名规则（如 "gpt-4", "claude-3"）
   - 特殊配置需求（如 API Key 前缀、请求头等）

3. **文档信息**
   - 官方文档 URL
   - API Key 获取地址
   - 示例模型列表

### 步骤 2: 修改代码文件

使用 `scripts/add_provider.py` 脚本自动修改以下文件：

#### 2.1 更新 `nanobot/config/schema.py`

**必需修改：**

1. 在 `ProvidersConfig` 类中添加 provider 字段：
   ```python
   provider_name: ProviderConfig = Field(default_factory=ProviderConfig)
   ```

2. 在 `_match_provider` 方法的 `providers` 字典中添加映射：
   ```python
   "provider_name": self.providers.provider_name,
   ```

3. 在 `get_api_key` 方法中添加到遍历列表：
   ```python
   self.providers.provider_name,
   ```

4. 在 `get_api_base` 方法中添加条件判断：
   ```python
   if "provider_name" in model:
       return self.providers.provider_name.api_base
   ```

#### 2.2 更新 `nanobot/providers/litellm_provider.py`

**OpenAI 兼容 provider 的修改：**

1. 添加检测逻辑：
   ```python
   self.is_provider_name = bool(api_base) and "provider_keyword" in api_base.lower()
   ```

2. 更新 `is_vllm` 条件，排除新 provider：
   ```python
   self.is_vllm = bool(api_base) and not self.is_openrouter and not self.is_longcat and not self.is_provider_name
   ```

3. 更新 OpenAI client 创建条件：
   ```python
   if self.is_longcat or self.is_vllm or self.is_provider_name:
   ```

4. 在 `chat` 方法中添加模型名称处理（如需要）

#### 2.3 更新 `README.md`

在 providers 表格中添加新行：
```markdown
| `provider_name` | LLM (描述) | [官方文档](URL) |
```

### 步骤 3: 生成自动化补丁脚本

使用 `scripts/generate_patch.py` 生成 provider 特定的补丁脚本：

- 生成 `apply_[provider]_patch.py`
- 包含所有必要的文件修改
- 支持自动化应用和回滚

### 步骤 4: 验证和测试

1. **语法检查**
   ```bash
   python -m py_compile nanobot/config/schema.py
   python -m py_compile nanobot/providers/litellm_provider.py
   ```

2. **运行补丁脚本**
   ```bash
   python scripts/apply_[provider]_patch.py
   ```

3. **配置验证**
   - 确保 `config.json` 中包含新 provider 配置
   - 检查 API Key 和 Base URL 格式

### 步骤 5: 更新文档

更新以下文档（可选但推荐）：

1. `workspace/ADD_PROVIDER.md` - 添加 provider 配置示例
2. `workspace/skills/provider-manager/references/providers.md` - 记录 provider 信息

## 脚本使用指南

### `scripts/add_provider.py`

交互式添加新 provider：

```bash
python workspace/skills/provider-manager/scripts/add_provider.py
```

脚本会引导用户完成：
- 输入 provider 信息
- 自动修改代码文件
- 生成补丁脚本
- 创建配置模板

### `scripts/generate_patch.py`

从现有 provider 生成补丁脚本：

```bash
python workspace/skills/provider-manager/scripts/generate_patch.py --provider longcat
```

### `scripts/validate_provider.py`

验证 provider 配置：

```bash
python workspace/skills/provider-manager/scripts/validate_provider.py --provider longcat
```

## 最佳实践

### 1. 命名约定

- Provider 名称使用小写，如 `longcat`、`openai`
- 变量名使用蛇形命名，如 `is_longcat`
- 模型名称遵循 provider 命名规范

### 2. 代码组织

- 将所有 provider 相关代码放在一个函数中
- 使用统一的错误处理
- 添加详细的注释说明

### 3. 测试策略

1. 单元测试：测试每个修改点
2. 集成测试：测试完整流程
3. 回归测试：确保现有 provider 不受影响

### 4. 文档化

- 更新 README.md
- 记录特殊配置需求
- 提供示例代码

## 参考资源

### 必读文件

1. `references/provider-pattern.md` - Provider 实现模式和最佳实践
2. `references/code-templates.md` - 代码修改模板
3. `references/existing-providers.md` - 现有 provider 列表和配置

### 示例

参考 `longcat` provider 的完整实现：
- 配置：`nanobot/config/schema.py` (搜索 `longcat`)
- 实现：`nanobot/providers/litellm_provider.py` (搜索 `is_longcat`)
- 文档：`README.md` (搜索 `longcat`)
- 补丁：`scripts/apply_longcat_patch.py`

## 故障排除

### 常见问题

**Q: 修改后代码无法运行？**
A: 检查语法错误，运行 `python -m py_compile` 验证

**Q: API 调用失败？**
A: 检查 `config.json` 中的 API Key 和 Base URL 是否正确

**Q: 模型名称不匹配？**
A: 查看 provider 文档，确认模型命名规范

### 回滚操作

如果添加 provider 后出现问题：

```bash
# 查看修改
git diff

# 回滚特定文件
git restore nanobot/config/schema.py
git restore nanobot/providers/litellm_provider.py

# 完全回滚
git reset --hard HEAD
```

## 扩展此技能

要添加新的 provider 特定功能：

1. 在 `references/` 中添加新文档
2. 在 `scripts/` 中添加新脚本
3. 更新 SKILL.md 中的工作流程

此技能旨在持续改进，基于实际使用反馈进行迭代优化。
