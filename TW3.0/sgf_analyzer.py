"""
TW3.0 SGF棋谱分析器
用于加载和分析SGF格式的围棋棋谱
"""

import sys
import os
from typing import Dict, List, Tuple
from sgf_parser import SGFParser, analyze_sgf_for_tw3


class TW3SGFAnalyzer:
    """
    TW3.0专用的SGF棋谱分析器
    """
    
    def __init__(self):
        self.parser = SGFParser()
    
    def load_and_analyze_sgf(self, filepath: str) -> dict:
        """
        加载并分析SGF棋谱
        :param filepath: SGF文件路径
        :return: 分析结果
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        # 解析SGF文件
        sgf_data = self.parser.load_from_file(filepath)
        
        # 进行分析
        analyses = analyze_sgf_for_tw3(sgf_data)
        
        # 生成完整分析报告
        report = {
            'game_info': sgf_data['header'],
            'board_size': sgf_data['size'],
            'total_moves': len(analyses),
            'analyses': analyses,
            'summary': self._generate_summary(sgf_data, analyses)
        }
        
        return report
    
    def _generate_summary(self, sgf_data: dict, analyses: List[dict]) -> dict:
        """
        生成棋局总结
        """
        # 简单统计
        black_moves = len([a for a in analyses if a['color'] == 'B'])
        white_moves = len([a for a in analyses if a['color'] == 'W'])
        
        # 结果分析（如果有的话）
        result = sgf_data['header'].get('RE', 'Unknown')
        
        # 关键时刻识别
        key_moments = self._identify_key_moments(analyses)
        
        return {
            'black_moves': black_moves,
            'white_moves': white_moves,
            'result': result,
            'key_moments': key_moments,
            'overall_commentary': self._generate_overall_commentary(sgf_data, analyses)
        }
    
    def _identify_key_moments(self, analyses: List[dict]) -> List[dict]:
        """
        识别关键时刻
        """
        key_moments = []
        
        # 这里可以根据胜率变化、复杂战斗等识别关键时刻
        # 简单示例：每隔20手标记一次
        for i in range(0, len(analyses), 20):
            if i < len(analyses):
                key_moments.append({
                    'move_number': analyses[i]['move_number'],
                    'comment': f"第{analyses[i]['move_number']}手左右的关键局面"
                })
        
        return key_moments
    
    def _generate_overall_commentary(self, sgf_data: dict, analyses: List[dict]) -> str:
        """
        生成总体评述
        """
        header = sgf_data['header']
        black_player = header.get('PB', 'Unknown')
        white_player = header.get('PW', 'Unknown')
        result = header.get('RE', 'Unknown')
        
        commentary = f"对局评述:\n"
        commentary += f"- 对手: {black_player} vs {white_player}\n"
        commentary += f"- 结果: {result}\n"
        commentary += f"- 总手数: {len(analyses)}手\n"
        commentary += f"- 棋盘大小: {sgf_data['size']}路\n\n"
        
        # 分阶段评述
        if len(analyses) > 0:
            commentary += "阶段分析:\n"
            if len(analyses) > 30:
                commentary += "- 布局阶段: 前30手，双方各自布局，构建势力范围\n"
            if len(analyses) > 100:
                commentary += "- 中盘阶段: 30-100手，进入激烈战斗，攻防转换频繁\n"
            if len(analyses) > 150:
                commentary += "- 官子阶段: 100手以后，精确收官，决定胜负\n"
        
        return commentary
    
    def print_detailed_analysis(self, report: dict):
        """
        打印详细的分析结果
        """
        print("=" * 60)
        print("TW3.0 SGF棋谱分析报告")
        print("=" * 60)
        
        # 游戏信息
        print("\n【游戏信息】")
        for key, value in report['game_info'].items():
            print(f"{key}: {value}")
        
        print(f"\n棋盘大小: {report['board_size']}路")
        print(f"总手数: {report['total_moves']}手")
        
        # 总结
        print("\n【棋局总结】")
        summary = report['summary']
        print(summary['overall_commentary'])
        
        # 关键时刻
        print("\n【关键时刻】")
        for moment in summary['key_moments']:
            print(f"- {moment['comment']}")
        
        # 每10手显示一次详细分析
        print("\n【详细分析（每10手）】")
        for i in range(0, len(report['analyses']), 10):
            analysis = report['analyses'][i]
            coords = analysis['coordinates']
            if coords:
                col_label = 'ABCDEFGHJKLMNOPQRST'[coords[1]]  # 跳过'I'
                row_label = report['board_size'] - coords[0]
                print(f"第{analysis['move_number']}手: {analysis['color']}方在{col_label}{row_label}，意图: {analysis['intention']}")
            else:
                print(f"第{analysis['move_number']}手: {analysis['color']}方虚手，意图: {analysis['intention']}")
        
        print("\n" + "=" * 60)
        print("分析完成！")


def main():
    """
    主函数：演示如何使用SGF分析器
    """
    if len(sys.argv) < 2:
        print("使用方法: python sgf_analyzer.py <sgf_file_path>")
        print("例如: python sgf_analyzer.py example.sgf")
        return
    
    analyzer = TW3SGFAnalyzer()
    
    try:
        # 分析SGF文件
        filepath = sys.argv[1]
        report = analyzer.load_and_analyze_sgf(filepath)
        
        # 打印详细分析
        analyzer.print_detailed_analysis(report)
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"分析过程中出现错误: {e}")


if __name__ == "__main__":
    main()