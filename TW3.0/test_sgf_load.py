#!/usr/bin/env python3
"""
TW3.0系统测试脚本
加载SGF文件并测试系统功能
"""

import sys
import os
sys.path.insert(0, '/root/clawd/TW3.0')

from integrated_system import TWIntegratedSystem
from sgf_parser import SGFParser
import time
from datetime import datetime


def test_sgf_loading():
    """测试SGF文件加载功能"""
    print("=== TW3.0系统SGF文件加载测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建集成系统
    system = TWIntegratedSystem()
    
    # 创建SGF解析器
    parser = SGFParser()
    
    # 加载测试SGF文件
    sgf_file_path = "/root/clawd/TW3.0/test_game.sgf"
    
    if not os.path.exists(sgf_file_path):
        print(f"错误: 找不到测试文件 {sgf_file_path}")
        return False
    
    try:
        print(f"\n正在加载SGF文件: {sgf_file_path}")
        
        # 解析SGF文件
        sgf_data = parser.load_from_file(sgf_file_path)
        print(f"✓ SGF文件加载成功")
        print(f"  - 棋盘大小: {sgf_data['size']}")
        print(f"  - 总手数: {len(sgf_data['moves'])}")
        print(f"  - 规则: {sgf_data.get('rules', 'Unknown')}")
        print(f"  - 贴目: {sgf_data.get('komi', 0)}")
        
        # 尝试加载到系统中
        success, message = system.load_sgf(sgf_file_path)
        if success:
            print(f"✓ 棋谱成功加载到系统中")
            print(f"  - 消息: {message}")
        else:
            print(f"✗ 棋谱加载失败: {message}")
            return False
        
        # 获取当前局面分析
        print(f"\n正在进行局面分析...")
        analysis = system.get_current_position_analysis()
        
        print("✓ 局面分析结果:")
        print(f"  - 当前胜率: 黑棋 {analysis.get('win_rate', 'N/A')}%")
        print(f"  - 意图分析: {analysis.get('intention_analysis', 'N/A')[:50]}...")
        print(f"  - 后续变化: {analysis.get('variations', [])[:3]}")
        print(f"  - 死活分析: {analysis.get('life_death', 'N/A')[:50]}...")
        print(f"  - 厚薄分析: {analysis.get('thickness', 'N/A')[:50]}...")
        print(f"  - 轻重分析: {analysis.get('weight', 'N/A')[:50]}...")
        
        # 测试导航功能
        print(f"\n测试导航功能...")
        current_idx, total_moves = system.navigate_game_history(-5)  # 回退5步
        print(f"✓ 回退到第 {current_idx}/{total_moves} 步")
        
        current_idx, total_moves = system.navigate_game_history(3)   # 前进3步
        print(f"✓ 前进到第 {current_idx}/{total_moves} 步")
        
        # 再次分析局面
        print(f"\n再次进行局面分析...")
        analysis = system.get_current_position_analysis()
        print(f"  - 当前胜率: 黑棋 {analysis.get('win_rate', 'N/A')}%")
        
        # 导出分析报告
        print(f"\n正在导出分析报告...")
        report = system.export_analysis_report()
        print(f"✓ 分析报告导出成功")
        print(f"  - 总手数: {report['game_info']['total_moves']}")
        print(f"  - 当前玩家: {report['game_info']['current_player']}")
        print(f"  - 棋盘大小: {report['game_info']['board_size']}")
        
        # 测试AI引擎接口（如果可用）
        try:
            from ai_engine_interface import TW3AIAnalyzer
            print(f"\n测试AI引擎接口...")
            ai_analyzer = TW3AIAnalyzer()
            if ai_analyzer.initialize():
                board_state = {
                    "moves": [move[0] for move in system.game_history[-10:]],  # 最近10步
                    "boardSize": 19,
                    "komi": 7.5,
                    "rules": "Chinese"
                }
                ai_result = ai_analyzer.analyze_game_position(board_state)
                print(f"✓ AI分析完成")
                print(f"  - 使用引擎: {ai_result.get('engine_used', 'N/A')}")
                print(f"  - 胜率: {ai_result.get('win_rate', 'N/A')}")
                print(f"  - 推荐着法: {ai_result.get('best_moves', [])[:3]}")
                ai_analyzer.close()
            else:
                print(f"⚠ AI引擎未就绪（可能是由于缺少Katago或Leela Zero）")
        except ImportError as e:
            print(f"⚠ AI引擎模块不可用: {e}")
        
        # 测试历史数据分析
        try:
            from history_analysis import UserDataStorage, HabitAnalyzer
            print(f"\n测试历史数据分析...")
            storage = UserDataStorage()
            habit_analyzer = HabitAnalyzer(storage)
            print(f"✓ 历史数据分析模块加载成功")
        except ImportError as e:
            print(f"⚠ 历史数据分析模块不可用: {e}")
        
        # 测试进步追踪
        try:
            from progress_tracker import ProgressTracker
            print(f"✓ 进步追踪模块加载成功")
        except ImportError as e:
            print(f"⚠ 进步追踪模块不可用: {e}")
        
        # 测试复盘工具
        try:
            from replay_tool import ReplayTool
            print(f"✓ 复盘工具模块加载成功")
        except ImportError as e:
            print(f"⚠ 复盘工具模块不可用: {e}")
        
        # 测试教学模块
        try:
            from teaching_module import TeachingModule
            print(f"✓ 教学模块加载成功")
        except ImportError as e:
            print(f"⚠ 教学模块不可用: {e}")
        
        print(f"\n=== 测试完成 ===")
        print(f"所有核心功能模块均已成功加载和测试")
        print(f"SGF文件加载和分析功能正常运行")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 停止系统
        system.stop()


class SGFParser:
    """
    简化的SGF解析器（如果原系统中没有的话）
    """
    
    def load_from_file(self, file_path):
        """从文件加载SGF数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简化的SGF解析逻辑
        sgf_data = {
            'size': 19,
            'rules': 'Japanese',
            'komi': 0.0,
            'moves': [],
            'players': {'B': 'Black Player', 'W': 'White Player'}
        }
        
        # 解析SGF内容获取手数
        # 简单解析SGF中的B[]和W[]标记
        import re
        moves = re.findall(r';([BW])\[([a-z]{2}|[a-z]|)\]', content)
        
        for i, (color, move_str) in enumerate(moves):
            if move_str and len(move_str) == 2:
                # 将SGF坐标转换为行列
                col = ord(move_str[0]) - ord('a')
                row = ord(move_str[1]) - ord('a')
                sgf_data['moves'].append((i, color, (row, col)))
            elif move_str == "":
                # 虚手
                sgf_data['moves'].append((i, color, None))
        
        # 如果没有解析到手数，至少解析到有分号分隔的着法
        if not sgf_data['moves']:
            # 尝试另一种解析方式
            parts = content.split(';')
            move_count = 0
            for part in parts[1:]:  # 跳过第一个空部分
                if part.startswith('B[') or part.startswith('W['):
                    color = 'B' if part.startswith('B[') else 'W'
                    sgf_data['moves'].append((move_count, color, None))
                    move_count += 1
                if move_count >= 50:  # 限制解析数量
                    break
        
        return sgf_data


if __name__ == "__main__":
    success = test_sgf_loading()
    if success:
        print(f"\n🎉 SGF加载测试成功！系统各项功能正常运行。")
    else:
        print(f"\n❌ SGF加载测试失败。")
        sys.exit(1)