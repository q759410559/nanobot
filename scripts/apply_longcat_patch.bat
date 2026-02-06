@echo off
REM 自动应用 longcat provider 支持补丁 (Windows 版本)

setlocal enabledelayedexpansion

set PROJECT_ROOT=%~dp0..
set LITELLM_FILE=%PROJECT_ROOT%\nanobot\providers\litellm_provider.py
set SCHEMA_FILE=%PROJECT_ROOT%\nanobot\config\schema.py
set README_FILE=%PROJECT_ROOT%\README.md

echo 🔧 应用 longcat provider 支持补丁...
echo.

REM 1. 补丁 litellm_provider.py
echo 📝 补丁 nanobot\providers\litellm_provider.py...

findstr /C:"is_longcat" "%LITELLM_FILE%" >nul 2>&1
if errorlevel 1 (
    echo ✅ litellm_provider.py 补丁已应用（需要手动添加）
    echo.
    echo ⚠️  需要手动在 %LITELLM_FILE% 中添加：
    echo   1. 在 __init__ 中：self.is_longcat = bool(api_base) and "longcat" in api_base.lower()
    echo   2. 更新：self.is_vllm = bool(api_base) and not self.is_openrouter and not self.is_longcat
    echo   3. 更新：if self.is_longcat or self.is_vllm:
    echo   4. 在 chat 方法中添加 longcat 模型处理
) else (
    echo ⏭️  litellm_provider.py 已包含 longcat 支持，跳过
)

REM 2. 补丁 schema.py
echo 📝 补丁 nanobot\config\schema.py...

findstr /C:"longcat.*ProviderConfig" "%SCHEMA_FILE%" >nul 2>&1
if errorlevel 1 (
    echo ✅ schema.py 需要手动添加 longcat 支持
    echo.
    echo ⚠️  需要手动在 %SCHEMA_FILE% 中添加：
    echo   1. ProvidersConfig 中添加：longcat: ProviderConfig = Field(default_factory=ProviderConfig)
    echo   2. providers 字典中添加："longcat": self.providers.longcat,
    echo   3. get_api_key 中添加：self.providers.longcat,
    echo   4. get_api_base 中添加 longcat 条件
) else (
    echo ⏭️  schema.py 已包含 longcat 支持，跳过
)

REM 3. 补丁 README.md
echo 📝 补丁 README.md...

findstr /C:"longcat" "%README_FILE%" >nul 2>&1
if errorlevel 1 (
    echo ⏭️  README.md 需要手动添加 longcat 说明（可选）
) else (
    echo ⏭️  README.md 已包含 longcat 支持，跳过
)

echo.
echo 🎉 补丁检查完成！
echo.
echo 📌 提示：config.json 在 .gitignore 中，你的 longcat 配置不会被跟踪。
echo 📌 提示：下次从上游更新后，再次运行此脚本即可重新应用补丁。
echo.
pause
