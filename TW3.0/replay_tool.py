"""
TW3.0复盘工具
专业的复盘分析功能
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class ReviewPoint:
    """复盘要点"""
    move_number: int
    position: str  # 棋盘位置，如 "Q16"
    comment: str   # 评论
    severity: str  # 严重程度: "critical", "major", "minor"
    alternative_moves: List[str]  # 替代着法
    score_impact: float  # 对胜率的影响
    variation: List[str]  # 变化图


@dataclass
class CriticalPoint:
    """关键点"""
    move_number: int
    position: str
    point_type: str  # "turning_point", "missed_opportunity", "blunder", "good_move"
    description: str
    impact: str      # "positive", "negative", "neutral"


@dataclass
class ReviewReport:
    """复盘报告"""
    game_id: str
    player_color: str
    opponent_strength: str
    result: str      # "win", "loss", "draw"
    total_moves: int
    review_points: List[ReviewPoint]
    critical_points: List[CriticalPoint]
    overall_assessment: str
    improvement_suggestions: List[str]
    generated_at: str


class ReviewAnalyzer:
    """复盘分析算法"""
    
    def __init__(self, db_path: str = "/root/clawd/TW3.0/user_data.db"):
        self.db_path = db_path
    
    def analyze_game_for_review(self, game_data: Dict) -> ReviewReport:
        """
        分析棋局以生成复盘报告
        game_data 应包含: moves, winner, players, etc.
        """
        moves = game_data.get('moves', [])
        player_color = game_data.get('player_color', 'B')
        opponent_color = 'W' if player_color == 'B' else 'B'
        winner = game_data.get('winner', 'unknown')
        
        # 识别关键点
        critical_points = self._identify_critical_points(moves, player_color)
        
        # 识别需要复盘的点
        review_points = self._identify_review_points(moves, player_color)
        
        # 生成总体评价
        overall_assessment = self._generate_overall_assessment(
            review_points, critical_points, winner, player_color
        )
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(
            review_points, critical_points
        )
        
        report = ReviewReport(
            game_id=game_data.get('game_id', 'unknown'),
            player_color=player_color,
            opponent_strength=game_data.get('opponent_strength', 'unknown'),
            result=self._determine_result(winner, player_color),
            total_moves=len(moves),
            review_points=review_points,
            critical_points=critical_points,
            overall_assessment=overall_assessment,
            improvement_suggestions=improvement_suggestions,
            generated_at=datetime.now().isoformat()
        )
        
        return report
    
    def _identify_critical_points(self, moves: List[str], player_color: str) -> List[CriticalPoint]:
        """识别关键点"""
        critical_points = []
        
        # 这里应该集成AI分析结果，但现在使用模拟逻辑
        
        # 模拟识别一些关键点
        move_count = len(moves)
        
        # 开局关键点（前20手）
        if move_count > 20:
            # 假设第5手是开局关键点
            critical_points.append(CriticalPoint(
                move_number=5,
                position=moves[4] if len(moves) > 4 else "unknown",
                point_type="turning_point",
                description="开局战略选择的关键时刻",
                impact="neutral"
            ))
        
        # 中盘关键点（20-100手）
        if move_count > 50:
            # 假设第30手是中盘关键点
            critical_points.append(CriticalPoint(
                move_number=30,
                position=moves[29] if len(moves) > 29 else "unknown",
                point_type="turning_point",
                description="中盘战斗的转折点",
                impact="negative" if player_color == 'B' else "positive"
            ))
        
        # 官子关键点（100手之后）
        if move_count > 120:
            # 假设倒数第10手是官子关键点
            end_pos = max(0, move_count - 10)
            critical_points.append(CriticalPoint(
                move_number=end_pos + 1,
                position=moves[end_pos] if len(moves) > end_pos else "unknown",
                point_type="missed_opportunity",
                description="官子阶段的小失误",
                impact="negative"
            ))
        
        # 添加一些模拟的严重失误
        if move_count > 30:
            critical_points.append(CriticalPoint(
                move_number=25,
                position=moves[24] if len(moves) > 24 else "unknown",
                point_type="blunder",
                description="明显的坏手，损失较大",
                impact="negative"
            ))
        
        return critical_points
    
    def _identify_review_points(self, moves: List[str], player_color: str) -> List[ReviewPoint]:
        """识别需要复盘的点"""
        review_points = []
        
        # 模拟识别一些需要复盘的点
        # 通常会选择一些重要的、有争议的或者失误的着法
        
        # 每隔20手选择一个点进行复盘
        for i in range(min(100, len(moves))):  # 只看前100手
            if i % 20 == 0 and i > 0:  # 每20手一个复盘点
                move_pos = moves[i-1] if moves else "unknown"
                
                # 确定严重程度
                if i < 30:
                    severity = "minor"
                    comment = f"第{i}手的位置选择值得讨论，开局阶段的布局思路"
                elif i < 70:
                    severity = "major" 
                    comment = f"第{i}手涉及中盘战斗，需要仔细分析得失"
                else:
                    severity = "minor"
                    comment = f"第{i}手官子阶段，注重细节"
                
                review_point = ReviewPoint(
                    move_number=i,
                    position=move_pos,
                    comment=comment,
                    severity=severity,
                    alternative_moves=self._suggest_alternatives(move_pos, i),
                    score_impact=round((i % 10) * 0.5 - 2.5, 1),  # 模拟影响值
                    variation=[move_pos, "R16", "Q17"]  # 模拟变化图
                )
                review_points.append(review_point)
        
        # 添加一些特殊的失误点
        if len(moves) > 25:
            bad_move_pos = moves[24] if len(moves) > 24 else "unknown"
            review_points.append(ReviewPoint(
                move_number=25,
                position=bad_move_pos,
                comment="这手棋过于保守，错失良机",
                severity="critical",
                alternative_moves=["Q15", "R15", "P16"],
                score_impact=-3.2,
                variation=[bad_move_pos, "Q15", "R15", "P16"]
            ))
        
        return review_points
    
    def _suggest_alternatives(self, position: str, move_number: int) -> List[str]:
        """建议替代着法"""
        # 根据位置和手数生成建议
        alternatives = []
        
        # 基于位置生成临近点
        if len(position) >= 2:
            try:
                col_char = position[0]
                row_num = int(position[1:])
                
                # 生成邻近位置
                col_idx = ord(col_char) - ord('A')
                if col_idx >= 8:  # 跳过'I'
                    col_idx -= 1
                
                # 生成附近的几个点
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue  # 跳过原位置
                        
                        new_col_idx = col_idx + dc
                        new_row = row_num + dr
                        
                        if 0 <= new_col_idx < 19 and 1 <= new_row <= 19:
                            new_col = chr(ord('A') + new_col_idx)
                            if new_col_idx >= 8:  # 跳过'I'
                                new_col = chr(ord('A') + new_col_idx + 1)
                            
                            alt_pos = f"{new_col}{new_row}"
                            alternatives.append(alt_pos)
                        
            except ValueError:
                pass  # 如果解析失败，跳过
        
        # 如果没有生成足够的替代点，添加一些固定的建议
        if len(alternatives) < 3:
            alternatives.extend(["Q16", "D4", "D16", "Q4", "K10"])
        
        return alternatives[:5]  # 返回最多5个替代点
    
    def _generate_overall_assessment(self, review_points: List[ReviewPoint], 
                                   critical_points: List[CriticalPoint], 
                                   winner: str, player_color: str) -> str:
        """生成总体评价"""
        # 统计各类问题
        critical_issues = len([p for p in review_points if p.severity == "critical"])
        major_issues = len([p for p in review_points if p.severity == "major"])
        negative_points = len([p for p in critical_points if p.impact == "negative"])
        
        player_won = (winner == player_color)
        
        assessment_parts = []
        
        if player_won:
            assessment_parts.append("恭喜获胜！整体表现不错。")
        else:
            assessment_parts.append("虽然失利，但在某些方面也有亮点。")
        
        if critical_issues > 2:
            assessment_parts.append(f"需要注意的是，在复盘中发现了{critical_issues}个严重问题，这是导致败局的主要原因。")
        elif critical_issues > 0:
            assessment_parts.append(f"有几个关键失误需要注意，避免类似的严重错误。")
        
        if major_issues > 3:
            assessment_parts.append(f"中等程度的问题较多({major_issues}个)，需要在实战中提高决策质量。")
        elif major_issues > 0:
            assessment_parts.append(f"有一些地方可以改进，主要是{major_issues}个中等程度的问题。")
        
        if negative_points > 0:
            assessment_parts.append(f"棋局中有{negative_points}个关键转折点处理不当，值得深入研究。")
        
        return " ".join(assessment_parts)
    
    def _generate_improvement_suggestions(self, review_points: List[ReviewPoint], 
                                        critical_points: List[CriticalPoint]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 统计问题类型
        critical_count = len([p for p in review_points if p.severity == "critical"])
        major_count = len([p for p in review_points if p.severity == "major"])
        negative_count = len([p for p in critical_points if p.impact == "negative"])
        
        if critical_count > 0:
            suggestions.append("加强大局观训练，避免严重失误")
        
        if major_count > 2:
            suggestions.append("提高中盘战斗力，多做死活题和手筋题")
        
        if negative_count > 1:
            suggestions.append("学习如何在关键点做出正确决策，多研究高手对局")
        
        # 添加通用建议
        if not suggestions:
            suggestions.append("继续保持，多下棋积累经验")
        
        suggestions.extend([
            "复习本次对局的复盘要点",
            "针对发现的问题进行专项练习"
        ])
        
        return suggestions
    
    def _determine_result(self, winner: str, player_color: str) -> str:
        """确定结果"""
        if winner == player_color:
            return "win"
        elif winner == "unknown":
            return "draw"
        else:
            return "loss"


class ReplayTool:
    """复盘分析工具"""
    
    def __init__(self, db_path: str = "/root/clawd/TW3.0/user_data.db"):
        self.db_path = db_path
        self.analyzer = ReviewAnalyzer(db_path)
    
    def conduct_review(self, game_data: Dict) -> ReviewReport:
        """进行复盘"""
        return self.analyzer.analyze_game_for_review(game_data)
    
    def save_review_report(self, report: ReviewReport):
        """保存复盘报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将报告序列化为JSON
        report_json = json.dumps({
            'game_id': report.game_id,
            'player_color': report.player_color,
            'opponent_strength': report.opponent_strength,
            'result': report.result,
            'total_moves': report.total_moves,
            'review_points': [
                {
                    'move_number': rp.move_number,
                    'position': rp.position,
                    'comment': rp.comment,
                    'severity': rp.severity,
                    'alternative_moves': rp.alternative_moves,
                    'score_impact': rp.score_impact,
                    'variation': rp.variation
                } for rp in report.review_points
            ],
            'critical_points': [
                {
                    'move_number': cp.move_number,
                    'position': cp.position,
                    'point_type': cp.point_type,
                    'description': cp.description,
                    'impact': cp.impact
                } for cp in report.critical_points
            ],
            'overall_assessment': report.overall_assessment,
            'improvement_suggestions': report.improvement_suggestions,
            'generated_at': report.generated_at
        }, ensure_ascii=False)
        
        cursor.execute('''
            INSERT OR REPLACE INTO analysis_reports 
            (user_id, report_type, report_data, generated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            "default_user",  # 这里应该从game_data中获取实际用户ID
            "post_game_review",
            report_json,
            report.generated_at
        ))
        
        conn.commit()
        conn.close()
    
    def get_historical_reviews(self, user_id: str, limit: int = 10) -> List[ReviewReport]:
        """获取历史复盘记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT report_data FROM analysis_reports
            WHERE user_id = ? AND report_type = ?
            ORDER BY generated_at DESC
            LIMIT ?
        ''', (user_id, "post_game_review", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            try:
                data = json.loads(row[0])
                report = ReviewReport(
                    game_id=data['game_id'],
                    player_color=data['player_color'],
                    opponent_strength=data['opponent_strength'],
                    result=data['result'],
                    total_moves=data['total_moves'],
                    review_points=[
                        ReviewPoint(
                            move_number=rp['move_number'],
                            position=rp['position'],
                            comment=rp['comment'],
                            severity=rp['severity'],
                            alternative_moves=rp['alternative_moves'],
                            score_impact=rp['score_impact'],
                            variation=rp['variation']
                        ) for rp in data['review_points']
                    ],
                    critical_points=[
                        CriticalPoint(
                            move_number=cp['move_number'],
                            position=cp['position'],
                            point_type=cp['point_type'],
                            description=cp['description'],
                            impact=cp['impact']
                        ) for cp in data['critical_points']
                    ],
                    overall_assessment=data['overall_assessment'],
                    improvement_suggestions=data['improvement_suggestions'],
                    generated_at=data['generated_at']
                )
                reports.append(report)
            except json.JSONDecodeError:
                continue  # 跳过无效数据
        
        return reports


def main():
    """主函数：演示复盘工具"""
    print("启动TW3.0复盘工具")
    
    # 创建复盘工具
    replay_tool = ReplayTool()
    
    # 模拟一局棋的数据
    sample_game_data = {
        'game_id': 'game_001',
        'moves': ['D4', 'D16', 'Q4', 'Q16', 'D3', 'D17', 'C4', 'C16', 
                  'R3', 'P16', 'Q3', 'Q15', 'R4', 'P15', 'Q5', 'O16',
                  'P4', 'R15', 'Q14', 'P14', 'O14', 'P13', 'Q13', 'R13',
                  'R12', 'S13', 'S12', 'R11', 'S11', 'R10'],
        'player_color': 'B',
        'opponent_strength': 'intermediate',
        'winner': 'W',
        'date': datetime.now().isoformat()
    }
    
    print(f"\n正在分析棋局 {sample_game_data['game_id']}...")
    
    # 进行复盘
    review_report = replay_tool.conduct_review(sample_game_data)
    
    # 保存复盘报告
    replay_tool.save_review_report(review_report)
    
    print(f"复盘完成！共识别出 {len(review_report.review_points)} 个复盘点")
    print(f"和 {len(review_report.critical_points)} 个关键点")
    
    print(f"\n总体评价: {review_report.overall_assessment}")
    
    print(f"\n改进建议:")
    for i, suggestion in enumerate(review_report.improvement_suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print(f"\n关键点分析:")
    for i, point in enumerate(review_report.critical_points[:3], 1):  # 只显示前3个
        print(f"  {i}. 第{point.move_number}手 {point.position}: {point.description}")
    
    print(f"\n复盘工具演示完成")


if __name__ == "__main__":
    main()