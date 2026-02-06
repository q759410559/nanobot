#!/usr/bin/env python3
"""
交互式添加新的 LLM Provider

使用此脚本快速添加新的 provider 到 nanobot 项目。
"""

import sys
import re
from pathlib import Path


def get_input(prompt, default=None):
    """获取用户输入，支持默认值"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    result = input(full_prompt).strip()
    return result if result else default


def modify_schema_py(provider_name, display_name, api_url):
    """修改 nanobot/config/schema.py"""
    schema_file = Path('nanobot/config/schema.py')
    content = schema_file.read_text(encoding='utf-8')

    # 1. 添加 provider 字段
    pattern = r'(gemini: ProviderConfig = Field\(default_factory=ProviderConfig\))'
    replacement = f'''\\1
    {provider_name}: ProviderConfig = Field(default_factory=ProviderConfig)'''
    content = re.sub(pattern, replacement, content)

    # 2. 添加到 providers 字典
    pattern2 = r'("moonshot": self\.providers\.moonshot,)'
    replacement2 = f'''\\1
            "{provider_name}": self.providers.{provider_name},'''
    content = re.sub(pattern2, replacement2, content)

    # 3. 添加到 get_api_key
    pattern3 = r'(self\.providers\.groq,)'
    replacement3 = f'''\\1
            self.providers.{provider_name},'''
    content = re.sub(pattern3, replacement3, content)

    # 4. 添加到 get_api_base
    pattern4 = r'(if "moonshot" in model or "kimi" in model:)'
    replacement4 = f'''if "{provider_name}" in model:
            return self.providers.{provider_name}.api_base
        \\1'''
    content = re.sub(pattern4, replacement4, content)

    schema_file.write_text(content, encoding='utf-8')
    print(f"[OK] {schema_file} 已修改")


def modify_litellm_provider_py(provider_name, api_url, is_openai_compatible):
    """修改 nanobot/providers/litellm_provider.py"""
    provider_file = Path('nanobot/providers/litellm_provider.py')
    content = provider_file.read_text(encoding='utf-8')

    if is_openai_compatible.lower() == 'y':
        # 1. 添加检测
        pattern = r'(self\.is_longcat = bool\(api_base\) and "longcat" in api_base\.lower\(\))'
        replacement = f'''\\1
        self.is_{provider_name} = bool(api_base) and "{provider_name}" in api_base.lower()'''
        content = re.sub(pattern, replacement, content)

        # 2. 更新 is_vllm
        pattern2 = r'(self\.is_vllm = bool\(api_base\) and not self\.is_openrouter and not self\.is_longcat)'
        replacement2 = f'\\1 and not self.is_{provider_name}'
        content = re.sub(pattern2, replacement2, content)

        # 3. 更新 OpenAI client 条件
        pattern3 = r'(if self\.is_longcat or self\.is_vllm:)'
        replacement3 = f'if self.is_longcat or self.is_vllm or self.is_{provider_name}:'
        content = re.sub(pattern3, replacement3, content)

        # 4. 更新注释
        pattern4 = r'(OpenAI-compatible endpoints \(longcat, vLLM\))'
        replacement4 = f'OpenAI-compatible endpoints (longcat, vllm, {provider_name})'
        content = re.sub(pattern4, replacement4, content)

    provider_file.write_text(content, encoding='utf-8')
    print(f"[OK] {provider_file} 已修改")


def modify_readme_md(provider_name, display_name, description, doc_url):
    """修改 README.md"""
    readme_file = Path('README.md')
    content = readme_file.read_text(encoding='utf-8')

    pattern = r'(\| `gemini` \| LLM \(Gemini direct\) \| \[aistudio\.google\.com\]\(https://aistudio\.google\.com\) \|)'
    replacement = f'''\\1
| `{provider_name}` | LLM ({description}) | [{doc_url}]({doc_url}) |'''
    content = re.sub(pattern, replacement, content)

    readme_file.write_text(content, encoding='utf-8')
    print(f"[OK] {readme_file} 已修改")


def generate_patch_script(provider_name, display_name, api_url, is_openai_compatible):
    """生成 provider 特定的补丁脚本"""
    patch_script = Path(f'scripts/apply_{provider_name}_patch.py')

    script_content = f'''#!/usr/bin/env python3
"""
自动应用 {display_name} provider 支持补丁

每次从上游更新后运行此脚本，自动重新添加 {provider_name} 相关代码。
"""

import sys
from pathlib import Path
import re


def patch_schema(file_path: Path) -> bool:
    """补丁 schema.py 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # 添加 {provider_name} 字段
    pattern = r'(gemini: ProviderConfig = Field\\(default_factory=ProviderConfig\\))'
    replacement = r'\\1\\n    {provider_name}: ProviderConfig = Field(default_factory=ProviderConfig)'
    content = re.sub(pattern, replacement, content)

    # 添加到 providers 字典
    pattern2 = r'("moonshot": self\\.providers\\.moonshot,)'
    replacement2 = r'\\1\\n            "{provider_name}": self.providers.{provider_name},'
    content = re.sub(pattern2, replacement2, content)

    # 添加到 get_api_key
    pattern3 = r'(self\\.providers\\.groq,)'
    replacement3 = r'\\1\\n            self.providers.{provider_name},'
    content = re.sub(pattern3, replacement3, content)

    # 添加到 get_api_base
    pattern4 = r'(if "moonshot" in model or "kimi" in model:)'
    replacement4 = r'if "{provider_name}" in model:\\n            return self.providers.{provider_name}.api_base\\n        \\1'
    content = re.sub(pattern4, replacement4, content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] schema.py 补丁已应用")
        return True
    return False


def patch_litellm_provider(file_path: Path) -> bool:
    """补丁 litellm_provider.py 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

'''

    if is_openai_compatible.lower() == 'y':
        script_content += f'''    # 添加 {provider_name} 检测
    pattern = r'(self.is_longcat = bool\\(api_base\\) and "longcat" in api_base.lower\\(\\))'
    replacement = r'\\1\\n        self.is_{provider_name} = bool(api_base) and "{provider_name}" in api_base.lower()'
    content = re.sub(pattern, replacement, content)

    # 更新 is_vllm
    pattern2 = r'(self.is_vllm = bool\\(api_base\\) and not self.is_openrouter and not self.is_longcat)'
    replacement2 = r'\\1 and not self.is_{provider_name}'
    content = re.sub(pattern2, replacement2, content)

    # 更新 OpenAI client 条件
    pattern3 = r'(if self.is_longcat or self.is_vllm:)'
    replacement3 = r'if self.is_longcat or self.is_vllm or self.is_{provider_name}:'
    content = re.sub(pattern3, replacement3, content)

    # 更新注释
    pattern4 = r'(OpenAI-compatible endpoints \\(longcat, vLLM\\))'
    replacement4 = r'\\1, {provider_name}'
    content = re.sub(pattern4, replacement4, content)

'''

    script_content += f'''    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] litellm_provider.py 补丁已应用")
        return True
    return False


def patch_readme(file_path: Path) -> bool:
    """补丁 README.md 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    pattern = r'(\\| `gemini` \\| LLM \\(Gemini direct\\) \\| \\[aistudio\\.google\\.com\\]\\(https://aistudio\\.google\\.com\\) \\|)'
    replacement = r'\\1\\n| `{provider_name}` | LLM ({display_name}) | {api_url} |'
    content = re.sub(pattern, replacement, content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] README.md 补丁已应用")
        return True
    return False


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent

    print("[PATCH] 应用 {display_name} provider 支持补丁...")
    print()

    modified = False

    # 补丁 schema.py
    schema_file = project_root / 'nanobot' / 'config' / 'schema.py'
    if schema_file.exists():
        if patch_schema(schema_file):
            modified = True
    else:
        print(f"[ERROR] 文件不存在: {{schema_file}}")
        sys.exit(1)

    # 补丁 litellm_provider.py
    provider_file = project_root / 'nanobot' / 'providers' / 'litellm_provider.py'
    if provider_file.exists():
        if patch_litellm_provider(provider_file):
            modified = True
    else:
        print(f"[ERROR] 文件不存在: {{provider_file}}")
        sys.exit(1)

    # 补丁 README.md
    readme_file = project_root / 'README.md'
    if readme_file.exists():
        if patch_readme(readme_file):
            modified = True
    else:
        print(f"[WARN] 文件不存在（可选）: {{readme_file}}")

    print()
    print("[SUCCESS] 所有补丁已成功应用！" if modified else "[INFO] 无需应用补丁（已存在）")
    print()
    print("[TIPS] 提示：config.json 在 .gitignore 中，你的 {provider_name} 配置不会被跟踪。")
    print("[TIPS] 提示：下次从上游更新后，再次运行此脚本即可重新应用补丁。")
    print()
    if modified:
        print("[ACTION] 请检查修改是否正确，然后运行：")
        print("   git add .")
        print("   git commit -m 'Apply {display_name} provider support patch'")
        print()


if __name__ == '__main__':
    main()
'''

    patch_script.write_text(script_content, encoding='utf-8')
    print(f"[OK] 补丁脚本已生成: {patch_script}")


def generate_config_template(provider_name, api_url):
    """生成配置模板"""
    config_template = f'''# {provider_name.upper()} Provider 配置

## 基本配置

在 `config.json` 中添加：

```json
{{
  "providers": {{
    "{provider_name}": {{
      "apiKey": "YOUR_API_KEY_HERE",
      "apiBase": "{api_url}"
    }}
  }}
}}
```

## 使用示例

```json
{{
  "agents": {{
    "defaults": {{
      "model": "{provider_name}/your-model-name",
      "maxTokens": 8192,
      "temperature": 0.7
    }}
  }}
}}
```

## 获取 API Key

访问 {api_url} 获取你的 API Key。
'''

    template_file = Path(f'workspace/skills/provider-manager/references/{provider_name}-config.md')
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(config_template, encoding='utf-8')
    print(f"[OK] 配置模板已生成: {template_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("           添加新的 LLM Provider 向导")
    print("=" * 60)
    print()

    # Step 1: 基本信息
    print("[步骤 1/4] 输入基本信息")
    print("-" * 60)
    provider_name = get_input("Provider 名称（小写，如: openai, longcat）", "myprovider")
    display_name = get_input("Provider 显示名称（如: OpenAI, LongCat）", "My Provider")
    description = get_input("Provider 描述（如: 自定义 API, GPT 模型）", "Custom API")
    api_url = get_input("API 端点 URL", "https://api.example.com/v1")
    doc_url = get_input("官方文档 URL", "https://docs.example.com")
    print()

    # Step 2: 技术特性
    print("[步骤 2/4] 技术特性")
    print("-" * 60)
    is_openai_compatible = get_input("是否使用 OpenAI 兼容接口？(Y/n)", "Y")
    model_pattern = get_input("模型命名规则（如: gpt-*, claude-*）", "model-*")
    print()

    # Step 3: 确认信息
    print("[步骤 3/4] 确认信息")
    print("-" * 60)
    print(f"Provider 名称:       {provider_name}")
    print(f"显示名称:           {display_name}")
    print(f"描述:               {description}")
    print(f"API 端点:          {api_url}")
    print(f"文档地址:           {doc_url}")
    print(f"OpenAI 兼容:        {is_openai_compatible}")
    print(f"模型命名:           {model_pattern}")
    print()

    confirm = get_input("确认添加？(Y/n)", "Y")
    if confirm.lower() != 'y':
        print("[CANCEL] 操作已取消")
        return

    # Step 4: 执行修改
    print()
    print("[步骤 4/4] 执行修改")
    print("-" * 60)

    try:
        modify_schema_py(provider_name, display_name, api_url)
        modify_litellm_provider_py(provider_name, api_url, is_openai_compatible)
        modify_readme_md(provider_name, display_name, description, doc_url)
        generate_patch_script(provider_name, display_name, api_url, is_openai_compatible)
        generate_config_template(provider_name, api_url)

        print()
        print("=" * 60)
        print("[SUCCESS] Provider 添加完成！")
        print("=" * 60)
        print()
        print("后续步骤：")
        print(f"1. 编辑 config.json 添加 {provider_name} 的 API Key")
        print(f"2. 运行验证: python scripts/apply_{provider_name}_patch.py")
        print("3. 提交代码: git add . && git commit -m 'Add {provider_name} provider'")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print(f"[ERROR] 发生错误: {e}")
        print("=" * 60)
        print()
        print("请检查：")
        print("1. 是否在项目根目录运行此脚本")
        print("2. 文件权限是否正确")
        print("3. 是否有足够的磁盘空间")
        sys.exit(1)


if __name__ == '__main__':
    main()
