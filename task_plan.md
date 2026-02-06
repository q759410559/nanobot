# Task Plan: Create Provider Management Skill

## Goal

创建一个通用的 Skill 来简化添加新 LLM Provider 的流程，参考 longcat provider 的实现方式，使其可以快速、自动化地添加任何新的 provider。

## Context

- 当前添加 longcat provider 需要手动修改多个文件
- 已有自动化脚本 `scripts/apply_longcat_patch.py` 作为参考
- 目标是将这个流程封装成一个可复用的 Skill

## Success Criteria

1. 创建一个 Provider 管理 Skill
2. 提供交互式向导，快速添加新 provider
3. 自动修改所有必要文件（schema.py, litellm_provider.py, README.md 等）
4. 生成自动化补丁脚本
5. 支持中文提示和文档

## Phases

### Phase 1: 研究现有实现 ✅

**Status:** Complete
**Findings:**
- longcat provider 修改涉及 3 个核心文件
- `nanobot/config/schema.py` - 配置模型
- `nanobot/providers/litellm_provider.py` - 提供者实现
- `README.md` - 文档
- 自动补丁脚本已存在并验证可用

---

### Phase 2: 设计 Skill 结构

**Status:** complete
**Deliverables:**
- ✅ Skill 目录结构定义
- ✅ 主要功能模块设计
- ✅ 交互式向导流程规划

**Tasks:**
1. ✅ 定义 Skill 目录结构
2. ✅ 设计添加 provider 的工作流
3. ✅ 定义配置文件模板
4. ✅ 规划代码生成逻辑

---

### Phase 3: 创建 Skill 基础框架

**Status:** complete
**Deliverables:**
- ✅ `workspace/skills/provider-manager/SKILL.md`
- ✅ Skill 主目录和子目录
- ✅ 模板文件

---

### Phase 4: 实现核心功能

**Status:** complete
**Deliverables:**
- ✅ 交互式命令行界面（`add_provider.py`）
- ✅ Provider 配置生成器
- ✅ 文件修改自动化
- ✅ 补丁脚本生成器

---

### Phase 5: 创建文档和示例

**Status:** complete
**Deliverables:**
- ✅ Skill 使用文档（SKILL.md）
- ✅ Provider 实现模式文档（`provider-pattern.md`）
- ✅ 配置模板生成器

---

### Phase 6: 测试和验证

**Status:** in_progress
**Deliverables:**
- 测试添加新 provider
- 验证所有修改正确
- 确保向后兼容

---

## Decisions

| Decision | Rationale |
|----------|-----------|
| 使用 Python 实现 | 复用现有补丁脚本的 Python 代码 |
| 交互式 CLI | 提供用户友好的向导体验 |
| 模板驱动 | 易于定制和扩展 |
| 支持中文 | 符合用户语言偏好 |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| (None yet) | - | - |

## Files Created/Modified

| File | Action | Status |
|------|--------|--------|
| `task_plan.md` | Created | ✅ |
| `findings.md` | Created | ✅ |
| `progress.md` | Created | ✅ |
| `workspace/skills/provider-manager/SKILL.md` | Created | ✅ |
| `workspace/skills/provider-manager/scripts/add_provider.py` | Created | ✅ |
| `workspace/skills/provider-manager/references/provider-pattern.md` | Created | ✅ |
