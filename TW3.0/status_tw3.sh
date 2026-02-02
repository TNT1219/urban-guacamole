#!/bin/bash
"""
TW3.0系统状态检查脚本
检查所有系统组件的运行状态
"""

echo "==========================================="
echo "    TW3.0围棋解说引擎系统状态"
echo "==========================================="

check_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo "$process_name: 运行中 (PID: $PID)"
            # 获取进程的一些基本信息
            CPU=$(ps -p $PID -o %cpu --no-headers 2>/dev/null || echo "N/A")
            MEM=$(ps -p $PID -o %mem --no-headers 2>/dev/null || echo "N/A")
            echo "  CPU使用率: $CPU%, 内存使用率: $MEM%"
        else
            echo "$process_name: 未运行 (PID: $PID, PID文件存在但进程不存在)"
        fi
    else
        echo "$process_name: 未运行 (PID文件不存在)"
    fi
    echo ""
}

# 检查各个组件
check_process "/root/clawd/TW3.0/tw3_core.pid" "核心系统"
check_process "/root/clawd/TW3.0/tw3_learning.pid" "学习系统"
check_process "/root/clawd/TW3.0/tw3_monitor.pid" "监控系统"

# 检查日志文件
echo "最近的日志信息:"
echo ""
echo "--- 核心系统日志 (最后5行) ---"
if [ -f "/root/clawd/TW3.0/logs/core_system.log" ]; then
    tail -n 5 "/root/clawd/TW3.0/logs/core_system.log"
else
    echo "日志文件不存在"
fi

echo ""
echo "--- 学习系统日志 (最后5行) ---"
if [ -f "/root/clawd/TW3.0/logs/learning_system.log" ]; then
    tail -n 5 "/root/clawd/TW3.0/logs/learning_system.log"
else
    echo "日志文件不存在"
fi

echo ""
echo "--- 监控系统日志 (最后5行) ---"
if [ -f "/root/clawd/TW3.0/logs/monitor_system.log" ]; then
    tail -n 5 "/root/clawd/TW3.0/logs/monitor_system.log"
else
    echo "日志文件不存在"
fi

echo ""
echo "==========================================="
echo "系统状态检查完成"
echo "==========================================="