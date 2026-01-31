# TW3.0 SGF棋谱分析功能使用说明

## 功能概述
TW3.0现在支持SGF格式的围棋棋谱分析功能，可以导入并分析现有的围棋对局。

## 环境准备
首先安装必要的依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法一：命令行分析
将您的SGF文件放在与程序相同的目录中，然后运行：
```bash
python sgf_analyzer.py your_game.sgf
```

### 方法二：在Python代码中使用
```python
from sgf_analyzer import TW3SGFAnalyzer

analyzer = TW3SGFAnalyzer()
report = analyzer.load_and_analyze_sgf('your_game.sgf')
analyzer.print_detailed_analysis(report)
```

## 功能特性

1. **SGF解析**：支持标准SGF格式的棋谱文件
2. **对局信息提取**：自动提取对局双方、结果、时间等信息
3. **逐手分析**：对每一手棋进行意图分析
4. **阶段划分**：按布局、中盘、官子等阶段进行分析
5. **关键节点识别**：识别棋局中的关键时刻

## 输出内容

分析报告包含：
- 对局基本信息（棋手、结果、手数等）
- 棋局阶段分析
- 关键时刻识别
- 每10手的详细分析
- 整体评述

## 注意事项

1. 目前SGF分析功能为独立模块，与主界面的实时分析功能不同
2. 分析结果基于TW3.0的分析引擎，但不包含实时互动功能
3. 支持19路、13路、9路棋盘的SGF文件

## 文件说明

- `sgf_parser.py`: SGF解析器
- `sgf_analyzer.py`: TW3.0专用SGF分析器
- `docs/SGF_USAGE.md`: 本文档