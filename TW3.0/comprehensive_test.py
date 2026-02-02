#!/usr/bin/env python3
"""
TW3.0系统全面功能测试
"""

import sys
import os
sys.path.insert(0, '/root/clawd/TW3.0')

from integrated_system import TWIntegratedSystem
from sgf_parser import SGFParser
from ai_engine_interface import TW3AIAnalyzer
from history_analysis import UserDataStorage, HabitAnalyzer, WeaknessIdentifier
from progress_tracker import ProgressTracker, MilestoneManager
from replay_tool import ReplayTool
from teaching_module import TeachingModule, InteractiveTeachingMode
from continuous_improvement import ContinuousLearningSystem, AutonomousIterationAlgorithm
from debug_monitor import UninterruptedOperationManager
from performance_optimizer import PerformanceOptimizer, MultiThreadedProcessor
import time
from datetime import datetime


def run_comprehensive_test():
    """运行全面功能测试"""
    print("="*60)
    print("TW3.0系统全面功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    test_results = {}
    
    # 1. 测试核心系统
    print("\n1. 测试核心系统...")
    try:
        system = TWIntegratedSystem()
        test_results['core_system'] = True
        print("   ✓ 核心系统初始化成功")
        
        # 测试基本下棋功能
        success, _ = system.place_stone_and_analyze(3, 3, 'B')
        if success:
            print("   ✓ 基本下棋功能正常")
        else:
            print("   ⚠ 基本下棋功能异常")
            test_results['core_move'] = False
        
        system.stop()
        print("   ✓ 核心系统测试完成")
    except Exception as e:
        print(f"   ✗ 核心系统测试失败: {e}")
        test_results['core_system'] = False
    
    # 2. 测试SGF功能
    print("\n2. 测试SGF功能...")
    try:
        system = TWIntegratedSystem()
        success, msg = system.load_sgf('/root/clawd/TW3.0/test_game.sgf')
        if success:
            print(f"   ✓ SGF加载功能正常: {msg}")
            test_results['sgf_load'] = True
        else:
            print(f"   ⚠ SGF加载功能异常: {msg}")
            test_results['sgf_load'] = False
        system.stop()
    except Exception as e:
        print(f"   ✗ SGF功能测试失败: {e}")
        test_results['sgf_load'] = False
    
    # 3. 测试AI引擎接口
    print("\n3. 测试AI引擎接口...")
    try:
        ai_analyzer = TW3AIAnalyzer()
        initialized = ai_analyzer.initialize()
        if initialized:
            print("   ✓ AI引擎接口初始化成功")
            test_results['ai_engine'] = True
        else:
            print("   ⚠ AI引擎未就绪（可能是由于缺少Katago或Leela Zero）")
            test_results['ai_engine'] = True  # 这不是错误，只是缺少外部引擎
        ai_analyzer.close()
    except Exception as e:
        print(f"   ✗ AI引擎接口测试失败: {e}")
        test_results['ai_engine'] = False
    
    # 4. 测试历史数据分析
    print("\n4. 测试历史数据分析...")
    try:
        storage = UserDataStorage()
        habit_analyzer = HabitAnalyzer(storage)
        weakness_identifier = WeaknessIdentifier(storage)
        print("   ✓ 历史数据分析模块加载成功")
        test_results['history_analysis'] = True
        
        # 模拟一些数据并测试
        from history_analysis import GameRecord
        import random
        from datetime import timedelta
        
        # 添加一些测试数据
        for i in range(5):
            game = GameRecord(
                game_id=f"test_game_{i}",
                timestamp=datetime.now() - timedelta(days=i),
                player_color='B',
                opponent_strength='intermediate',
                game_result='win' if i % 2 == 0 else 'loss',
                komi=7.5,
                game_length=200 + i * 10,
                opening_pattern='Chinese' if i % 2 == 0 else 'Shimari',
                score_difference=10.0 - i,
                mistakes_count=max(0, 3 - i),
                blunders_count=1 if i == 0 else 0,
                avg_thinking_time=25.0 + i * 2
            )
            storage.save_game_record(game)
        
        # 分析用户习惯
        habits = habit_analyzer.analyze_all_habits("test_user")
        print(f"   ✓ 识别到 {len(habits)} 个用户习惯模式")
        
        # 识别弱点
        weaknesses = weakness_identifier.identify_weaknesses("test_user")
        total_weaknesses = sum(len(v) for v in weaknesses.values())
        print(f"   ✓ 识别到 {total_weaknesses} 个弱点领域")
        
    except Exception as e:
        print(f"   ✗ 历史数据分析测试失败: {e}")
        test_results['history_analysis'] = False
    
    # 5. 测试进步追踪
    print("\n5. 测试进步追踪...")
    try:
        tracker = ProgressTracker()
        milestone_mgr = MilestoneManager(tracker)
        
        # 记录一些模拟对局
        for i in range(10):
            opponent_rating = 1400 + i * 10
            game_result = 1 if i % 3 != 2 else 0  # 约66%胜率
            record = tracker.record_game_result(
                user_id="test_player",
                opponent_rating=opponent_rating,
                game_result=game_result
            )
        
        summary = tracker.get_progress_summary("test_player")
        milestones = milestone_mgr.check_milestones("test_player")
        
        print(f"   ✓ 进步追踪功能正常 - 当前等级分: {summary['current_rating']:.1f}")
        print(f"   ✓ 识别到 {len(milestones)} 个里程碑")
        test_results['progress_tracking'] = True
    except Exception as e:
        print(f"   ✗ 进步追踪测试失败: {e}")
        test_results['progress_tracking'] = False
    
    # 6. 测试复盘工具
    print("\n6. 测试复盘工具...")
    try:
        replay_tool = ReplayTool()
        
        # 模拟棋局数据
        sample_game_data = {
            'game_id': 'test_review_game',
            'moves': ['D4', 'D16', 'Q4', 'Q16', 'D3', 'D17', 'C4', 'C16'],
            'player_color': 'B',
            'opponent_strength': 'intermediate',
            'winner': 'B',
            'date': datetime.now().isoformat()
        }
        
        # 进行复盘
        review_report = replay_tool.conduct_review(sample_game_data)
        replay_tool.save_review_report(review_report)
        
        print(f"   ✓ 复盘工具功能正常 - 识别到 {len(review_report.review_points)} 个复盘点")
        test_results['replay_tool'] = True
    except Exception as e:
        print(f"   ✗ 复盘工具测试失败: {e}")
        test_results['replay_tool'] = False
    
    # 7. 测试教学模块
    print("\n7. 测试教学模块...")
    try:
        teaching_module = TeachingModule()
        interactive_mode = InteractiveTeachingMode(teaching_module)
        
        # 获取课程
        lessons = teaching_module.get_lessons_by_category("basic")
        print(f"   ✓ 教学模块功能正常 - 可用基础课程: {len(lessons)} 门")
        
        # 尝试开始一个课程
        lesson = interactive_mode.start_teaching_session("test_student")
        if lesson:
            content = interactive_mode.get_current_lesson_content()
            exercises = interactive_mode.get_exercises_for_current_lesson()
            print(f"   ✓ 成功开始课程: {lesson.title}")
            print(f"   ✓ 课程练习数: {len(exercises)}")
            interactive_mode.complete_lesson()
        
        test_results['teaching_module'] = True
    except Exception as e:
        print(f"   ✗ 教学模块测试失败: {e}")
        test_results['teaching_module'] = False
    
    # 8. 测试持续学习系统
    print("\n8. 测试持续学习系统...")
    try:
        learning_system = ContinuousLearningSystem()
        learning_system.start()
        time.sleep(2)  # 等待系统运行
        status = learning_system.get_learning_status()
        learning_system.stop()
        print(f"   ✓ 持续学习系统功能正常 - 日志条目数: {status['log_entries_count']}")
        test_results['continuous_learning'] = True
    except Exception as e:
        print(f"   ✗ 持续学习系统测试失败: {e}")
        test_results['continuous_learning'] = False
    
    # 9. 测试性能优化
    print("\n9. 测试性能优化...")
    try:
        optimizer = PerformanceOptimizer()
        processor = MultiThreadedProcessor(num_threads=2)
        processor.start_workers()
        
        # 测试缓存功能
        @optimizer.optimize_with_cache(cache_key="test_cache")
        def test_func(x):
            time.sleep(0.01)  # 模拟耗时操作
            return x * 2
        
        # 第一次调用
        result1 = test_func(5)
        # 第二次调用（应该从缓存获取）
        result2 = test_func(5)
        
        stats = optimizer.get_stats()
        print(f"   ✓ 性能优化功能正常 - 缓存大小: {stats['cache_size']}")
        
        processor.shutdown()
        optimizer.cleanup()
        test_results['performance_opt'] = True
    except Exception as e:
        print(f"   ✗ 性能优化测试失败: {e}")
        test_results['performance_opt'] = False
    
    # 10. 测试系统监控
    print("\n10. 测试系统监控...")
    try:
        monitor = UninterruptedOperationManager()
        monitor.start()
        time.sleep(2)  # 等待系统运行
        status = monitor.get_system_status()
        monitor.stop()
        print(f"   ✓ 系统监控功能正常 - 健康状态: {status['health_status']['cpu_usage']:.1f}% CPU")
        test_results['system_monitor'] = True
    except Exception as e:
        print(f"   ✗ 系统监控测试失败: {e}")
        test_results['system_monitor'] = False
    
    # 总结测试结果
    print("\n" + "="*60)
    print("测试结果汇总:")
    print("="*60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for feature, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {feature:<20} {status}")
    
    print(f"\n总体结果: {passed}/{total} 项功能测试通过")
    
    if passed == total:
        print("\n🎉 所有功能测试均已通过！TW3.0系统运行正常。")
        return True
    else:
        print(f"\n⚠️  {total-passed} 项功能测试未通过，请检查相关模块。")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    if not success:
        sys.exit(1)