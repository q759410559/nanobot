# Provider Manager Skill 使用指南

## 简介

Provider Manager Skill 是一个自动化工具，用于简化和加速向 nanobot 添加新 LLM Provider 的过程。

## 功能特性

- ✅ **交互式向导**：引导用户完成 provider 添加流程
- ✅ **自动化代码修改**：自动修改所有必要文件
- ✅ **补丁脚本生成**：自动生成 provider 特定的补丁脚本
- ✅ **配置模板**：生成配置示例和文档
- ✅ **中文支持**：全中文界面和文档

## 快速开始

### 方式 1: 交互式添加（推荐）

运行交互式脚本：

```bash
python workspace/skills/provider-manager/scripts/add_provider.py
```

脚本会引导你完成以下步骤：

1. 输入 provider 基本信息
2. 选择技术特性
3. 确认信息
4. 自动修改代码文件
5. 生成补丁脚本和配置模板

### 方式 2: 手动参考

参考 `references/provider-pattern.md` 手动添加 provider。

## 使用示例

### 示例 1: 添加自定义 OpenAI API

```bash
$ python workspace/skills/provider-manager/scripts/add_provider.py

============================================================
           添加新的 LLM Provider 向导
============================================================

[步骤 1/4] 输入基本信息
------------------------------------------------------------
Provider 名称（小写，如: openai, longcat） [myprovider]: myapi
Provider 显示名称（如: OpenAI, LongCat） [My Provider]: My Custom API
Provider 描述（如: 自定义 API, GPT 模型）[Custom API]: 自定义 OpenAI 兼容 API
API 端点 URL [https://api.example.com/v1]: https://api.mycompany.com/v1
官方文档 URL [https://docs.example.com]: https://docs.mycompany.com

[步骤 2/4] 技术特性
------------------------------------------------------------
是否使用 OpenAI 兼容接口？(Y/n) [Y]: Y
模型命名规则（如: gpt-*, claude-*）[model-*]: my-model-*

[步骤 3/4] 确认信息
------------------------------------------------------------
Provider 名称:       myapi
显示名称:           My Custom API
描述:               自定义 OpenAI 兼容 API
API 端点:          https://api.mycompany.com/v1
文档地址:           https://docs.mycompany.com
OpenAI 兼容:        Y
模型命名:           my-model-*

确认添加？(Y/n) [Y]: Y

[步骤 4/4] 执行修改
------------------------------------------------------------
[OK] nanobot/config/schema.py 已修改
[OK] nanobot/providers/litellm_provider.py 已修改
[OK] README.md 已修改
[OK] 补丁脚本已生成: scripts/apply_myapi_patch.py
[OK] 配置模板已生成: workspace/skills/provider-manager/references/myapi-config.md

============================================================
[SUCCESS] Provider 添加完成！
============================================================

后续步骤：
1. 编辑 config.json 添加 myapi 的 API Key
2. 运行验证: python scripts/apply_myapi_patch.py
3. 提交代码: git add . && git commit -m 'Add myapi provider'
```

## 文件结构

```
workspace/skills/provider-manager/
├── SKILL.md                    # Skill 主文档
├── README.md                    # 使用指南（本文件）
├── scripts/
│   └── add_provider.py         # 交互式添加脚本
└── references/
    └── provider-pattern.md       # Provider 实现模式文档
```

## 工作原理

### 1. 交互式收集信息

脚本通过命令行界面收集以下信息：

- Provider 名称和显示名称
- API 端点 URL
- 是否 OpenAI 兼容
- 模型命名规则

### 2. 自动修改代码

根据收集的信息，自动修改：

1. **`nanobot/config/schema.py`**
   - 添加 provider 配置字段
   - 添加到 provider 映射
   - 添加到 API key 获取列表
   - 添加到 API base 判断

2. **`nanobot/providers/litellm_provider.py`**
   - 添加 provider 检测逻辑
   - 更新 OpenAI client 创建条件
   - 添加模型名称处理

3. **`README.md`**
   - 在 providers 表格中添加说明

### 3. 生成补丁脚本

自动生成 `scripts/apply_[provider]_patch.py`，用于：
- 从上游更新后重新应用修改
- 自动化重复任务

### 4. 生成配置模板

生成配置示例文档，包含：
- JSON 配置格式
- 使用示例
- API Key 获取说明

## 后续步骤

### 1. 配置 API Key

编辑 `config.json`：

```json
{
  "providers": {
    "myprovider": {
      "apiKey": "your-api-key-here",
      "apiBase": "https://api.myprovider.com/v1"
    }
  }
}
```

### 2. 运行补丁脚本

如果需要重新应用修改：

```bash
python scripts/apply_myprovider_patch.py
```

### 3. 测试 Provider

测试新 provider 是否工作：

```bash
nanobot agent -m "myprovider/model-name"
```

### 4. 提交代码

```bash
git add .
git commit -m "Add myprovider support"
git push origin lwk
```

## 常见问题

### Q: 添加后代码无法运行？

A: 检查语法错误：

```bash
python -m py_compile nanobot/config/schema.py
python -m py_compile nanobot/providers/litellm_provider.py
```

### Q: API 调用失败？

A: 检查：
1. API Key 是否正确
2. API Base URL 是否正确
3. 网络连接是否正常

### Q: 模型名称不匹配？

A: 检查 provider 文档，确认模型命名规范。

### Q: 如何撤销修改？

A: 使用 git 回滚：

```bash
# 查看修改
git diff

# 回滚特定文件
git restore nanobot/config/schema.py

# 完全回滚
git reset --hard HEAD
```

## 高级用法

### 自定义代码模板

如果需要自定义修改逻辑，编辑 `scripts/add_provider.py` 中的相应函数：

- `modify_schema_py()` - 修改 schema.py
- `modify_litellm_provider_py()` - 修改 litellm_provider.py
- `modify_readme_md()` - 修改 README.md

### 批量添加多个 Provider

可以修改脚本以支持批量添加，或者多次运行脚本。

### 集成到 CI/CD

将补丁脚本集成到 CI/CD 流程，确保上游更新后自动应用。

## 相关文档

- `SKILL.md` - Skill 完整文档
- `references/provider-pattern.md` - Provider 实现模式
- `workspace/FORK_UPDATE_GUIDE.md` - Fork 更新指南

## 反馈和改进

如果遇到问题或有改进建议，请：

1. 检查 `references/provider-pattern.md` 中的常见问题
2. 查看 `workspace/FORK_UPDATE_GUIDE.md` 的故障排除章节
3. 提交 issue 或 pull request

## 版本历史

- **v1.0** (2026-02-06)
  - 初始版本
  - 交互式向导
  - 自动代码修改
  - 补丁脚本生成
