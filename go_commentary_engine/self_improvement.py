"""
TW1.0.0 自我迭代强化模块
实现围棋AI解说引擎的自我学习与持续改进
"""

class SelfImprovementEngine:
    def __init__(self):
        self.performance_log = []
        self.analysis_accuracy = 0.0
        self.user_feedback_score = 0.0
        self.iteration_count = 0
        
    def evaluate_analysis_quality(self, analysis_result, expert_reference=None):
        """
        评估分析质量，为自我改进提供反馈信号
        """
        # 评估分析的准确性、专业性和有用性
        accuracy_score = self._assess_accuracy(analysis_result, expert_reference)
        professional_score = self._assess_professionalism(analysis_result)
        utility_score = self._assess_utility(analysis_result)
        
        overall_score = (accuracy_score * 0.5 + 
                        professional_score * 0.3 + 
                        utility_score * 0.2)
        
        return overall_score
    
    def _assess_accuracy(self, analysis_result, expert_reference):
        """评估分析准确性"""
        # 简化的准确性评估逻辑
        # 在实际应用中，这里会与专家参考答案进行对比
        if expert_reference:
            # 计算与专家分析的相似度
            similarity = self._calculate_similarity(analysis_result, expert_reference)
            return similarity
        else:
            # 基于内部一致性检查
            consistency_score = self._check_internal_consistency(analysis_result)
            return consistency_score
    
    def _assess_professionalism(self, analysis_result):
        """评估专业性"""
        # 检查是否使用了专业术语和概念
        professional_terms = [
            '外势', '实地', '厚薄', '急所', '大场', '手筋', '定式',
            '布局', '中盘', '官子', '劫争', '攻防', '平衡'
        ]
        
        term_count = sum(1 for term in professional_terms 
                        if term in analysis_result.lower())
        
        return min(term_count / 5.0, 1.0)  # 标准化到0-1范围
    
    def _assess_utility(self, analysis_result):
        """评估实用性"""
        # 检查分析是否包含具体建议和改进建议
        utility_indicators = [
            '建议', '改进', '更好', '应改', '不如', '推荐', '选择'
        ]
        
        indicator_count = sum(1 for indicator in utility_indicators 
                            if indicator in analysis_result)
        
        return min(indicator_count / 3.0, 1.0)  # 标准化到0-1范围
    
    def _calculate_similarity(self, result, reference):
        """计算两个分析结果的相似度"""
        # 简化的相似度计算
        result_words = set(result.lower().split())
        reference_words = set(reference.lower().split())
        
        intersection = len(result_words.intersection(reference_words))
        union = len(result_words.union(reference_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _check_internal_consistency(self, analysis_result):
        """检查分析内部一致性"""
        # 简化的内部一致性检查
        # 检查分析是否前后矛盾
        positive_indicators = ['好手', '正确', '优秀', '巧妙']
        negative_indicators = ['恶手', '错误', '糟糕', '失误']
        
        pos_count = sum(1 for indicator in positive_indicators 
                       if indicator in analysis_result)
        neg_count = sum(1 for indicator in negative_indicators 
                       if indicator in analysis_result)
        
        # 如果同时存在过多正面和负面评价，可能存在不一致
        inconsistency_penalty = min(pos_count, neg_count) * 0.1
        base_score = 0.8  # 基础一致性分数
        
        return max(0.0, base_score - inconsistency_penalty)
    
    def learn_from_experience(self, analysis_result, expert_reference=None, feedback_score=None):
        """
        从经验中学习，更新模型参数
        """
        # 计算本次分析的质量评分
        quality_score = self.evaluate_analysis_quality(analysis_result, expert_reference)
        
        # 如果有用户反馈，则结合用户反馈
        if feedback_score is not None:
            adjusted_score = (quality_score * 0.7 + feedback_score * 0.3)
        else:
            adjusted_score = quality_score
        
        # 记录性能日志
        self.performance_log.append({
            'iteration': self.iteration_count,
            'quality_score': quality_score,
            'feedback_score': feedback_score,
            'adjusted_score': adjusted_score,
            'analysis_result': analysis_result
        })
        
        # 更新总体准确率
        self.analysis_accuracy = self._calculate_moving_average()
        
        # 增加迭代计数
        self.iteration_count += 1
        
        # 如果性能有所下降，触发自适应调整
        if self._should_adjust_strategy():
            self._adjust_analysis_strategy()
        
        return adjusted_score
    
    def _calculate_moving_average(self, window_size=10):
        """计算移动平均准确率"""
        recent_scores = [entry['adjusted_score'] 
                        for entry in self.performance_log[-window_size:]]
        if not recent_scores:
            return 0.0
        return sum(recent_scores) / len(recent_scores)
    
    def _should_adjust_strategy(self):
        """判断是否需要调整策略"""
        if len(self.performance_log) < 5:
            return False
        
        recent_performance = [entry['adjusted_score'] 
                             for entry in self.performance_log[-5:]]
        previous_performance = [entry['adjusted_score'] 
                               for entry in self.performance_log[-10:-5]]
        
        if not previous_performance:
            return False
        
        recent_avg = sum(recent_performance) / len(recent_performance)
        prev_avg = sum(previous_performance) / len(previous_performance)
        
        # 如果最近表现比之前差超过阈值，则调整策略
        return (prev_avg - recent_avg) > 0.1
    
    def _adjust_analysis_strategy(self):
        """调整分析策略"""
        print("检测到性能下降，正在调整分析策略...")
        # 这里可以实现各种策略调整，例如：
        # - 调整术语权重
        # - 修改分析深度
        # - 调整专业性与易懂性的平衡
        pass
    
    def get_self_improvement_report(self):
        """生成自我改进报告"""
        report = {
            'total_iterations': self.iteration_count,
            'current_accuracy': self.analysis_accuracy,
            'performance_trend': self._get_performance_trend(),
            'recommended_improvements': self._get_recommendations()
        }
        return report
    
    def _get_performance_trend(self):
        """获取性能趋势"""
        if len(self.performance_log) < 2:
            return 'insufficient_data'
        
        recent_scores = [entry['adjusted_score'] 
                        for entry in self.performance_log[-5:]]
        earlier_scores = [entry['adjusted_score'] 
                         for entry in self.performance_log[-10:-5]]
        
        if not earlier_scores:
            return 'unknown'
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        if recent_avg > earlier_avg:
            return 'improving'
        elif recent_avg < earlier_avg:
            return 'declining'
        else:
            return 'stable'
    
    def _get_recommendations(self):
        """获取改进建议"""
        recommendations = []
        
        if self.analysis_accuracy < 0.7:
            recommendations.append("提高分析准确性：增加专业棋谱训练数据")
        
        if self._get_performance_trend() == 'declining':
            recommendations.append("性能下降：检查最近的分析策略调整")
        
        if self.iteration_count < 10:
            recommendations.append("增加训练数据以提升模型稳定性")
        
        return recommendations


# 使用示例
def demonstrate_self_improvement():
    """演示自我改进功能"""
    engine = SelfImprovementEngine()
    
    # 模拟几次分析和学习过程
    sample_analyses = [
        "这手棋是好手，加强了外势。",
        "此处应改下在别处，有更好的选择。",
        "这步棋符合定式，是正确下法。"
    ]
    
    for i, analysis in enumerate(sample_analyses):
        score = engine.learn_from_experience(analysis)
        print(f"迭代 {i+1}: 分析质量得分 = {score:.2f}")
    
    # 获取改进报告
    report = engine.get_self_improvement_report()
    print(f"\n自我改进报告:")
    print(f"总迭代次数: {report['total_iterations']}")
    print(f"当前准确率: {report['current_accuracy']:.2f}")
    print(f"性能趋势: {report['performance_trend']}")
    print(f"改进建议: {report['recommended_improvements']}")


if __name__ == "__main__":
    demonstrate_self_improvement()