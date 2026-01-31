#!/bin/bash

# TW3.0 一键启动脚本
# 启动TW Go Commentary Engine集成系统

echo "正在启动 TW Go Commentary Engine (TW3.0)..."
echo "时间: $(date)"

# 检查Python环境
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "使用Python命令: $PYTHON_CMD"

# 启动调试监控（后台）
echo "启动调试监控..."
$PYTHON_CMD debug_monitor.py &
DEBUG_PID=$!

# 启动持续学习进程（后台）
echo "启动持续学习进程..."
$PYTHON_CMD continuous_learning.py &
LEARNING_PID=$!

# 稍等片刻让服务启动
sleep 2

echo "TW3.0核心服务已启动!"
echo "调试监控PID: $DEBUG_PID"
echo "持续学习PID: $LEARNING_PID"

echo ""
echo "系统包含以下组件:"
echo "- TW1.0 分析引擎 (集成在主系统中)"
echo "- TW2.0 交互界面 (集成在主系统中)"
echo "- 持续学习进程"
echo "- 调试监控系统"
echo ""

echo "要使用系统，请运行: $PYTHON_CMD -c \"from integrated_system import TWIntegratedSystem; system = TWIntegratedSystem()\""
echo "要停止系统，请运行: pkill -f 'python.*\(continuous_learning\|debug_monitor\)'"