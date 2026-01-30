"""
TW围棋解说引擎 - 统一整合系统
整合TW1.0（核心分析）和TW2.0（交互界面）的完整系统
"""

from go_commentary_engine.board import GoBoard
from go_commentary_engine.self_improvement import SelfImprovementEngine
from go_commentary_engine.interactive_interface import InteractiveGoInterface
import threading
import queue
import time
from typing import Dict, List, Tuple, Optional


class TWIntegratedSystem:
    """
    TW围棋解说引擎统一系统
    整合核心分析引擎(TW1.0)和交互界面(TW2.0)
    """
    
    def __init__(self):
        # TW1.0 核心分析引擎组件
        self.board = GoBoard(19)
        self.self_improvement_engine = SelfImprovementEngine()
        self.analysis_cache = {}
        
        # TW2.0 交互界面组件
        self.interface = None
        self.current_player = 'B'  # B=Black, W=White
        self.game_history = []
        
        # 通信队列
        self.analysis_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # 控制标志
        self.running = False
        self.analysis_thread = None
        
        # 初始化分析线程
        self._start_analysis_thread()
    
    def _start_analysis_thread(self):
        """启动分析线程"""
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self.analysis_thread.start()
    
    def _analysis_worker(self):
        """分析工作线程 - TW1.0核心功能"""
        while self.running:
            try:
                # 检查是否有新的分析请求
                if not self.analysis_queue.empty():
                    request = self.analysis_queue.get(timeout=0.1)
                    position_data = request['position_data']
                    analysis_type = request['type']
                    
                    # 使用TW1.0的分析能力
                    result = self._perform_analysis(position_data, analysis_type)
                    
                    # 将结果放入结果队列
                    self.result_queue.put({
                        'request_id': request['request_id'],
                        'result': result,
                        'timestamp': time.time()
                    })
                else:
                    time.sleep(0.1)  # 短暂休眠避免过度占用CPU
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"分析线程错误: {e}")
    
    def _perform_analysis(self, position_data: Dict, analysis_type: str):
        """
        执行具体分析 - TW1.0核心分析能力
        """
        result = {}
        
        if analysis_type == 'full_analysis':
            # 完整分析：胜率、意图、变化、死活、厚薄、轻重
            result['win_rate'] = self._calculate_win_rate(position_data)
            result['intention_analysis'] = self._analyze_intention(position_data)
            result['variations'] = self._calculate_variations(position_data)
            result['life_death'] = self._analyze_life_death(position_data)
            result['thickness'] = self._analyze_thickness(position_data)
            result['weight'] = self._analyze_weight(position_data)
            
        elif analysis_type == 'win_rate':
            result['win_rate'] = self._calculate_win_rate(position_data)
            
        elif analysis_type == 'intention':
            result['intention_analysis'] = self._analyze_intention(position_data)
            
        elif analysis_type == 'variations':
            result['variations'] = self._calculate_variations(position_data)
            
        elif analysis_type == 'life_death':
            result['life_death'] = self._analyze_life_death(position_data)
            
        elif analysis_type == 'thickness':
            result['thickness'] = self._analyze_thickness(position_data)
            
        elif analysis_type == 'weight':
            result['weight'] = self._analyze_weight(position_data)
        
        return result
    
    def _calculate_win_rate(self, position_data: Dict) -> float:
        """
        计算胜率 - 使用TW1.0的分析能力
        """
        # 模拟胜率计算，实际应用中会调用Katago或其他引擎
        # 这里结合历史数据和当前局面特征
        board_state = position_data.get('board_state', {})
        move_sequence = position_data.get('move_sequence', [])
        
        # 基于棋子数量和位置的简单估算
        black_stones = board_state.get('black_count', 0)
        white_stones = board_state.get('white_count', 0)
        
        # 模拟一个合理的胜率计算
        total_moves = len(move_sequence)
        base_rate = 50.0
        
        # 根据局面复杂度和手数调整
        complexity_factor = min(total_moves * 0.1, 20.0)  # 最多影响20%
        if black_stones > white_stones:
            base_rate += complexity_factor
        else:
            base_rate -= complexity_factor
            
        # 限制在0-100范围内
        win_rate = max(0.0, min(100.0, base_rate + (black_stones - white_stones) * 0.5))
        
        return round(win_rate, 2)
    
    def _analyze_intention(self, position_data: Dict) -> str:
        """
        意图分析 - 使用TW1.0的意图识别能力
        """
        move = position_data.get('last_move', '')
        board_state = position_data.get('board_state', {})
        
        # 基于位置的意图分析
        if move:
            row, col = self._gtp_to_coordinate(move)
            if 3 <= row <= 15 and 3 <= col <= 15:
                # 中央区域，可能是扩张意图
                return "扩张意图：在中央寻求发展势力"
            elif row < 6 or col < 6 or row > 12 or col > 12:
                # 边缘区域，可能是实地意图
                return "实地意图：巩固边角实地"
            else:
                return "平衡发展：兼顾实地与外势"
        else:
            return "常规布局：遵循定式或常见开局"
    
    def _calculate_variations(self, position_data: Dict) -> List[str]:
        """
        计算后续变化 - 使用TW1.0的变化预测能力
        """
        # 模拟主要变化，实际应用中会调用Katago分析
        variations = [
            f"主要变化1: Q{16 if position_data.get('player', 'B') == 'B' else 4}",
            f"主要变化2: D{16 if position_data.get('player', 'B') == 'B' else 4}", 
            f"主要变化3: {chr(ord('D') + 12 if position_data.get('player', 'B') == 'B' else 4)}{4 if position_data.get('player', 'B') == 'B' else 16}"
        ]
        return variations
    
    def _analyze_life_death(self, position_data: Dict) -> str:
        """
        死活分析 - 使用TW1.0的死活判断能力
        """
        # 简单的死活分析，实际应用中会有更复杂的算法
        board_state = position_data.get('board_state', {})
        surrounding_area = board_state.get('surrounding_analysis', {})
        
        if surrounding_area.get('liberties', 0) < 2:
            return "危险：该块棋气紧，需要注意死活问题"
        elif surrounding_area.get('liberties', 0) > 5:
            return "安全：该块棋较为安定，无死活忧虑"
        else:
            return "一般：该块棋有一定活动空间，但需注意对手攻击"
    
    def _analyze_thickness(self, position_data: Dict) -> str:
        """
        厚薄分析 - 使用TW1.0的厚薄判断能力
        """
        board_state = position_data.get('board_state', {})
        density_map = board_state.get('density_map', {})
        
        if density_map.get('local_density', 0) > 0.6:
            return "厚重：该区域棋子密集，形成厚势"
        elif density_map.get('local_density', 0) < 0.3:
            return "薄弱：该区域棋子稀疏，需注意薄弱环节"
        else:
            return "适中：该区域棋子分布合理，厚薄均衡"
    
    def _analyze_weight(self, position_data: Dict) -> str:
        """
        轻重分析 - 使用TW1.0的轻重判断能力
        """
        move = position_data.get('last_move', '')
        board_state = position_data.get('board_state', {})
        
        if move and board_state.get('is_critical_point', False):
            return "重棋：此手棋关系到全局要点，必须应对此处"
        elif move and board_state.get('strategic_value', 0) > 0.7:
            return "重棋：此手棋战略价值高，影响较大"
        else:
            return "轻棋：此手棋相对较轻，可暂时忽略其他要点"
    
    def _gtp_to_coordinate(self, gtp_coord: str) -> Tuple[int, int]:
        """
        将GTP坐标转换为数组坐标
        """
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
    
    def analyze_position_for_interface(self, board_state: Dict, analysis_type: str = 'full_analysis'):
        """
        为界面提供分析结果 - TW2.0调用TW1.0功能的入口
        """
        request = {
            'request_id': f"req_{int(time.time())}_{hash(str(board_state)) % 10000}",
            'position_data': board_state,
            'type': analysis_type
        }
        
        # 将请求加入分析队列
        self.analysis_queue.put(request)
        
        # 等待结果（带超时）
        timeout = 5.0  # 5秒超时
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if not self.result_queue.empty():
                    result_item = self.result_queue.get_nowait()
                    if result_item['request_id'] == request['request_id']:
                        return result_item['result']
            except queue.Empty:
                pass
            
            time.sleep(0.01)  # 短暂休眠
        
        # 超时返回默认结果
        return self._get_default_analysis_result(analysis_type)
    
    def _get_default_analysis_result(self, analysis_type: str):
        """
        获取默认分析结果（超时时使用）
        """
        if analysis_type == 'full_analysis':
            return {
                'win_rate': 50.0,
                'intention_analysis': '等待深度分析...',
                'variations': ['等待分析...', '等待分析...', '等待分析...'],
                'life_death': '等待分析...',
                'thickness': '等待分析...',
                'weight': '等待分析...'
            }
        else:
            return {'analysis': '等待分析...'}
    
    def place_stone_and_analyze(self, row: int, col: int, player: str = None):
        """
        放置棋子并进行分析 - TW2.0交互时调用TW1.0分析
        """
        if player is None:
            player = self.current_player
        
        # 在棋盘上放置棋子
        success = self.board.place_stone(row, col, player)
        if not success:
            return False, "无效落子"
        
        # 记录历史
        move_notation = self._coordinate_to_gtp(row, col)
        self.game_history.append((move_notation, player))
        
        # 切换玩家
        self.current_player = 'W' if player == 'B' else 'B'
        
        # 使用TW1.0的分析能力进行分析
        board_state = {
            'last_move': move_notation,
            'player': player,
            'board_state': self._get_board_features(),
            'move_sequence': [move[0] for move in self.game_history]
        }
        
        analysis_result = self.analyze_position_for_interface(board_state, 'full_analysis')
        
        return True, analysis_result
    
    def _coordinate_to_gtp(self, row: int, col: int) -> str:
        """
        将坐标转换为GTP格式
        """
        col_str = chr(ord('A') + col)
        if col >= 8:  # 跳过字母'I'
            col_str = chr(ord('A') + col + 1)
        return f"{col_str}{self.board.size - row}"
    
    def _get_board_features(self) -> Dict:
        """
        获取当前棋盘特征，用于分析
        """
        # 统计棋子数量
        black_count = 0
        white_count = 0
        
        for i in range(self.board.size):
            for j in range(self.board.size):
                stone = self.board.get_stone(i, j)
                if stone == 'B':
                    black_count += 1
                elif stone == 'W':
                    white_count += 1
        
        return {
            'black_count': black_count,
            'white_count': white_count,
            'total_moves': len(self.game_history)
        }
    
    def start_interface(self):
        """
        启动交互界面 - TW2.0功能
        """
        # 创建界面实例，传入当前系统实例以实现双向通信
        self.interface = InteractiveGoInterfaceWrapper(self)
        self.interface.run()
    
    def stop(self):
        """
        停止系统
        """
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=2.0)


class InteractiveGoInterfaceWrapper:
    """
    包装交互界面，使其能够调用集成系统
    """
    
    def __init__(self, integrated_system: TWIntegratedSystem):
        self.system = integrated_system
        self.root = None
        self.canvas = None
        self.current_player = 'B'
        
        # 导入GUI组件
        import tkinter as tk
        from tkinter import ttk
        
        self.tk = tk
        self.ttk = ttk
    
    def run(self):
        """
        运行界面
        """
        # 创建主窗口
        self.root = self.tk.Tk()
        self.root.title("TW围棋解说引擎 - 统一系统")
        
        # 设置界面
        self.setup_ui()
        
        # 运行主循环
        self.root.mainloop()
    
    def setup_ui(self):
        """
        设置用户界面
        """
        # 主框架
        main_frame = self.ttk.Frame(self.root)
        main_frame.pack(fill=self.tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：棋盘
        board_frame = self.ttk.LabelFrame(main_frame, text="棋盘", padding=5)
        board_frame.grid(row=0, column=0, sticky=(self.tk.W, self.tk.E, self.tk.N, self.tk.S), padx=(0, 10))
        
        # 创建画布用于绘制棋盘
        self.canvas = self.tk.Canvas(
            board_frame, 
            width=400, 
            height=400, 
            bg='#DEB887'  # 棋盘颜色
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # 右侧：信息面板
        info_frame = self.ttk.LabelFrame(main_frame, text="TW1.0分析结果", padding=5)
        info_frame.grid(row=0, column=1, sticky=(self.tk.W, self.tk.E, self.tk.N, self.tk.S))
        
        # 当前胜率显示
        self.ttk.Label(info_frame, text="当前胜率:").grid(row=0, column=0, sticky=self.tk.W)
        self.win_rate_var = self.tk.StringVar(value="黑棋 50.0% / 白棋 50.0%")
        self.ttk.Label(info_frame, textvariable=self.win_rate_var).grid(row=0, column=1, sticky=self.tk.W)
        
        # 当前意图分析
        self.ttk.Label(info_frame, text="意图分析:").grid(row=1, column=0, sticky=self.tk.W, pady=(10, 0))
        intention_frame = self.ttk.LabelFrame(info_frame, padding=5)
        intention_frame.grid(row=2, column=0, columnspan=2, sticky=(self.tk.W, self.tk.E), pady=(0, 10))
        
        self.intention_var = self.tk.StringVar(value="点击棋盘下子以开始TW1.0深度分析")
        self.ttk.Label(intention_frame, textvariable=self.intention_var, wraplength=300).pack(anchor=self.tk.W)
        
        # 后续变化显示
        self.ttk.Label(info_frame, text="后续变化:").grid(row=3, column=0, sticky=self.tk.W)
        variations_frame = self.ttk.LabelFrame(info_frame, padding=5)
        variations_frame.grid(row=4, column=0, columnspan=2, sticky=(self.tk.W, self.tk.E), pady=(0, 10))
        
        self.variations_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(variations_frame, textvariable=self.variations_var, wraplength=300).pack(anchor=self.tk.W)
        
        # 死活分析
        self.ttk.Label(info_frame, text="死活分析:").grid(row=5, column=0, sticky=self.tk.W)
        self.life_death_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(info_frame, textvariable=self.life_death_var, wraplength=300).grid(row=5, column=1, sticky=self.tk.W)
        
        # 厚薄分析
        self.ttk.Label(info_frame, text="厚薄分析:").grid(row=6, column=0, sticky=self.tk.W)
        self.thickness_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(info_frame, textvariable=self.thickness_var, wraplength=300).grid(row=6, column=1, sticky=self.tk.W)
        
        # 轻重分析
        self.ttk.Label(info_frame, text="轻重分析:").grid(row=7, column=0, sticky=self.tk.W)
        self.weight_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(info_frame, textvariable=self.weight_var, wraplength=300).grid(row=7, column=1, sticky=self.tk.W)
        
        # 控制按钮
        control_frame = self.ttk.Frame(info_frame)
        control_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.ttk.Button(control_frame, text="悔棋", command=self.undo_move).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="重新分析", command=self.reanalyze_position).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="保存棋谱", command=self.save_sgf).pack(side=self.tk.LEFT)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)
        board_frame.rowconfigure(0, weight=1)
        
        info_frame.columnconfigure(1, weight=1)
        info_frame.rowconfigure(4, weight=1)
        
        # 绘制初始棋盘
        self.draw_board()
    
    def draw_board(self):
        """
        绘制棋盘
        """
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        size = 19  # 标准19x19棋盘
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
        star_points = [3, 9, 15]  # 19路棋盘的星位
        for i in star_points:
            for j in star_points:
                x = offset + i * cell_size
                y = offset + j * cell_size
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='black')
        
        # 绘制棋子（从系统棋盘获取）
        for i in range(size):
            for j in range(size):
                # 这里需要从集成系统获取实际棋子状态
                # 为简化，暂时不实现实时同步
                
                # TODO: 从集成系统获取棋子状态并绘制
                pass
    
    def on_board_click(self, event):
        """
        处理棋盘点击事件 - TW2.0调用TW1.0分析
        """
        size = 19
        cell_size = min(400 // size, 400 // size)
        offset = (400 - (size - 1) * cell_size) // 2
        
        # 计算点击位置对应的棋盘坐标
        col = round((event.x - offset) / cell_size)
        row = round((event.y - offset) / cell_size)
        
        # 检查坐标是否在棋盘范围内
        if 0 <= row < size and 0 <= col < size:
            # 调用集成系统进行落子和分析（使用TW1.0能力）
            success, analysis_result = self.system.place_stone_and_analyze(row, col, self.current_player)
            
            if success:
                # 更新界面显示
                self.draw_board()
                
                # 更新分析结果显示
                if isinstance(analysis_result, dict):
                    self.win_rate_var.set(f"黑棋 {analysis_result.get('win_rate', 50.0)}% / 白棋 {100 - analysis_result.get('win_rate', 50.0)}%")
                    self.intention_var.set(analysis_result.get('intention_analysis', ''))
                    
                    variations_text = '; '.join(analysis_result.get('variations', []))
                    self.variations_var.set(variations_text[:100] + "..." if len(variations_text) > 100 else variations_text)
                    
                    self.life_death_var.set(analysis_result.get('life_death', ''))
                    self.thickness_var.set(analysis_result.get('thickness', ''))
                    self.weight_var.set(analysis_result.get('weight', ''))

    def undo_move(self):
        """悔棋功能"""
        if self.system.game_history:
            self.system.game_history.pop()
            self.current_player = 'W' if self.current_player == 'B' else 'B'
            # 重新设置棋盘状态
            self.system.board = GoBoard(19)  # 重置棋盘
            for move, player in self.system.game_history:
                row, col = self.system._gtp_to_coordinate(move)
                if row != -1 and col != -1:
                    self.system.board.place_stone(row, col, player)
            
            self.draw_board()
    
    def reanalyze_position(self):
        """重新分析当前局面"""
        # 使用TW1.0的分析能力重新分析
        board_state = {
            'player': self.current_player,
            'board_state': self.system._get_board_features(),
            'move_sequence': [move[0] for move in self.system.game_history]
        }
        
        analysis_result = self.system.analyze_position_for_interface(board_state, 'full_analysis')
        
        # 更新界面
        if isinstance(analysis_result, dict):
            self.win_rate_var.set(f"黑棋 {analysis_result.get('win_rate', 50.0)}% / 白棋 {100 - analysis_result.get('win_rate', 50.0)}%")
            self.intention_var.set(analysis_result.get('intention_analysis', ''))
            
            variations_text = '; '.join(analysis_result.get('variations', []))
            self.variations_var.set(variations_text[:100] + "..." if len(variations_text) > 100 else variations_text)
            
            self.life_death_var.set(analysis_result.get('life_death', ''))
            self.thickness_var.set(analysis_result.get('thickness', ''))
            self.weight_var.set(analysis_result.get('weight', ''))
    
    def save_sgf(self):
        """保存SGF棋谱"""
        print("SGF棋谱保存功能待实现")


def main():
    """
    主函数：启动统一的TW围棋解说引擎系统
    """
    print("启动TW围棋解说引擎 - 统一系统 (整合TW1.0和TW2.0)")
    print("系统将同时提供核心分析(TW1.0)和交互界面(TW2.0)功能")
    
    # 创建集成系统
    integrated_system = TWIntegratedSystem()
    
    try:
        # 启动界面（这将阻塞主线程）
        integrated_system.start_interface()
    except KeyboardInterrupt:
        print("\n接收到停止信号...")
    finally:
        integrated_system.stop()


if __name__ == "__main__":
    main()