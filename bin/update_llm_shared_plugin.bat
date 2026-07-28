@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM Self-locate the llm-shared folder from this launcher's own path.
if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."

set "PLUGIN_ROOT=%LLM_SHARED_DIR%\.agents\llm-shared"
set "PLUGIN_CREATOR_ROOT=%USERPROFILE%\.codex\skills\.system\plugin-creator"
set "VALIDATOR=%PLUGIN_CREATOR_ROOT%\scripts\validate_plugin.py"
set "CACHEBUSTER=%PLUGIN_CREATOR_ROOT%\scripts\update_plugin_cachebuster.py"

if not exist "%PLUGIN_ROOT%\.codex-plugin\plugin.json" (
    echo ERROR: llm-shared plugin manifest not found under "%PLUGIN_ROOT%".
    exit /b 1
)

if not exist "%VALIDATOR%" (
    echo ERROR: Codex plugin validator not found at "%VALIDATOR%".
    exit /b 1
)

if not exist "%CACHEBUSTER%" (
    echo ERROR: Codex cachebuster helper not found at "%CACHEBUSTER%".
    exit /b 1
)

set "UV_EXE="
for %%e in (uv.exe) do set "UV_EXE=%%~$PATH:e"
if not defined UV_EXE (
    echo ERROR: uv.exe is not available on PATH.
    exit /b 1
)

set "CODEX_EXE=%USERPROFILE%\.codex\packages\standalone\current\bin\codex.exe"
if not exist "%CODEX_EXE%" (
    set "CODEX_EXE="
    for %%e in (codex.exe) do set "CODEX_EXE=%%~$PATH:e"
)
if not defined CODEX_EXE (
    echo ERROR: codex.exe was not found in the standalone package or on PATH.
    exit /b 1
)

"%UV_EXE%" run --isolated --no-project --with PyYAML python "%VALIDATOR%" "%PLUGIN_ROOT%"
if errorlevel 1 exit /b 1

python "%CACHEBUSTER%" "%PLUGIN_ROOT%"
if errorlevel 1 exit /b 1

"%CODEX_EXE%" plugin add llm-shared@personal
if errorlevel 1 exit /b 1

"%CODEX_EXE%" plugin list | findstr /I /C:"llm-shared@personal"
if errorlevel 1 (
    echo ERROR: llm-shared@personal was not found in the installed plugin list.
    exit /b 1
)

echo Start a new Codex thread to load the updated plugin.
