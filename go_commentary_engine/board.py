"""
围棋棋盘模块
实现标准围棋棋盘的基本功能
"""


class GoBoard:
    """
    围棋棋盘类
    """
    
    def __init__(self, size=19):
        """
        初始化棋盘
        :param size: 棋盘大小，默认19路
        """
        if size not in [9, 13, 19]:
            raise ValueError("棋盘大小必须是9、13或19")
        
        self.size = size
        self.board = [['.' for _ in range(size)] for _ in range(size)]
    
    def place_stone(self, row, col, color):
        """
        在指定位置放置棋子
        :param row: 行索引
        :param col: 列索引
        :param color: 棋子颜色 ('B'为黑子, 'W'为白子)
        :return: 是否成功放置
        """
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        if self.board[row][col] != '.':
            return False  # 位置已被占用
        
        if color not in ['B', 'W']:
            return False  # 无效的颜色
        
        self.board[row][col] = color
        return True
    
    def get_stone(self, row, col):
        """
        获取指定位置的棋子
        :param row: 行索引
        :param col: 列索引
        :return: 棋子颜色 ('B', 'W' 或 '.') 
        """
        if not (0 <= row < self.size and 0 <= col < self.size):
            return None
        
        return self.board[row][col]
    
    def clear_board(self):
        """
        清空棋盘
        """
        self.board = [['.' for _ in range(self.size)] for _ in range(self.size)]
    
    def copy_board(self):
        """
        复制棋盘
        """
        new_board = GoBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        return new_board
    
    def get_board_state(self):
        """
        获取棋盘状态
        """
        return [row[:] for row in self.board]
    
    def display(self):
        """
        显示棋盘（文本形式，主要用于调试）
        """
        print("  ", end="")
        for j in range(self.size):
            print(f"{j:2}", end=" ")
        print()
        
        for i in range(self.size):
            print(f"{i:2}", end=" ")
            for j in range(self.size):
                print(f"{self.board[i][j]:2}", end=" ")
            print()


def main():
    """
    主函数：演示棋盘功能
    """
    print("围棋棋盘模块演示")
    board = GoBoard(9)  # 使用9路棋盘进行演示
    
    # 放置几个棋子
    board.place_stone(4, 4, 'B')
    board.place_stone(4, 5, 'W')
    board.place_stone(5, 4, 'B')
    
    print("当前棋盘状态:")
    board.display()


if __name__ == "__main__":
    main()