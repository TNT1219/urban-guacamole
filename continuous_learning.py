#!/usr/bin/env python3
"""
TW1.0.0 持续学习与自我强化脚本
实现7x24小时不间断的自我迭代优化
"""

import time
import random
import json
import os
from datetime import datetime
from go_commentary_engine.self_improvement import SelfImprovementEngine
from training_data.professional_commentary_examples import *

class ContinuousLearningEngine:
    def __init__(self):
        self.improvement_engine = SelfImprovementEngine()
        self.is_running = False
        self.session_start_time = None
        self.iterations_completed = 0
        self.learning_log = []
        
        # 创建日志目录
        os.makedirs('logs', exist_ok=True)
        
    def load_training_data(self):
        """
        加载训练数据，包括专业棋谱和解说
        """
        # 模拟加载一些训练数据
        training_samples = [
            "这手棋体现了职业棋手的深远构思，既巩固了实地，又对上方白棋施加了压力。",
            "此处的定式选择显示出黑棋的深厚功力，后续变化极为复杂。",
            "白棋第37手是一步疑问手，错失了在左边展开的良机。",
            "黑棋的外势构建恰到好处，为后续的中腹作战奠定了坚实基础。",
            "官子阶段双方争夺激烈，每一步都关系到最终胜负。",
            "此手筋是局面的要点，充分体现了职业九段的敏锐嗅觉。",
            "白棋在这里选择了稳健的下法，虽然损失了些许先机，但避免了复杂的战斗。",
            "黑棋的攻击方向选择极佳，有效地发挥了子力的效率。",
        ]
        
        return training_samples
    
    def simulate_analysis(self, sample_text):
        """
        模拟棋局分析过程
        """
        # 在实际应用中，这里会调用真正的分析引擎
        # 目前我们模拟一个分析过程
        simulated_analysis = f"分析：{sample_text}。基于当前局面，这步棋的价值评分为{random.uniform(0.7, 0.95):.2f}，在专业比赛中出现频率约为{random.randint(60, 90)}%。"
        
        return simulated_analysis
    
    def run_iteration(self):
        """
        执行单次学习迭代
        """
        # 加载训练样本
        training_samples = self.load_training_data()
        
        # 随机选择一个样本进行分析
        sample = random.choice(training_samples)
        
        # 模拟分析过程
        analysis_result = self.simulate_analysis(sample)
        
        # 评估分析质量
        quality_score = random.uniform(0.6, 0.95)  # 模拟质量评分
        
        # 学习并更新模型
        score = self.improvement_engine.learn_from_experience(
            analysis_result=analysis_result,
            expert_reference=sample,
            feedback_score=quality_score
        )
        
        # 记录迭代信息
        iteration_record = {
            'timestamp': datetime.now().isoformat(),
            'iteration_id': self.iterations_completed,
            'input_sample': sample,
            'analysis_result': analysis_result,
            'quality_score': score,
            'engine_state': {
                'accuracy': self.improvement_engine.analysis_accuracy,
                'iterations': self.improvement_engine.iteration_count
            }
        }
        
        self.learning_log.append(iteration_record)
        self.iterations_completed += 1
        
        # 每10次迭代保存一次日志
        if self.iterations_completed % 10 == 0:
            self.save_learning_log()
            
        return iteration_record
    
    def save_learning_log(self):
        """
        保存学习日志
        """
        log_file = f"logs/learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_log, f, ensure_ascii=False, indent=2)
        
        # 只保留最近的几个日志文件
        self.cleanup_old_logs()
    
    def cleanup_old_logs(self):
        """
        清理旧的日志文件
        """
        log_dir = 'logs'
        log_files = [f for f in os.listdir(log_dir) if f.startswith('learning_session_') and f.endswith('.json')]
        
        # 只保留最近的5个日志文件
        if len(log_files) > 5:
            log_files.sort()
            for old_file in log_files[:-5]:
                os.remove(os.path.join(log_dir, old_file))
    
    def run_continuous_learning(self, iterations_per_hour=60):
        """
        运行持续学习过程
        默认每小时执行60次迭代（平均每分钟1次）
        """
        self.is_running = True
        self.session_start_time = datetime.now()
        
        print(f"[{self.session_start_time}] 开始持续学习会话...")
        print(f"目标：每小时 {iterations_per_hour} 次迭代")
        
        try:
            while self.is_running:
                start_time = time.time()
                
                # 执行单次迭代
                iteration_record = self.run_iteration()
                
                # 输出当前状态
                if self.iterations_completed % 10 == 0:
                    print(f"[{datetime.now()}] 已完成 {self.iterations_completed} 次迭代")
                    print(f"  - 当前质量评分: {iteration_record['quality_score']:.3f}")
                    print(f"  - 平均准确率: {self.improvement_engine.analysis_accuracy:.3f}")
                    
                    report = self.improvement_engine.get_self_improvement_report()
                    print(f"  - 性能趋势: {report['performance_trend']}")
                
                # 计算剩余等待时间以维持所需的迭代频率
                elapsed_time = time.time() - start_time
                sleep_time = max(0, 3600.0 / iterations_per_hour - elapsed_time)
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] 收到停止信号，正在保存进度...")
            self.stop_learning()
    
    def stop_learning(self):
        """
        停止学习过程
        """
        self.is_running = False
        end_time = datetime.now()
        
        if self.session_start_time:
            duration = end_time - self.session_start_time
            print(f"[{end_time}] 学习会话结束")
            print(f"总运行时间: {duration}")
            print(f"总迭代次数: {self.iterations_completed}")
            
            # 保存最终日志
            self.save_learning_log()
    
    def get_status_report(self):
        """
        获取当前状态报告
        """
        if not self.session_start_time:
            return "尚未开始学习会话"
        
        current_time = datetime.now()
        duration = current_time - self.session_start_time
        
        report = {
            'session_status': 'running' if self.is_running else 'stopped',
            'session_duration': str(duration),
            'iterations_completed': self.iterations_completed,
            'current_accuracy': self.improvement_engine.analysis_accuracy,
            'performance_trend': self.improvement_engine._get_performance_trend(),
            'recent_improvements': self.improvement_engine._get_recommendations()[-3:] if self.improvement_engine._get_recommendations() else []
        }
        
        return report


def main():
    """
    主函数：启动持续学习过程
    """
    print("=== TW1.0.0 持续学习与自我强化系统 ===")
    print("启动7x24小时不间断自我迭代优化...")
    
    engine = ContinuousLearningEngine()
    
    try:
        # 开始持续学习，每小时100次迭代（平均每36秒一次）
        engine.run_continuous_learning(iterations_per_hour=100)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        engine.stop_learning()


if __name__ == "__main__":
    main()