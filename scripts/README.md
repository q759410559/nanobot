# Longcat Provider 自动补丁脚本

## 快速开始

### 每次从上游更新后，只需运行：

**Windows:**
```bash
python scripts\apply_longcat_patch.py
```

**Linux/Mac:**
```bash
python scripts/apply_longcat_patch.py
```

## 功能说明

这个脚本会自动修改以下文件以添加 longcat provider 支持：

1. **`nanobot/providers/litellm_provider.py`**
   - 添加 `is_longcat` 检测逻辑
   - 更新 OpenAI 客户端创建条件
   - 添加 longcat 模型名称处理

2. **`nanobot/config/schema.py`**
   - 在 `ProvidersConfig` 中添加 `longcat` 字段
   - 在 `_match_provider` 中添加映射
   - 在 `get_api_key` 和 `get_api_base` 中添加支持

3. **`README.md`**
   - 在 providers 表格中添加 longcat 说明

## 特性

- ✅ **智能检测**：自动判断文件是否已包含 longcat 支持，避免重复应用
- ✅ **跨平台**：支持 Windows、Linux、Mac
- ✅ **安全可靠**：使用正则表达式精确匹配和替换
- ✅ **自动化**：一键应用所有补丁

## 完整工作流程

```bash
# 1. 从上游获取更新
git fetch upstream

# 2. 合并更新
git merge upstream/main

# 3. 应用 longcat 补丁
python scripts/apply_longcat_patch.py

# 4. 检查修改
git diff

# 5. 提交
git add .
git commit -m "Apply longcat provider support patch"

# 6. 推送
git push origin lwk
```

## 故障排除

### 脚本运行失败

如果脚本运行失败，可以手动应用补丁。参考 `workspace/FORK_UPDATE_GUIDE.md` 中的"手动补丁"章节。

### 文件被占用

确保没有编辑器打开正在修改的文件。

## 优势

相比手动修改，使用脚本的优势：

- **速度快**：一键完成所有修改
- **一致性好**：每次修改都使用相同的逻辑
- **不易出错**：避免遗漏某个文件或某行代码
- **可重复**：每次上游更新后都可以重新运行

## 相关文档

- 完整 Fork 更新指南：`workspace/FORK_UPDATE_GUIDE.md`
- 中文语言配置：`workspace/USER.md`
