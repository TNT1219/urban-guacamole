"""
TW2.0 交互式围棋界面模块
实现用户与AI引擎的实时交互功能
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from go_commentary_engine.board import GoBoard
from go_commentary_engine.self_improvement import SelfImprovementEngine


class InteractiveGoInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TW2.0 交互式围棋界面")
        self.board = GoBoard(19)  # 19x19标准棋盘
        self.commentary_engine = SelfImprovementEngine()
        self.current_player = 'B'  # B=Black, W=White
        self.game_history = []
        self.analysis_cache = {}
        
        # 初始化界面
        self.setup_ui()
        
        # 启动后台分析线程
        self.analysis_thread = None
        self.should_analyze = True
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：棋盘
        board_frame = ttk.LabelFrame(main_frame, text="棋盘", padding=5)
        board_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 创建画布用于绘制棋盘
        self.canvas = tk.Canvas(
            board_frame, 
            width=400, 
            height=400, 
            bg='#DEB887'  # 棋盘颜色
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # 右侧：信息面板
        info_frame = ttk.LabelFrame(main_frame, text="分析信息", padding=5)
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 当前胜率显示
        ttk.Label(info_frame, text="当前胜率:").grid(row=0, column=0, sticky=tk.W)
        self.win_rate_var = tk.StringVar(value="黑棋 50.0% / 白棋 50.0%")
        ttk.Label(info_frame, textvariable=self.win_rate_var).grid(row=0, column=1, sticky=tk.W)
        
        # 当前意图分析
        ttk.Label(info_frame, text="意图分析:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.intention_frame = ttk.LabelFrame(info_frame, padding=5)
        self.intention_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.intention_var = tk.StringVar(value="点击棋盘下子以开始分析")
        ttk.Label(self.intention_frame, textvariable=self.intention_var, wraplength=300).pack(anchor=tk.W)
        
        # 后续变化显示
        ttk.Label(info_frame, text="后续变化:").grid(row=3, column=0, sticky=tk.W)
        self.variations_frame = ttk.LabelFrame(info_frame, padding=5)
        self.variations_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.variations_var = tk.StringVar(value="等待分析...")
        ttk.Label(self.variations_frame, textvariable=self.variations_var, wraplength=300).pack(anchor=tk.W)
        
        # 死活分析
        ttk.Label(info_frame, text="死活分析:").grid(row=5, column=0, sticky=tk.W)
        self.life_death_var = tk.StringVar(value="等待分析...")
        ttk.Label(info_frame, textvariable=self.life_death_var, wraplength=300).grid(row=5, column=1, sticky=tk.W)
        
        # 厚薄分析
        ttk.Label(info_frame, text="厚薄分析:").grid(row=6, column=0, sticky=tk.W)
        self.thickness_var = tk.StringVar(value="等待分析...")
        ttk.Label(info_frame, textvariable=self.thickness_var, wraplength=300).grid(row=6, column=1, sticky=tk.W)
        
        # 轻重分析
        ttk.Label(info_frame, text="轻重分析:").grid(row=7, column=0, sticky=tk.W)
        self.weight_var = tk.StringVar(value="等待分析...")
        ttk.Label(info_frame, textvariable=self.weight_var, wraplength=300).grid(row=7, column=1, sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.Frame(info_frame)
        control_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="悔棋", command=self.undo_move).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="重新分析", command=self.reanalyze_position).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="保存棋谱", command=self.save_sgf).pack(side=tk.LEFT)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)
        board_frame.rowconfigure(0, weight=1)
        
        info_frame.columnconfigure(1, weight=1)
        info_frame.rowconfigure(4, weight=1)
        
    def draw_board(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        size = self.board.size
        cell_size = min(400 // size, 400 // size)
        offset = (400 - (size - 1) * cell_size) // 2
        
        # 绘制网格线
        for i in range(size):
            # 垂直线
            x = offset + i * cell_size
            self.canvas.create_line(x, offset, x, offset + (size - 1) * cell_size)
            # 水平线
            y = offset + i * cell_size
            self.canvas.create_line(offset, y, offset + (size - 1) * cell_size, y)
        
        # 绘制星位点
        star_points = [3, 9, 15] if size == 19 else [2, int(size/2), size-3]
        for i in star_points:
            for j in star_points:
                x = offset + i * cell_size
                y = offset + j * cell_size
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='black')
        
        # 绘制棋子
        for i in range(size):
            for j in range(size):
                stone = self.board.get_stone(i, j)
                if stone != '.':
                    x = offset + j * cell_size
                    y = offset + i * cell_size
                    color = 'black' if stone == 'B' else 'white'
                    outline = 'black' if stone == 'B' else 'black'  # 白子用黑色轮廓
                    self.canvas.create_oval(
                        x-12, y-12, x+12, y+12, 
                        fill=color, outline=outline, width=1
                    )
    
    def on_board_click(self, event):
        """处理棋盘点击事件"""
        size = self.board.size
        cell_size = min(400 // size, 400 // size)
        offset = (400 - (size - 1) * cell_size) // 2
        
        # 计算点击位置对应的棋盘坐标
        col = round((event.x - offset) / cell_size)
        row = round((event.y - offset) / cell_size)
        
        # 检查坐标是否在棋盘范围内
        if 0 <= row < size and 0 <= col < size:
            # 尝试放置棋子
            if self.board.place_stone(row, col, self.current_player):
                # 记录这次移动
                move_notation = self.coordinate_to_gtp(row, col)
                self.game_history.append((move_notation, self.current_player))
                
                # 切换玩家
                self.current_player = 'W' if self.current_player == 'B' else 'B'
                
                # 更新界面
                self.draw_board()
                self.update_analysis()
                
                # 启动后台分析
                self.start_background_analysis()
    
    def coordinate_to_gtp(self, row, col):
        """将坐标转换为GTP格式"""
        # GTP坐标：列用字母表示（跳过I），行用数字表示
        col_str = chr(ord('A') + col)
        if col >= 8:  # 跳过字母'I'
            col_str = chr(ord('A') + col + 1)
        return f"{col_str}{self.board.size - row}"
    
    def update_analysis(self):
        """更新分析信息"""
        # 这里会调用AI引擎进行分析
        # 模拟分析结果
        current_analysis = self.analyze_current_position()
        
        # 更新胜率显示
        black_win_rate = 45.0 + (len(self.game_history) % 10) * 1.2
        white_win_rate = 100.0 - black_win_rate
        self.win_rate_var.set(f"黑棋 {black_win_rate:.1f}% / 白棋 {white_win_rate:.1f}%")
        
        # 更新意图分析
        if self.game_history:
            last_move = self.game_history[-1]
            self.intention_var.set(f"上一手: {last_move[1]}在{last_move[0]}落子，意图分析: 控制中央要点，加强势力")
        else:
            self.intention_var.set("点击棋盘下子以开始分析")
        
        # 更新后续变化
        variations = "主要变化: Q16, D16, Q4, D4, P3, R3, P17, R17"
        self.variations_var.set(variations)
        
        # 更新死活分析
        self.life_death_var.set("当前局面无明显死活问题，各块棋均较为安定")
        
        # 更新厚薄分析
        self.thickness_var.set("黑棋右侧较厚，白棋左上角需注意薄弱环节")
        
        # 更新轻重分析
        self.weight_var.set("白棋第30手为重棋，需要处理，黑棋可考虑先手攻击")
    
    def analyze_current_position(self):
        """分析当前位置"""
        # 这里会调用真正的AI分析引擎
        # 返回分析结果
        analysis_result = {
            'win_rate': 52.3,
            'variations': ['Q16', 'D16', 'Q4'],
            'intention': '控制中央，加强势力',
            'life_death': '各块棋均安定',
            'thickness': '右侧较厚',
            'weight': '第30手为重棋'
        }
        return analysis_result
    
    def start_background_analysis(self):
        """启动后台分析"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.should_analyze = False  # 停止当前分析
        
        self.should_analyze = True
        self.analysis_thread = threading.Thread(target=self.background_analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def background_analysis_worker(self):
        """后台分析工作线程"""
        # 模拟后台分析过程
        time.sleep(1)  # 模拟分析时间
        
        if not self.should_analyze:
            return
        
        # 实际分析逻辑
        # 这里会调用Katago或其他引擎进行深度分析
        print(f"后台分析完成: {len(self.game_history)}手棋")
    
    def undo_move(self):
        """悔棋功能"""
        if self.game_history:
            self.game_history.pop()
            self.current_player = 'W' if self.current_player == 'B' else 'B'
            # 重新设置棋盘状态（简化处理）
            temp_history = self.game_history[:]
            self.board = GoBoard(19)
            for move, player in temp_history:
                row, col = self.gtp_to_coordinate(move)
                self.board.place_stone(row, col, player)
            
            self.draw_board()
            self.update_analysis()
    
    def gtp_to_coordinate(self, gtp_coord):
        """将GTP坐标转换为数组坐标"""
        if len(gtp_coord) < 2:
            return -1, -1
        
        col_char = gtp_coord[0].upper()
        row_part = gtp_coord[1:]
        
        try:
            row = self.board.size - int(row_part)
            col = ord(col_char) - ord('A')
            if col >= 8:  # 跳过了字母'I'
                col -= 1
            return row, col
        except ValueError:
            return -1, -1
    
    def reanalyze_position(self):
        """重新分析当前局面"""
        self.update_analysis()
        self.start_background_analysis()
    
    def save_sgf(self):
        """保存SGF棋谱"""
        # 简化版本：仅输出到控制台
        print("SGF棋谱保存功能待实现")
        # 实际实现中会将游戏历史保存为SGF格式
    
    def run(self):
        """运行界面"""
        self.draw_board()
        self.root.mainloop()


def main():
    """主函数"""
    print("启动TW2.0交互式围棋界面...")
    interface = InteractiveGoInterface()
    interface.run()


if __name__ == "__main__":
    main()