@echo off
REM TW3.0 Windows一键启动脚本
REM 启动TW Go Commentary Engine集成系统

echo 正在启动 TW Go Commentary Engine (TW3.0)...
echo 时间: %date% %time%

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python 3.7+
    pause
    exit /b 1
)

REM 检查numpy
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo 正在安装numpy...
    pip install numpy
)

echo 启动TW3.0集成系统...
start "TW3.0_GUI" python integrated_system.py

echo 启动持续学习进程...
start "TW3_ConsLearning" python continuous_learning.py

echo 启动调试监控...
start "TW3_DebugMonitor" python debug_monitor.py

echo.
echo TW3.0系统已启动!
echo 系统包含以下组件:
echo   - TW1.0 分析引擎 (集成在主系统中)
echo   - TW2.0 交互界面 (集成在主系统中)
echo   - 持续学习进程
echo   - 调试监控系统
echo.
echo 注意: 请保持命令窗口开启以维持后台进程运行
pause