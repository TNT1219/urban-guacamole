#!/bin/bash
"""
TW3.0系统完整启动脚本
启动所有系统组件，包括核心引擎、持续学习、监控等
"""

echo "==========================================="
echo "    TW3.0围棋解说引擎完整启动脚本"
echo "==========================================="

# 设置环境变量
export PYTHONPATH="/root/clawd/TW3.0:$PYTHONPATH"

# 创建必要的目录
mkdir -p /root/clawd/TW3.0/logs
mkdir -p /root/clawd/TW3.0/backups
mkdir -p /root/clawd/TW3.0/learning_data

echo "[1/5] 启动TW3.0核心系统..."

# 启动核心系统（后台运行）
python3 /root/clawd/TW3.0/integrated_system.py > /root/clawd/TW3.0/logs/core_system.log 2>&1 &
CORE_PID=$!
echo "核心系统PID: $CORE_PID"

echo "[2/5] 启动持续学习系统..."

# 启动持续学习系统（后台运行）
python3 /root/clawd/TW3.0/continuous_improvement.py > /root/clawd/TW3.0/logs/learning_system.log 2>&1 &
LEARNING_PID=$!
echo "持续学习系统PID: $LEARNING_PID"

echo "[3/5] 启动系统监控与异常恢复..."

# 启动监控系统（后台运行）
python3 /root/clawd/TW3.0/debug_monitor.py > /root/clawd/TW3.0/logs/monitor_system.log 2>&1 &
MONITOR_PID=$!
echo "监控系统PID: $MONITOR_PID"

echo "[4/5] 初始化AI分析引擎..."

# 检查是否已安装katago
if command -v katago &> /dev/null; then
    echo "Katago引擎已安装"
else
    echo "警告: Katago引擎未安装，将使用模拟AI分析"
    echo "如需安装Katago，请运行: pip install katago"
fi

echo "[5/5] 启动完成，系统正在运行..."

# 创建PID文件以便管理
echo "$CORE_PID" > /root/clawd/TW3.0/tw3_core.pid
echo "$LEARNING_PID" > /root/clawd/TW3.0/tw3_learning.pid
echo "$MONITOR_PID" > /root/clawd/TW3.0/tw3_monitor.pid

echo ""
echo "==========================================="
echo "TW3.0系统已成功启动！"
echo "==========================================="
echo "核心系统 PID: $CORE_PID"
echo "学习系统 PID: $LEARNING_PID" 
echo "监控系统 PID: $MONITOR_PID"
echo ""
echo "日志文件位置:"
echo "  - 核心系统: /root/clawd/TW3.0/logs/core_system.log"
echo "  - 学习系统: /root/clawd/TW3.0/logs/learning_system.log"
echo "  - 监控系统: /root/clawd/TW3.0/logs/monitor_system.log"
echo ""
echo "要停止系统，请运行: ./stop_tw3.sh"
echo "==========================================="

# 输出系统状态
echo ""
echo "当前系统状态:"
python3 -c "
import sys
sys.path.insert(0, '/root/clawd/TW3.0')
try:
    from integrated_system import TWIntegratedSystem
    print('- 核心系统: 可用')
except ImportError as e:
    print(f'- 核心系统: 错误 - {e}')

try:
    from continuous_improvement import ContinuousLearningSystem
    print('- 学习系统: 可用')
except ImportError as e:
    print(f'- 学习系统: 错误 - {e}')

try:
    from debug_monitor import UninterruptedOperationManager
    print('- 监控系统: 可用')
except ImportError as e:
    print(f'- 监控系统: 错误 - {e}')
"