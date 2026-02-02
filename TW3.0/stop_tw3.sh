#!/bin/bash
"""
TW3.0系统停止脚本
停止所有系统组件
"""

echo "==========================================="
echo "    TW3.0围棋解说引擎停止脚本"
echo "==========================================="

# 读取PID并停止进程
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo "停止$process_name (PID: $PID)..."
            kill $PID
            sleep 2
            # 再次检查进程是否还存在
            if ps -p $PID > /dev/null 2>&1; then
                echo "$process_name仍在运行，强制停止..."
                kill -9 $PID
            fi
            rm -f "$pid_file"
            echo "$process_name已停止"
        else
            echo "$process_name (PID: $PID) 未在运行"
            rm -f "$pid_file"
        fi
    else
        echo "$process_name 未找到PID文件"
    fi
}

# 停止各个组件
stop_process "/root/clawd/TW3.0/tw3_monitor.pid" "监控系统"
stop_process "/root/clawd/TW3.0/tw3_learning.pid" "学习系统" 
stop_process "/root/clawd/TW3.0/tw3_core.pid" "核心系统"

echo ""
echo "==========================================="
echo "TW3.0系统已停止"
echo "==========================================="