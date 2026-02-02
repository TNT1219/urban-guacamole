
"""
轻重分析模块 - TW3.0解说能力增强
用于判断棋子轻重缓急
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


class ImportanceLevel(Enum):
    """重要性等级"""
    CRITICAL = "至关重要"
    HIGH = "非常重要"
    MEDIUM = "一般重要"
    LOW = "不太重要"


@dataclass
class ImportanceAnalysisResult:
    """轻重分析结果"""
    importance_level: ImportanceLevel  # 重要性等级
    strategic_value: float            # 战略价值
    tactical_necessity: float         # 战术必要性
    risk_factor: float               # 风险系数
    recommendations: List[str]       # 应对建议
    explanation: str                 # 解释


class ImportanceAnalyzer:
    """轻重分析器"""
    
    def __init__(self):
        self.name = "TW3.0轻重分析器"
        self.version = "1.0"
    
    def analyze_importance(
        self, 
        board_state, 
        stones: List[Tuple[int, int]], 
        context: dict = None
    ) -> ImportanceAnalysisResult:
        """
        分析棋子轻重缓急
        """
        # 评估战略价值
        strategic_value = self._evaluate_strategic_value(stones, board_state)
        
        # 评估战术必要性
        tactical_necessity = self._evaluate_tactical_necessity(stones, board_state, context)
        
        # 评估风险系数
        risk_factor = self._evaluate_risk_factor(stones, board_state)
        
        # 确定重要性等级
        importance_level = self._determine_importance_level(
            strategic_value, tactical_necessity, risk_factor
        )
        
        # 生成应对建议
        recommendations = self._generate_recommendations(importance_level, stones)
        
        # 生成解释
        explanation = self._generate_explanation(
            importance_level, strategic_value, tactical_necessity, risk_factor
        )
        
        return ImportanceAnalysisResult(
            importance_level=importance_level,
            strategic_value=strategic_value,
            tactical_necessity=tactical_necessity,
            risk_factor=risk_factor,
            recommendations=recommendations,
            explanation=explanation
        )
    
    def _evaluate_strategic_value(self, stones: List[Tuple[int, int]], board_state) -> float:
        """评估战略价值"""
        # 简化的战略价值评估
        return 7.2  # 模拟值
    
    def _evaluate_tactical_necessity(self, stones: List[Tuple[int, int]], board_state, context) -> float:
        """评估战术必要性"""
        # 简化的战术必要性评估
        return 6.8  # 模拟值
    
    def _evaluate_risk_factor(self, stones: List[Tuple[int, int]], board_state) -> float:
        """评估风险系数"""
        # 简化的风险评估
        return 0.3  # 模拟值（0-1之间）
    
    def _determine_importance_level(
        self, 
        strategic_value: float, 
        tactical_necessity: float, 
        risk_factor: float
    ) -> ImportanceLevel:
        """确定重要性等级"""
        avg_value = (strategic_value + tactical_necessity) / 2
        if avg_value >= 8 and risk_factor <= 0.2:
            return ImportanceLevel.CRITICAL
        elif avg_value >= 6 and risk_factor <= 0.4:
            return ImportanceLevel.HIGH
        elif avg_value >= 4:
            return ImportanceLevel.MEDIUM
        else:
            return ImportanceLevel.LOW
    
    def _generate_recommendations(
        self, 
        importance_level: ImportanceLevel, 
        stones: List[Tuple[int, int]]
    ) -> List[str]:
        """生成应对建议"""
        if importance_level == ImportanceLevel.CRITICAL:
            return ["必须立即处理，不可弃掉", "需要重点关注和保护"]
        elif importance_level == ImportanceLevel.HIGH:
            return ["需要及时处理", "考虑适当的保护措施"]
        elif importance_level == ImportanceLevel.MEDIUM:
            return ["可以根据局势决定取舍", "灵活应对"]
        else:
            return ["可以考虑弃掉以换取其他利益", "不必过分在意"]
    
    def _generate_explanation(
        self, 
        importance_level: ImportanceLevel, 
        strategic_value: float, 
        tactical_necessity: float, 
        risk_factor: float
    ) -> str:
        """生成解释文本"""
        return f"该棋子组重要性为{importance_level.value}，战略价值{strategic_value:.1f}，战术必要性{tactical_necessity:.1f}，风险系数{risk_factor:.2f}。"
