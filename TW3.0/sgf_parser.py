"""
SGF棋谱解析器模块
用于解析和加载SGF格式的围棋棋谱
"""

import re
from typing import List, Dict, Tuple, Optional


class SGFParser:
    """
    SGF棋谱解析器
    用于解析SGF格式的围棋棋谱文件
    """
    
    def __init__(self):
        self.properties = {}
        self.moves = []
        self.size = 19  # 默认棋盘大小
    
    def parse_sgf(self, sgf_content: str) -> Dict:
        """
        解析SGF内容
        :param sgf_content: SGF格式的字符串内容
        :return: 包含棋谱信息的字典
        """
        # 移除注释和空白字符
        sgf_content = re.sub(r';(?=\s*[A-Z][A-Z])', ';\n', sgf_content)
        sgf_content = sgf_content.replace('\n', '').replace('\r', '').strip()
        
        # 解析头部信息
        header_info = self._parse_header(sgf_content)
        
        # 解析棋步
        moves = self._parse_moves(sgf_content)
        
        return {
            'header': header_info,
            'moves': moves,
            'size': self.size
        }
    
    def _parse_header(self, sgf_content: str) -> Dict:
        """
        解析SGF头部信息
        """
        header = {}
        
        # 查找基本信息
        patterns = {
            'GM': r'GM\[([^\]]+)\]',  # Game Type
            'FF': r'FF\[([^\]]+)\]',  # File Format
            'CA': r'CA\[([^\]]+)\]',  # Charset
            'SZ': r'SZ\[([^\]]+)\]',  # Size
            'PB': r'PB\[([^\]]+)\]',  # Player Black
            'PW': r'PW\[([^\]]+)\]',  # Player White
            'WR': r'WR\[([^\]]+)\]',  # White Rank
            'BR': r'BR\[([^\]]+)\]',  # Black Rank
            'DT': r'DT\[([^\]]+)\]',  # Date
            'KM': r'KM\[([^\]]+)\]',  # Komi
            'HA': r'HA\[([^\]]+)\]',  # Handicap
            'RE': r'RE\[([^\]]+)\]'   # Result
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, sgf_content)
            if match:
                header[key] = match.group(1)
                if key == 'SZ':
                    try:
                        self.size = int(header[key])
                    except ValueError:
                        self.size = 19
        
        return header
    
    def _parse_moves(self, sgf_content: str) -> List[Tuple[str, str, int]]:
        """
        解析棋步序列
        :return: [(move_number, color, coordinates), ...]
        """
        moves = []
        
        # 查找所有棋步 (B=Black, W=White)
        move_pattern = r'(B|W)\[([a-z]{2}|[])'
        matches = re.findall(move_pattern, sgf_content)
        
        move_num = 1
        for color, coord in matches:
            if coord == ']' or coord == 'tt':  # 虚手或空手
                moves.append((move_num, color, None))
            elif len(coord) == 2:
                # 转换坐标 a-z to 0-25
                col = ord(coord[0]) - ord('a')
                row = ord(coord[1]) - ord('a')
                moves.append((move_num, color, (row, col)))
            move_num += 1
        
        return moves
    
    def load_from_file(self, filepath: str) -> Dict:
        """
        从文件加载SGF内容
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_sgf(content)


def analyze_sgf_for_tw3(sgf_data: Dict) -> List[Dict]:
    """
    为TW3.0分析SGF棋谱
    :param sgf_data: 解析后的SGF数据
    :return: 分析结果列表
    """
    analyses = []
    
    # 对每个位置进行分析
    for move_num, color, coords in sgf_data['moves']:
        if coords is None:  # 虚手
            analysis = {
                'move_number': move_num,
                'color': color,
                'coordinates': None,
                'commentary': f"第{move_num}手: {color}方虚手",
                'win_rate': None,
                'intention': "形势判断或策略调整"
            }
        else:
            row, col = coords
            # 简单的位置描述
            col_label = 'ABCDEFGHJKLMNOPQRST'[col]  # 跳过'I'
            row_label = sgf_data['size'] - row
            
            analysis = {
                'move_number': move_num,
                'color': color,
                'coordinates': (row, col),
                'commentary': f"第{move_num}手: {color}方下在{col_label}{row_label}",
                'win_rate': 50.0 + (move_num % 20) - 10,  # 模拟胜率变化
                'intention': analyze_move_intention(color, (row, col), move_num)
            }
        
        analyses.append(analysis)
    
    return analyses


def analyze_move_intention(color: str, coords: Tuple[int, int], move_num: int) -> str:
    """
    分析棋手意图
    """
    if move_num <= 6:
        return "布局阶段：占角守角，构建阵势"
    elif move_num <= 30:
        return "布局向中盘过渡：占据大场，完善阵势"
    elif move_num <= 100:
        return "中盘作战：攻防转换，争夺要点"
    else:
        return "官子阶段：精确计算，争夺细节"


def main():
    """
    主函数：演示SGF解析功能
    """
    print("TW3.0 SGF棋谱解析器")
    print("此模块用于解析和分析SGF格式的围棋棋谱")
    
    # 示例使用方法
    print("\n使用方法:")
    print("1. 将SGF文件放在与本程序相同的目录")
    print("2. 使用 SGFParser().load_from_file('your_game.sgf') 加载棋谱")
    print("3. 调用 analyze_sgf_for_tw3() 进行分析")


if __name__ == "__main__":
    main()