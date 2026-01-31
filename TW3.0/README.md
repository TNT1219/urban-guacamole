# TW3.0 - TW围棋解说引擎（完整版）

## 项目概述

TW3.0是一个专业级的围棋分析与解说系统，整合了TW1.0（核心分析引擎）和TW2.0（交互界面）的功能，并在此基础上进行了增强，形成了功能更强大的围棋AI系统。

## 功能特性

1. **实时分析**：用户在界面下棋时，系统实时提供分析
2. **意图识别**：深度分析每一步棋的意图
3. **多维度评估**：提供胜率、变化、死活、厚薄、轻重等多方面分析
4. **自我学习**：系统具备持续学习和改进的能力
5. **可视化界面**：直观展示棋局和分析结果
6. **SGF支持**：可导入和分析SGF格式的棋谱文件
7. **棋局导航**：支持在棋谱中前进、后退查看不同局面
8. **报告导出**：可导出详细的分析报告

## 文件结构

```
TW3.0/
├── integrated_system.py      # TW3.0集成系统（核心程序）
├── continuous_learning.py    # 持续学习模块
├── debug_monitor.py          # 调试监控系统
├── sgf_parser.py            # SGF棋谱解析模块
├── sgf_analyzer.py          # SGF棋谱分析模块
├── start_tw3.sh             # Linux/Mac一键启动脚本
├── start_tw3.bat            # Windows一键启动脚本
├── go_commentary_engine/    # 围棋解说引擎模块
│   ├── board.py             # 围棋棋盘类
│   ├── integrated_system.py # TW引擎集成系统
│   ├── interactive_interface.py # 交互界面模块
│   └── self_improvement.py  # 自我改进模块
├── docs/                    # 文档目录
│   ├── USAGE.md             # 基本使用说明
│   └── SGF_USAGE.md         # SGF功能使用说明
└── README.md                # 本说明文件
```

## 环境要求

- Python 3.7+
- tkinter (通常随Python一起安装)
- 2GB以上可用内存

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速启动

```bash
# 进入TW3.0目录
cd TW3.0/

# 给启动脚本授权（Linux/Mac）
chmod +x start_tw3.sh

# Linux/Mac启动系统
./start_tw3.sh

# Windows启动系统
start_tw3.bat
```

## 使用说明

详见 `docs/USAGE.md` 和 `docs/SGF_USAGE.md` 文件。