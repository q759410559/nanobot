# Provider Manager Skill - 快速开始

## 🎯 一句话说明

**Provider Manager Skill** 让你用交互式向导快速添加任何新的 LLM Provider 到 nanobot，就像添加 longcat 一样简单！

## 📦 包含什么

- ✅ 交互式添加脚本（`add_provider.py`）
- ✅ 自动代码修改
- ✅ 补丁脚本生成器
- ✅ 配置模板
- ✅ 完整文档（中文）

## 🚀 立即使用

### 步骤 1: 运行交互式脚本

```bash
python workspace/skills/provider-manager/scripts/add_provider.py
```

### 步骤 2: 按照向导操作

1. 输入 provider 名称（如：`myapi`）
2. 输入显示名称（如：`My Custom API`）
3. 输入 API 端点（如：`https://api.example.com/v1`）
4. 选择是否 OpenAI 兼容
5. 确认信息

### 步骤 3: 完成！

脚本会自动：
- 修改所有必要代码文件
- 生成补丁脚本
- 生成配置模板
- 更新文档

## 📋 完整示例

```bash
$ python workspace/skills/provider-manager/scripts/add_provider.py

Provider 名称 [myprovider]: mycustom
Provider 显示名称 [My Provider]: My Custom API
API 端点 URL [https://api.example.com/v1]: https://api.mycompany.com/v1
是否使用 OpenAI 兼容接口？(Y/n) [Y]: Y

确认添加？(Y/n) [Y]: Y

[OK] nanobot/config/schema.py 已修改
[OK] nanobot/providers/litellm_provider.py 已修改
[OK] README.md 已修改
[OK] 补丁脚本已生成: scripts/apply_mycustom_patch.py
[OK] 配置模板已生成: workspace/skills/provider-manager/references/mycustom-config.md

[SUCCESS] Provider 添加完成！
```

## 📁 文件结构

```
workspace/skills/provider-manager/
├── SKILL.md                    # Skill 主文档（加载此 skill 时自动加载）
├── README.md                    # 详细使用指南
├── QUICK_START.md               # 本文件 - 快速开始
├── scripts/
│   └── add_provider.py         # 交互式添加脚本
└── references/
    └── provider-pattern.md       # Provider 实现模式参考
```

## 🎯 核心功能

### 1. 交互式向导
- 清晰的步骤引导
- 智能默认值
- 输入确认

### 2. 自动修改
- `nanobot/config/schema.py`
- `nanobot/providers/litellm_provider.py`
- `README.md`

### 3. 补丁脚本生成
- 自动生成 `apply_[provider]_patch.py`
- 用于上游更新后重新应用

### 4. 配置模板
- 生成配置示例
- 包含 JSON 格式
- 提供使用说明

## 📖 文档说明

| 文档 | 用途 | 何时阅读 |
|------|------|---------|
| `QUICK_START.md` | 快速开始 | 第一次使用 |
| `README.md` | 完整使用指南 | 需要详细信息 |
| `SKILL.md` | Skill 完整文档 | AI 使用此 skill 时 |
| `references/provider-pattern.md` | 实现模式参考 | 手动添加 provider |

## 🔧 高级用法

### 自定义修改

编辑 `scripts/add_provider.py` 来自定义：
- 代码修改逻辑
- 正则表达式模式
- 生成的模板内容

### 参考实现模式

查看 `references/provider-pattern.md` 了解：
- Provider 分类
- 代码修改模式
- 命名约定
- 测试清单

## 🆚 对比：手动 vs 自动

| 任务 | 手动 | 使用 Skill |
|------|------|-----------|
| 修改 schema.py | 5-10 分钟 | 自动 |
| 修改 litellm_provider.py | 10-20 分钟 | 自动 |
| 修改 README.md | 2-5 分钟 | 自动 |
| 生成补丁脚本 | 10-15 分钟 | 自动 |
| 配置模板 | 5-10 分钟 | 自动 |
| **总计** | **30-60 分钟** | **2-3 分钟** |

## 🎉 总结

使用 Provider Manager Skill，你可以：

1. **快速添加**任何新的 LLM Provider
2. **自动化**重复性工作
3. **标准化**添加流程
4. **减少错误**手动修改的风险

**下次需要添加新的 provider 时，直接运行：**

```bash
python workspace/skills/provider-manager/scripts/add_provider.py
```

就这么简单！🎯
