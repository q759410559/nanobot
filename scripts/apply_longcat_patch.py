#!/usr/bin/env python3
"""
自动应用 longcat provider 支持补丁

每次从上游更新后运行此脚本，自动重新添加 longcat 相关代码。
"""

import sys
from pathlib import Path
import re


def patch_litellm_provider(file_path: Path) -> bool:
    """补丁 litellm_provider.py 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # 检查是否已经包含 longcat
    if 'is_longcat' in content and 'self.is_longcat' in content:
        print("[SKIP] litellm_provider.py 已包含 longcat 支持，跳过")
        return False

    # 1. 添加 longcat 检测（在 is_openrouter 之后）
    pattern1 = r'(self\.is_openrouter = \([^)]+\))'
    replacement1 = r'''\1

        # Detect Longcat by api_base
        self.is_longcat = bool(api_base) and "longcat" in api_base.lower()'''
    content = re.sub(pattern1, replacement1, content)

    # 2. 更新 is_vllm 检测，排除 longcat
    content = content.replace(
        'self.is_vllm = bool(api_base) and not self.is_openrouter',
        'self.is_vllm = bool(api_base) and not self.is_openrouter and not self.is_longcat'
    )

    # 3. 更新 OpenAI client 创建条件
    content = content.replace(
        'if self.is_vllm:',
        'if self.is_longcat or self.is_vllm:'
    )

    # 4. 更新注释
    content = content.replace(
        'OpenAI-compatible endpoints (vLLM)',
        'OpenAI-compatible endpoints (longcat, vLLM)'
    )

    # 5. 在 chat 方法中添加 longcat 模型处理
    pattern2 = r'(# For vLLM, use hosted_vllm/ prefix per LiteLLM docs)'
    replacement2 = r'''\1

        # For longcat, remove any provider prefix and use raw model name
        if self.is_longcat:
            # Remove openai/ prefix if present
            if model.startswith("openai/"):
                model = model[7:]'''
    content = re.sub(pattern2, replacement2, content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] litellm_provider.py 补丁已应用")
        return True
    return False


def patch_schema(file_path: Path) -> bool:
    """补丁 schema.py 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # 检查是否已经包含 longcat
    if 'longcat: ProviderConfig' in content and 'self.providers.longcat' in content:
        print("[SKIP] schema.py 已包含 longcat 支持，跳过")
        return False

    # 1. 在 ProvidersConfig 类中添加 longcat
    pattern1 = r'(gemini: ProviderConfig = Field\(default_factory=ProviderConfig\))'
    replacement1 = r'''\1
    longcat: ProviderConfig = Field(default_factory=ProviderConfig)'''
    content = re.sub(pattern1, replacement1, content)

    # 2. 在 providers 字典中添加 longcat 映射
    content = content.replace(
        '"vllm": self.providers.vllm,',
        '"vllm": self.providers.vllm,\n            "longcat": self.providers.longcat,'
    )

    # 3. 在 get_api_key 方法中添加 longcat
    content = content.replace(
        'self.providers.groq,',
        'self.providers.groq,\n            self.providers.longcat,'
    )

    # 4. 在 get_api_base 方法中添加 longcat
    pattern2 = r'(if "moonshot" in model or "kimi" in model:)'
    replacement2 = r'''if "longcat" in model:
            return self.providers.longcat.api_base
        \1'''
    content = re.sub(pattern2, replacement2, content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] schema.py 补丁已应用")
        return True
    return False


def patch_readme(file_path: Path) -> bool:
    """补丁 README.md 文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # 检查是否已经包含 longcat
    if 'longcat' in content.lower():
        print("[SKIP] README.md 已包含 longcat 支持，跳过")
        return False

    # 在 providers 表格中添加 longcat（在 gemini 行之后）
    pattern = r'(\| `gemini` \| LLM \(Gemini direct\) \| \[aistudio\.google\.com\]\(https://aistudio\.google\.com\) \|)'
    replacement = r'''\1
| `longcat` | LLM (LongCat - 自定义 API) | https://api.longcat.chat/openai |'''
    content = re.sub(pattern, replacement, content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print("[OK] README.md 补丁已应用")
        return True
    return False


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent

    print("[PATCH] 应用 longcat provider 支持补丁...")
    print()

    modified = False

    # 补丁 litellm_provider.py
    litellm_file = project_root / 'nanobot' / 'providers' / 'litellm_provider.py'
    if litellm_file.exists():
        if patch_litellm_provider(litellm_file):
            modified = True
    else:
        print(f"[ERROR] 文件不存在: {litellm_file}")
        sys.exit(1)

    # 补丁 schema.py
    schema_file = project_root / 'nanobot' / 'config' / 'schema.py'
    if schema_file.exists():
        if patch_schema(schema_file):
            modified = True
    else:
        print(f"[ERROR] 文件不存在: {schema_file}")
        sys.exit(1)

    # 补丁 README.md
    readme_file = project_root / 'README.md'
    if readme_file.exists():
        if patch_readme(readme_file):
            modified = True
    else:
        print(f"[WARN] 文件不存在（可选）: {readme_file}")

    print()
    print("[SUCCESS] 所有补丁已成功应用！" if modified else "[INFO] 无需应用补丁（已存在）")
    print()
    print("[TIPS] 提示：config.json 在 .gitignore 中，你的 longcat 配置不会被跟踪。")
    print("[TIPS] 提示：下次从上游更新后，再次运行此脚本即可重新应用补丁。")
    print()
    if modified:
        print("[ACTION] 请检查修改是否正确，然后运行：")
        print("   git add .")
        print("   git commit -m 'Apply longcat provider support patch'")
        print()


if __name__ == '__main__':
    main()
