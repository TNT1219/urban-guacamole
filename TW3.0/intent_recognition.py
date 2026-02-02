"""
意图识别模块 - TW3.0解说能力增强
用于判断每步棋的真实意图
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np


class IntentType(Enum):
    """意图类型枚举"""
    LAYOUT = "布局意图"           # 布局阶段的落子意图
    MIDDLE_GAME = "中盘意图"      # 中盘战斗意图
    END_GAME = "官子意图"         # 官子阶段意图
    ATTACK = "进攻意图"          # 主动攻击意图
    DEFENSE = "防守意图"         # 防守意图
    BALANCE = "平衡意图"         # 平衡局势意图
    INVESTMENT = "投资意图"       # 为将来做准备的意图
    TACTICAL = "战术意图"        # 局部战术意图
    STRATEGIC = "战略意图"       # 全局战略意图
    RESPONSE = "应对手段"        # 对对方意图的回应


@dataclass
class IntentAnalysisResult:
    """意图分析结果"""
    intent_types: List[IntentType]
    confidence: float
    explanation: str
    phase_specificity: str  # 布局/中盘/官子特异性
    tactical_elements: List[str]
    strategic_elements: List[str]


# 优化后的意图识别引擎
class IntentRecognitionEngine:
    """意图识别引擎"""
    
    def __init__(self):
        self.name = "TW3.0意图识别引擎"
        self.version = "1.0"
        
    def analyze_move_intent(
        self, 
        board_state, 
        move, 
        move_number: int,
        surrounding_stones: List[Tuple[int, int]],
        opponent_threats: List[Tuple[int, int]],
        territory_influence: Dict
    ) -> IntentAnalysisResult:
        """
        分析单步棋的意图
        """
        intents = []
        
        # 根据棋局阶段判断意图
        game_phase = self._determine_game_phase(move_number)
        
        # 分析落子位置特征
        position_features = self._analyze_position_features(move, board_state)
        
        # 分析周围环境
        environmental_factors = self._analyze_environmental_factors(
            move, surrounding_stones, opponent_threats, territory_influence
        )
        
        # 识别意图类型
        intents = self._identify_intents(
            game_phase, position_features, environmental_factors
        )
        
        # 计算置信度
        confidence = self._calculate_confidence(intents, environmental_factors)
        
        # 生成解释
        explanation = self._generate_explanation(
            intents, game_phase, position_features, environmental_factors
        )
        
        return IntentAnalysisResult(
            intent_types=intents,
            confidence=confidence,
            explanation=explanation,
            phase_specificity=game_phase,
            tactical_elements=self._extract_tactical_elements(environmental_factors),
            strategic_elements=self._extract_strategic_elements(environmental_factors)
        )
    
    def _determine_game_phase(self, move_number: int) -> str:
        """确定棋局阶段"""
        if move_number <= 30:
            return "布局阶段"
        elif move_number <= 100:
            return "中盘阶段"
        else:
            return "官子阶段"
    
    def _analyze_position_features(self, move: Tuple[int, int], board_state) -> Dict:
        """分析落子位置特征"""
        row, col = move
        features = {
            "靠近边线": abs(row - 9) >= 6 or abs(col - 9) >= 6,
            "靠近星位": self._is_near_star_point(row, col),
            "中央区域": 5 <= row <= 13 and 5 <= col <= 13,
            "角部区域": (row <= 5 and col <= 5) or (row <= 5 and col >= 13) or 
                      (row >= 13 and col <= 5) or (row >= 13 and col >= 13),
            "边部区域": not ((5 <= row <= 13 and 5 <= col <= 13) or 
                           (row <= 5 and col <= 5) or (row <= 5 and col >= 13) or 
                           (row >= 13 and col <= 5) or (row >= 13 and col >= 13))
        }
        return features
    
    def _is_near_star_point(self, row: int, col: int) -> bool:
        """判断是否靠近星位"""
        star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), 
                       (15, 3), (15, 9), (15, 15)]
        for sr, sc in star_points:
            if abs(row - sr) <= 1 and abs(col - sc) <= 1:
                return True
        return False
    
    def _analyze_environmental_factors(
        self, 
        move: Tuple[int, int], 
        surrounding_stones: List[Tuple[int, int]], 
        opponent_threats: List[Tuple[int, int]], 
        territory_influence: Dict
    ) -> Dict:
        """分析环境因素"""
        factors = {
            "附近友方棋子数量": len([stone for stone in surrounding_stones if stone[2] == 'own']),
            "附近敌方棋子数量": len([stone for stone in surrounding_stones if stone[2] == 'opponent']),
            "附近敌方威胁数量": len(opponent_threats),
            "附近潜在眼位": self._count_potential_liberties(move, surrounding_stones),
            "影响势力范围": territory_influence.get('impact', 0),
            "是否回应威胁": len(opponent_threats) > 0,
            "是否发起攻击": self._would_attack_opponent(move, surrounding_stones)
        }
        return factors
    
    def _count_potential_liberties(self, move: Tuple[int, int], surrounding_stones: List[Tuple[int, int]]) -> int:
        """计算潜在气数"""
        # 简化的气数计算逻辑
        liberties = 0
        r, c = move
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 19 and 0 <= nc < 19:
                liberties += 1  # 简化处理，实际需要检查是否有空交叉点
        return liberties
    
    def _would_attack_opponent(self, move: Tuple[int, int], surrounding_stones: List[Tuple[int, int]]) -> bool:
        """判断是否攻击对方"""
        opponent_stones = [stone for stone in surrounding_stones if stone[2] == 'opponent']
        # 简化判断逻辑
        return len(opponent_stones) > 0
    
    def _identify_intents(
        self, 
        game_phase: str, 
        position_features: Dict, 
        environmental_factors: Dict
    ) -> List[IntentType]:
        """识别意图类型"""
        intents = []
        
        # 根据棋局阶段识别意图
        if game_phase == "布局阶段":
            intents.append(IntentType.LAYOUT)
            if position_features["靠近星位"]:
                intents.append(IntentType.STRATEGIC)
        elif game_phase == "中盘阶段":
            intents.append(IntentType.MIDDLE_GAME)
            if environmental_factors["附近敌方威胁数量"] > 0:
                intents.append(IntentType.DEFENSE)
            elif environmental_factors["附近友方棋子数量"] > environmental_factors["附近敌方棋子数量"]:
                intents.append(IntentType.ATTACK)
        elif game_phase == "官子阶段":
            intents.append(IntentType.END_GAME)
        
        # 根据环境因素识别意图
        if environmental_factors["是否回应威胁"]:
            intents.append(IntentType.RESPONSE)
        if environmental_factors["附近敌方威胁数量"] > environmental_factors["附近友方棋子数量"]:
            intents.append(IntentType.DEFENSE)
        elif environmental_factors["附近友方棋子数量"] > environmental_factors["附近敌方威胁数量"]:
            intents.append(IntentType.ATTACK)
        
        # 如果没有明确意图，添加平衡意图
        if not intents:
            intents.append(IntentType.BALANCE)
            
        # 去除重复意图
        intents = list(set(intents))
        
        return intents
    
    def _calculate_confidence(self, intents: List[IntentType], environmental_factors: Dict) -> float:
        """计算置信度"""
        base_confidence = 0.6  # 基础置信度
        
        # 根据环境因素调整置信度
        factor_count = sum([
            environmental_factors.get("附近友方棋子数量", 0) > 0,
            environmental_factors.get("附近敌方棋子数量", 0) > 0,
            environmental_factors.get("附近敌方威胁数量", 0) > 0,
            environmental_factors.get("是否回应威胁", False)
        ])
        
        confidence = base_confidence + (factor_count * 0.1)
        return min(confidence, 1.0)  # 最大置信度为1.0
    
    def _generate_explanation(
        self, 
        intents: List[IntentType], 
        game_phase: str, 
        position_features: Dict, 
        environmental_factors: Dict
    ) -> str:
        """生成解释文本"""
        intent_names = [intent.value for intent in intents]
        
        explanation = f"该手棋具有{game_phase}特征，主要意图包括：{', '.join(intent_names)}。"
        
        if environmental_factors.get("是否回应威胁"):
            explanation += "此手棋是对对方威胁的回应。"
        if environmental_factors.get("附近友方棋子数量", 0) > environmental_factors.get("附近敌方棋子数量", 0):
            explanation += "该位置有利于己方势力发展。"
        elif environmental_factors.get("附近敌方棋子数量", 0) > environmental_factors.get("附近友方棋子数量", 0):
            explanation += "该位置主要针对对方棋子进行应对。"
        
        return explanation
    
    def _extract_tactical_elements(self, environmental_factors: Dict) -> List[str]:
        """提取战术元素"""
        elements = []
        if environmental_factors.get("附近敌方威胁数量", 0) > 0:
            elements.append("应对威胁")
        if environmental_factors.get("附近友方棋子数量", 0) > 0:
            elements.append("配合己方棋子")
        return elements
    
    def _extract_strategic_elements(self, environmental_factors: Dict) -> List[str]:
        """提取战略元素"""
        elements = []
        if environmental_factors.get("影响势力范围", 0) > 0:
            elements.append("扩大势力范围")
        if environmental_factors.get("附近敌方威胁数量", 0) > 0:
            elements.append("稳固防守")
        return elements


# 测试代码
if __name__ == "__main__":
    engine = IntentRecognitionEngine()
    print(f"{engine.name} v{engine.version} 初始化成功")