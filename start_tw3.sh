#!/bin/bash

# TW3.0 一键启动脚本
# 启动TW Go Commentary Engine集成系统

echo "正在启动 TW Go Commentary Engine (TW3.0)..."
echo "时间: $(date)"

# 检查Python环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 启动TW3.0集成系统
echo "启动TW3.0集成系统..."
python go_commentary_engine/integrated_system.py &

# 启动持续学习进程
echo "启动持续学习进程..."
python continuous_learning.py &

# 启动调试监控
echo "启动调试监控..."
python debug_monitor.py &

echo "TW3.0系统已启动!"
echo "PID列表:"
jobs -p

echo "系统包含以下组件:"
echo "- TW1.0 分析引擎 (集成在主系统中)"
echo "- TW2.0 交互界面 (集成在主系统中)"
echo "- 持续学习进程"
echo "- 调试监控系统"

echo "要停止系统，请运行: pkill -f 'python.*\(integrated_system\|continuous_learning\|debug_monitor\)'"