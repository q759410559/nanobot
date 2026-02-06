#!/bin/bash
# 自动应用 longcat provider 支持补丁

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 应用 longcat provider 支持补丁..."

# 1. 补丁 litellm_provider.py
echo "📝 补丁 nanobot/providers/litellm_provider.py..."
LITELLM_FILE="$PROJECT_ROOT/nanobot/providers/litellm_provider.py"

# 检查是否已经包含 longcat
if ! grep -q "is_longcat" "$LITELLM_FILE"; then
    # 在 __init__ 方法中添加 longcat 检测
    sed -i '/self.is_openrouter = (/a\
\
        # Detect Longcat by api_base\
        self.is_longcat = bool(api_base) and "longcat" in api_base.lower()' "$LITELLM_FILE"

    # 更新 is_vllm 检测，排除 longcat
    sed -i 's/self.is_vllm = bool(api_base) and not self.is_openrouter/self.is_vllm = bool(api_base) and not self.is_openrouter and not self.is_longcat/' "$LITELLM_FILE"

    # 在 OpenAI client 创建条件中添加 longcat
    sed -i 's/if self.is_vllm:/if self.is_longcat or self.is_vllm:/' "$LITELLM_FILE"

    # 在 chat 方法中添加 longcat 模型处理
    sed -i '/# For vLLM, use hosted_vllm\/ prefix per LiteLLM docs/a\
\
        # For longcat, remove any provider prefix and use raw model name\
        if self.is_longcat:\
            # Remove openai\/ prefix if present\
            if model.startswith("openai\/"):\
                model = model[7:]' "$LITELLM_FILE"

    # 在 OpenAI client 注释中添加 longcat
    sed -i 's/OpenAI-compatible endpoints (vLLM)/OpenAI-compatible endpoints (longcat, vLLM)/' "$LITELLM_FILE"

    echo "✅ litellm_provider.py 补丁已应用"
else
    echo "⏭️  litellm_provider.py 已包含 longcat 支持，跳过"
fi

# 2. 补丁 schema.py
echo "📝 补丁 nanobot/config/schema.py..."
SCHEMA_FILE="$PROJECT_ROOT/nanobot/config/schema.py"

# 检查是否已经包含 longcat
if ! grep -q "longcat.*ProviderConfig" "$SCHEMA_FILE"; then
    # 在 ProvidersConfig 类中添加 longcat
    sed -i '/self.providers.gemini = Field(default_factory=ProviderConfig)/a\        longcat: ProviderConfig = Field(default_factory=ProviderConfig)' "$SCHEMA_FILE"

    # 在 providers 字典中添加 longcat 映射
    sed -i '/"vllm": self.providers.vllm,/a\            "longcat": self.providers.longcat,' "$SCHEMA_FILE"

    # 在 get_api_key 方法中添加 longcat
    sed -i '/self.providers.groq,/a\            self.providers.longcat,' "$SCHEMA_FILE"

    # 在 get_api_base 方法中添加 longcat
    sed -i '/if "moonshot"/i\        if "longcat" in model:\
            return self.providers.longcat.api_base\
' "$SCHEMA_FILE"

    echo "✅ schema.py 补丁已应用"
else
    echo "⏭️  schema.py 已包含 longcat 支持，跳过"
fi

# 3. 补丁 README.md
echo "📝 补丁 README.md..."
README_FILE="$PROJECT_ROOT/README.md"

# 检查是否已经包含 longcat
if ! grep -q "longcat" "$README_FILE"; then
    # 在 providers 表格中添加 longcat
    sed -i '/| `gemini` | LLM (Gemini direct) | \[aistudio.google.com\]/a| `longcat` | LLM (LongCat - 自定义 API) | https://api.longcat.chat/openai |' "$README_FILE"

    echo "✅ README.md 补丁已应用"
else
    echo "⏭️  README.md 已包含 longcat 支持，跳过"
fi

echo ""
echo "🎉 所有补丁已成功应用！"
echo ""
echo "📌 提示：config.json 在 .gitignore 中，你的 longcat 配置不会被跟踪。"
echo "📌 提示：下次从上游更新后，再次运行此脚本即可重新应用补丁。"
