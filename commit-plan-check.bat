@echo off
setlocal

REM Run the read-only commit-plan checker from the newest llm-shared Python.
set "COMMIT_PLAN_CHECK_ROOT=%~dp0"
set "COMMIT_PLAN_CHECK_PYTHON_BASE=%COMMIT_PLAN_CHECK_ROOT%venvs"
set "COMMIT_PLAN_CHECK_LATEST="

for /f "delims=" %%d in ('dir /b /ad /o-d "%COMMIT_PLAN_CHECK_PYTHON_BASE%\python_3*llm-shared*" 2^>nul') do (
    if not defined COMMIT_PLAN_CHECK_LATEST set "COMMIT_PLAN_CHECK_LATEST=%%d"
)

if not defined COMMIT_PLAN_CHECK_LATEST (
    echo commit-plan-check: no llm-shared Python environment found 1>&2
    exit /b 2
)

set "COMMIT_PLAN_CHECK_PYTHON=%COMMIT_PLAN_CHECK_PYTHON_BASE%\%COMMIT_PLAN_CHECK_LATEST%\Scripts\python.exe"
REM Keep the caller's directory so default root discovery checks its repository.
if defined PYTHONPATH (
    set "PYTHONPATH=%COMMIT_PLAN_CHECK_ROOT%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%COMMIT_PLAN_CHECK_ROOT%"
)
"%COMMIT_PLAN_CHECK_PYTHON%" -m tools.commit_plan_check %*
set "COMMIT_PLAN_CHECK_STATUS=%ERRORLEVEL%"
exit /b %COMMIT_PLAN_CHECK_STATUS%
