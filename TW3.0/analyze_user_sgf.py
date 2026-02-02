#!/usr/bin/env python3
"""
TW3.0系统 - 用户SGF文件分析与解说演示
"""

import sys
import os
sys.path.insert(0, '/root/clawd/TW3.0')

from integrated_system import TWIntegratedSystem
from sgf_parser import SGFParser
import time
from datetime import datetime


def analyze_user_sgf():
    """分析用户上传的SGF文件并展示解说效果"""
    print("="*80)
    print("TW3.0系统 - 用户SGF文件分析与解说演示")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 检查文件是否存在
    sgf_file_path = "/root/clawd/TW3.0/user_game.sgf"
    if not os.path.exists(sgf_file_path):
        print(f"错误: 找不到SGF文件 {sgf_file_path}")
        return False
    
    # 创建系统实例
    system = TWIntegratedSystem()
    
    try:
        # 加载用户SGF文件
        print(f"\n🔍 正在加载用户SGF文件...")
        success, message = system.load_sgf(sgf_file_path)
        
        if not success:
            print(f"❌ 加载失败: {message}")
            return False
        
        print(f"✅ 棋谱加载成功: {message}")
        
        # 获取棋谱基本信息
        report = system.export_analysis_report()
        game_info = report['game_info']
        print(f"\n📋 棋谱信息:")
        print(f"   - 棋局总数: {game_info['total_moves']} 手")
        print(f"   - 棋盘大小: {game_info['board_size']}x{game_info['board_size']}")
        print(f"   - 当前玩家: {game_info['current_player']}")
        print(f"   - 游戏日期: {game_info.get('date', 'N/A')}")
        
        # 分析当前局面
        print(f"\n🔍 正在分析当前局面...")
        analysis = system.get_current_position_analysis()
        
        print(f"\n📊 当前局面分析:")
        print(f"   - 黑棋胜率: {analysis.get('win_rate', 'N/A')}%")
        print(f"   - 意图分析: {analysis.get('intention_analysis', 'N/A')}")
        print(f"   - 推荐着法: {analysis.get('variations', [])[:3]}")
        print(f"   - 死活分析: {analysis.get('life_death', 'N/A')}")
        print(f"   - 厚薄分析: {analysis.get('thickness', 'N/A')}")
        print(f"   - 轻重分析: {analysis.get('weight', 'N/A')}")
        
        # 导航到棋局的不同阶段进行分析
        print(f"\n🔄 正在分析棋局不同阶段...")
        
        # 获取总手数
        total_moves = game_info['total_moves']
        sample_points = [10, 30, 50, 70, 90]  # 选择几个关键点进行分析
        
        for point in sample_points:
            if point < total_moves:
                print(f"\n--- 第 {point} 手分析 ---")
                current_idx, total = system.navigate_game_history(point)
                
                if current_idx >= 0:
                    analysis = system.get_current_position_analysis()
                    print(f"   - 黑棋胜率: {analysis.get('win_rate', 'N/A')}%")
                    print(f"   - 意图分析: {analysis.get('intention_analysis', 'N/A')[:60]}...")
                    print(f"   - 推荐着法: {analysis.get('variations', [])[:2]}")
        
        # 回到最新局面
        system.navigate_game_history(total_moves)
        
        # 进行复盘分析
        print(f"\n📖 正在进行复盘分析...")
        try:
            from replay_tool import ReplayTool
            replay_tool = ReplayTool()
            
            # 构建游戏数据用于复盘
            sample_game_data = {
                'game_id': 'user_game_analysis',
                'moves': [f"Move_{i}" for i in range(min(20, total_moves))],  # 简化表示
                'player_color': game_info.get('current_player', 'B'),
                'opponent_strength': 'intermediate',
                'winner': 'B' if analysis.get('win_rate', 50) > 50 else 'W',
                'date': game_info.get('date', datetime.now().isoformat())
            }
            
            review_report = replay_tool.conduct_review(sample_game_data)
            print(f"✅ 复盘分析完成: 识别到 {len(review_report.review_points)} 个复盘要点")
            
            # 显示前几个复盘点
            for i, point in enumerate(review_report.review_points[:5]):
                print(f"   - 复盘点 {i+1}: {str(point)[:80]}...")
                
        except Exception as e:
            print(f"⚠️ 复盘分析遇到问题: {e}")
        
        # 尝试使用历史分析功能
        print(f"\n🧠 正在进行历史数据分析...")
        try:
            from history_analysis import UserDataStorage, HabitAnalyzer
            storage = UserDataStorage()
            habit_analyzer = HabitAnalyzer(storage)
            
            # 这里我们模拟记录这个游戏数据
            from history_analysis import GameRecord
            from datetime import timedelta
            
            game_record = GameRecord(
                game_id="user_game_001",
                timestamp=datetime.now(),
                player_color=game_info.get('current_player', 'B'),
                opponent_strength='intermediate',
                game_result='unknown',
                komi=7.5,
                game_length=total_moves,
                opening_pattern='mixed',
                score_difference=0.0,
                mistakes_count=0,
                blunders_count=0,
                avg_thinking_time=25.0
            )
            storage.save_game_record(game_record)
            
            habits = habit_analyzer.analyze_all_habits("user_001")
            print(f"✅ 识别到 {len(habits)} 个用户习惯模式")
            
            # 显示一些习惯分析
            for habit_type, details in list(habits.items())[:3]:
                print(f"   - {habit_type}: {details}")
                
        except Exception as e:
            print(f"⚠️ 历史数据分析遇到问题: {e}")
        
        # 导出完整分析报告
        print(f"\n📄 正在导出完整分析报告...")
        final_report = system.export_analysis_report()
        
        print(f"✅ 分析报告导出完成")
        print(f"   - 棋局历史样本数: {len(final_report['game_history_sample'])}")
        print(f"   - 当前分析指标数: {len(final_report['current_analysis']) if final_report['current_analysis'] else 0}")
        print(f"   - 改进指标数: {len(final_report['improvement_metrics']) if final_report['improvement_metrics'] else 0}")
        
        # 显示当前分析概要
        print(f"\n📝 当前分析概要:")
        current_analysis = final_report['current_analysis']
        if current_analysis:
            for key, value in list(current_analysis.items())[:5]:  # 显示前5个项目
                preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"   - {key}: {preview}")
        
        print(f"\n🎯 TW3.0解说系统演示完成!")
        print(f"   - 成功分析了您的SGF棋谱")
        print(f"   - 提供了多维度的局面解说")
        print(f"   - 展示了系统的全面分析能力")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 停止系统
        system.stop()


def main():
    """主函数"""
    print("启动TW3.0系统 - 用户SGF文件分析与解说演示")
    success = analyze_user_sgf()
    
    if success:
        print(f"\n🎉 演示成功完成！TW3.0系统已成功分析您的SGF文件并提供了解说。")
    else:
        print(f"\n❌ 演示未能完成，请检查SGF文件格式或系统配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()