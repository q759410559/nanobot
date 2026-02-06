# Findings: Provider Management Skill Research

## Research Notes

### 1. 当前 longcat Provider 实现

#### 文件 1: `nanobot/config/schema.py`
- 在 `ProvidersConfig` 类中添加 `longcat: ProviderConfig = Field(default_factory=ProviderConfig)`
- 在 `_match_provider` 方法的 `providers` 字典中添加 `"longcat": self.providers.longcat`
- 在 `get_api_key` 方法中添加 `self.providers.longcat` 到列表
- 在 `get_api_base` 方法中添加条件判断 `if "longcat" in model: return self.providers.longcat.api_base`

#### 文件 2: `nanobot/providers/litellm_provider.py`
- 在 `__init__` 中添加检测：`self.is_longcat = bool(api_base) and "longcat" in api_base.lower()`
- 更新 `is_vllm` 条件：排除 longcat
- 更新 OpenAI client 创建：`if self.is_longcat or self.is_vllm:`
- 在 `chat` 方法中添加模型名称处理逻辑

#### 文件 3: `README.md`
- 在 providers 表格中添加新行

### 2. 自动补丁脚本分析

文件：`scripts/apply_longcat_patch.py`

**核心函数：**
- `patch_litellm_provider()` - 修改 provider 实现
- `patch_schema()` - 修改配置 schema
- `patch_readme()` - 修改文档

**使用模式：**
- 正则表达式匹配和替换
- 智能检测避免重复应用
- 跨平台兼容

### 3. Skill 设计考虑

#### 需求分析
- **交互式**：用户输入 provider 名称、API URL、文档链接等
- **自动化**：自动修改所有必要文件
- **可配置**：生成 provider 特定的配置
- **文档化**：自动生成文档

#### 技术方案
- 使用 Python 的 `argparse` 或 `click` 处理命令行参数
- 使用 `jinja2` 或简单字符串模板生成代码
- 提供交互式和批处理两种模式

### 4. Potential Issues

1. **冲突检测**：需要检测文件是否已被修改
2. **回滚机制**：修改失败时需要回滚功能
3. **版本兼容**：不同版本 nanobot 的代码结构可能不同

---

## Key Insights

1. **模式识别**：所有 provider 的修改遵循相同的模式
2. **可自动化**：通过模板和正则表达式可以完全自动化
3. **可测试**：每次修改后可以运行测试验证

---

## Next Steps

1. 设计 Skill 目录结构
2. 创建 SKILL.md 文档
3. 实现核心功能模块
