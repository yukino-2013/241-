@echo off
chcp 65001 > nul
echo ========================================
echo  智能运维助手 - 快速启动脚本
echo ========================================
echo.

echo [1] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo [2] 检查智谱API配置...
if exist ".env" (
    echo .env文件已存在
    for /f "tokens=2 delims==" %%i in ('findstr "ZHIPUAI_API_KEY" .env') do (
        set "API_KEY=%%i"
    )
    if "%API_KEY%"=="your_zhipuai_api_key_here" (
        echo 警告: 请编辑.env文件配置真实的智谱API Key
    ) else (
        echo API Key已配置: %API_KEY:~0,10%...
    )
) else (
    echo 错误: .env文件不存在，请复制.env.example并配置
    pause
    exit /b 1
)

echo.
echo [3] 启动简化版API服务器...
echo 请在新的窗口中按以下命令启动：
echo   cd backend
echo   python main_simple.py
echo.
echo 或直接按任意键启动（按Ctrl+C停止）
pause

cd backend
python main_simple.py --host 127.0.0.1 --port 8000

pause