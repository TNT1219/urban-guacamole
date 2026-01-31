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
import json
import os


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
        
        # 新增：SGF相关功能
        self.sgf_parser = None
        self.current_sgf_path = None
        
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
            # 完整分析：胜率、意图、变化、死活、厚薄、轻重、目数影响
            result['win_rate'] = self._calculate_win_rate(position_data)
            result['intention_analysis'] = self._analyze_intention(position_data)
            result['variations'] = self._calculate_variations(position_data)
            result['life_death'] = self._analyze_life_death(position_data)
            result['thickness'] = self._analyze_thickness(position_data)
            result['weight'] = self._analyze_weight(position_data)
            result['territorial_impact'] = self._calculate_territorial_impact(position_data)
            result['tactical_criticality'] = self._evaluate_tactical_criticality(position_data)
            
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
        
        elif analysis_type == 'territorial_impact':
            result['territorial_impact'] = self._calculate_territorial_impact(position_data)
            
        elif analysis_type == 'tactical_criticality':
            result['tactical_criticality'] = self._evaluate_tactical_criticality(position_data)
        
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
        move_sequence = position_data.get('move_sequence', [])
        current_player = position_data.get('player', 'B')
        
        # 基于位置、时机和局势的意图分析
        if move:
            row, col = self._gtp_to_coordinate(move)
            move_number = len(move_sequence)
            
            # 根据手数判断阶段
            if move_number <= 20:  # 布局阶段
                if self._is_corner_area(row, col):
                    return "布局意图：占角或守角，构建根据地"
                elif self._is_side_area(row, col):
                    return "布局意图：挂角或拆边，扩展势力"
                elif self._is_center_area(row, col):
                    return "布局意图：抢占中央要点，构建外势"
                else:
                    return "布局意图：配合整体布局，完善阵势"
            elif move_number <= 100:  # 中盘阶段
                # 检查是否是攻击或防守
                if self._is_near_enemy_groups(row, col, current_player):
                    return "攻击意图：压迫对方棋子，寻求作战机会"
                elif self._is_near_own_weak_group(row, col, current_player):
                    return "防守意图：加固自身弱点，确保棋子安全"
                else:
                    return "战略意图：争夺要点，影响全局形势"
            else:  # 官子阶段
                if self._is_territory_boundary(row, col):
                    return "官子意图：精确收官，巩固实地"
                else:
                    return "官子意图：收束局面，争取微小优势"
        else:
            return "常规布局：遵循定式或常见开局"
    
    def _is_corner_area(self, row: int, col: int) -> bool:
        """判断是否在角落区域"""
        return (row < 5 and col < 5) or (row < 5 and col > 13) or \
               (row > 13 and col < 5) or (row > 13 and col > 13)
    
    def _is_side_area(self, row: int, col: int) -> bool:
        """判断是否在边部区域"""
        return (row < 4 or row > 14 or col < 4 or col > 14) and not self._is_corner_area(row, col)
    
    def _is_center_area(self, row: int, col: int) -> bool:
        """判断是否在中央区域"""
        return 5 <= row <= 13 and 5 <= col <= 13
    
    def _is_near_enemy_groups(self, row: int, col: int, current_player: str) -> bool:
        """判断是否靠近敌方棋块"""
        # 简化的判断逻辑，实际应用中会更复杂
        return True  # 暂时返回True，实际实现需分析棋盘状态
    
    def _is_near_own_weak_group(self, row: int, col: int, current_player: str) -> bool:
        """判断是否靠近己方弱棋"""
        # 简化的判断逻辑
        return False  # 暂时返回False
    
    def _is_territory_boundary(self, row: int, col: int) -> bool:
        """判断是否在实地边界"""
        # 简化的判断逻辑
        return True  # 暂时返回True
    
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
        # 更深入的死活分析，考虑眼形、气数、潜在手段等
        board_state = position_data.get('board_state', {})
        move = position_data.get('last_move', '')
        
        if move:
            row, col = self._gtp_to_coordinate(move)
            move_number = len(position_data.get('move_sequence', []))
            
            # 分析该位置附近棋块的死活状况
            liberties_count = board_state.get('liberties', 0)
            group_size = board_state.get('group_size', 1)
            eye_count = board_state.get('eyes', 0)
            
            # 根据棋块特征判断死活
            if liberties_count == 0:
                return "死棋：该棋块已被提子或即将被提"
            elif liberties_count == 1:
                if eye_count == 0:
                    return "死棋：该块棋只有一个气，处于打吃状态"
                else:
                    return "活棋：虽只有一气，但已有真眼保证安全"
            elif liberties_count == 2:
                if eye_count == 0:
                    return "危险：该块棋只有两气，易受攻击，建议补强"
                elif eye_count == 1:
                    return "有望活棋：有一眼一外气，需进一步做眼"
                else:
                    return "活棋：已有两眼或以上，绝对安全"
            elif liberties_count >= 3:
                if group_size < 5:
                    return "活棋：小块棋有多气，安全无忧"
                elif group_size < 10:
                    if eye_count == 0:
                        return "半活：中等规模棋块，虽有多气但尚无眼位，需尽快做眼"
                    else:
                        return "活棋：已有眼位，相对安全"
                else:
                    if eye_count == 0:
                        return "危险：大龙无眼，虽有多气但仍需谨慎处理"
                    elif eye_count == 1:
                        return "半活：大龙有一眼，但需继续做眼确保安全"
                    else:
                        return "活棋：大龙已有双眼，安全稳固"
            else:
                return "活棋：该块棋气数充足，安全无忧"
        else:
            return "未确定：无法分析该位置的死活状态"
    
    def _analyze_thickness(self, position_data: Dict) -> str:
        """
        厚薄分析 - 使用TW1.0的厚薄判断能力
        """
        board_state = position_data.get('board_state', {})
        move = position_data.get('last_move', '')
        
        if move:
            row, col = self._gtp_to_coordinate(move)
            move_number = len(position_data.get('move_sequence', []))
            
            # 基于位置和周围棋子密度的厚薄分析
            local_density = board_state.get('local_density', 0.0)
            influence_radius = board_state.get('influence_radius', 3)
            nearby_stones = board_state.get('nearby_stones_count', 0)
            
            if local_density > 0.7:
                if nearby_stones > 8:
                    return "过厚：该区域棋子过于密集，效率偏低，可考虑灵活运用"
                else:
                    return "厚重：该区域棋子密集，形成强大厚势，可借力发挥"
            elif local_density > 0.5:
                if nearby_stones > 5:
                    return "偏厚：该区域棋子较多，略显凝重，可适当灵活应对"
                else:
                    return "厚实：该区域较为坚实，具备一定厚度和影响力"
            elif local_density > 0.3:
                if nearby_stones > 3:
                    return "适度：该区域厚薄适中，攻守兼备"
                else:
                    return "轻灵：该区域较为轻盈，机动性强但需注意安全"
            else:
                if nearby_stones == 0:
                    return "薄弱：该区域缺乏支撑，属于薄弱环节，需加强保护"
                else:
                    return "单薄：该区域力量不足，容易被分割攻击，建议补强"
        else:
            return "未确定：无法分析该位置的厚薄状态"
    
    def _calculate_territorial_impact(self, position_data: Dict) -> str:
        """
        计算目数影响 - 评估每步棋对实地的影响
        """
        board_state = position_data.get('board_state', {})
        move = position_data.get('last_move', '')
        
        if move:
            row, col = self._gtp_to_coordinate(move)
            
            # 估算这手棋对实地的影响
            immediate_territory = board_state.get('immediate_territory', 0)  # 直接围成的空
            potential_territory = board_state.get('potential_territory', 0)  # 潜在空
            territory_reduction = board_state.get('territory_reduction', 0)  # 对方实地减少
            influence_expansion = board_state.get('influence_expansion', 0)  # 影响力扩展
            
            total_impact = immediate_territory + potential_territory * 0.5 - territory_reduction * 0.3 + influence_expansion * 0.2
            
            if total_impact > 5:
                return f"巨大价值：此手棋价值约{total_impact:.1f}目，极大提升了局面优势"
            elif total_impact > 2:
                return f"高价值：此手棋价值约{total_impact:.1f}目，显著改善了局面"
            elif total_impact > 0.5:
                return f"中等价值：此手棋价值约{total_impact:.1f}目，有一定积极作用"
            elif total_impact > -0.5:
                return f"低价值：此手棋价值约{total_impact:.1f}目，影响较小"
            elif total_impact > -2:
                return f"负价值：此手棋价值约{total_impact:.1f}目，略有亏损"
            else:
                return f"严重亏损：此手棋价值约{total_impact:.1f}目，明显不利"
    
    def _analyze_weight(self, position_data: Dict) -> str:
        """
        轻重分析 - 使用TW1.0的轻重判断能力
        """
        move = position_data.get('last_move', '')
        board_state = position_data.get('board_state', {})
        move_sequence = position_data.get('move_sequence', [])
        
        if move:
            row, col = self._gtp_to_coordinate(move)
            move_number = len(move_sequence)
            
            # 综合考虑多个因素判断轻重
            strategic_importance = board_state.get('strategic_value', 0.5)
            tactical_criticality = board_state.get('tactical_criticality', 0.3)
            global_influence = board_state.get('global_influence', 0.4)
            game_stage_factor = 1.0 if move_number < 100 else 0.7  # 官子阶段影响降低
            
            # 计算综合权重
            combined_weight = (strategic_importance * 0.4 + 
                              tactical_criticality * 0.4 + 
                              global_influence * 0.2) * game_stage_factor
            
            if combined_weight > 0.8:
                return "极重：此手棋关系到全局胜负，必须立即应对，影响深远"
            elif combined_weight > 0.6:
                return "很重：此手棋战略意义重大，应优先处理，影响全局"
            elif combined_weight > 0.4:
                return "较重：此手棋有一定重要性，值得重视，但可稍缓"
            elif combined_weight > 0.2:
                return "一般：此手棋影响有限，可根据全局形势决定处理时机"
            else:
                return "较轻：此手棋影响较小，可暂时搁置，优先处理其他要点"
        else:
            return "未确定：无法分析该位置的轻重状态"
    
    def _evaluate_tactical_criticality(self, position_data: Dict) -> str:
        """
        评估战术紧急性 - 判断是否需要立即应对
        """
        board_state = position_data.get('board_state', {})
        move = position_data.get('last_move', '')
        
        if move:
            immediate_threat = board_state.get('immediate_threat', 0)  # 立即威胁
            ladder_potential = board_state.get('ladder_potential', 0)  # 征子可能性
            atari_status = board_state.get('atari_status', 0)  # 打吃状态
            cutting_point = board_state.get('cutting_point', 0)  # 切断点
            
            criticality_score = (immediate_threat * 0.4 + 
                                ladder_potential * 0.2 + 
                                atari_status * 0.2 + 
                                cutting_point * 0.2)
            
            if criticality_score > 0.8:
                return "极度紧急：存在立即被吃或造成重大损失的危险，必须立刻应对"
            elif criticality_score > 0.6:
                return "非常紧急：存在明显的战术威胁，应立即处理"
            elif criticality_score > 0.4:
                return "比较紧急：存在一定的战术风险，建议尽快应对"
            elif criticality_score > 0.2:
                return "不太紧急：存在轻微风险，可视情况决定处理时机"
            else:
                return "无需紧急应对：战术风险较低，可按计划行棋"
        else:
            return "未确定：无法评估战术紧急性"
    
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
                'weight': '等待分析...',
                'territorial_impact': '等待分析...',
                'tactical_criticality': '等待分析...'
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
    
    def load_sgf(self, sgf_path: str):
        """
        加载SGF棋谱文件 - 增强功能
        """
        try:
            # 尝试导入SGF解析器
            from sgf_parser import SGFParser
            self.sgf_parser = SGFParser()
            
            # 解析SGF文件
            sgf_data = self.sgf_parser.load_from_file(sgf_path)
            
            # 重置棋盘和游戏历史
            self.board = GoBoard(sgf_data['size'])
            self.game_history = []
            self.current_player = 'B'
            
            # 应用棋谱中的棋步
            for move_num, color, coords in sgf_data['moves']:
                if coords is not None:
                    row, col = coords
                    self.board.place_stone(row, col, color)
                    move_notation = self._coordinate_to_gtp(row, col)
                    self.game_history.append((move_notation, color))
                    self.current_player = 'W' if color == 'B' else 'B'
            
            self.current_sgf_path = sgf_path
            return True, f"成功加载 {len(sgf_data['moves'])} 手棋谱"
        except ImportError:
            return False, "SGF解析模块未找到，请确保已安装sgfmill库"
        except Exception as e:
            return False, f"加载SGF文件失败: {str(e)}"
    
    def get_current_position_analysis(self):
        """
        获取当前局面的完整分析 - 增强功能
        """
        board_state = {
            'player': self.current_player,
            'board_state': self._get_board_features(),
            'move_sequence': [move[0] for move in self.game_history]
        }
        
        analysis_result = self.analyze_position_for_interface(board_state, 'full_analysis')
        return analysis_result
    
    def navigate_game_history(self, step: int):
        """
        导航游戏历史 - 增强功能
        :param step: 步数，正数向前，负数向后
        """
        target_index = len(self.game_history) + step
        target_index = max(0, min(target_index, len(self.game_history)))
        
        # 重置棋盘
        self.board = GoBoard(19)
        self.game_history = self.game_history[:target_index]
        
        # 重新应用棋步到目标位置
        for move_notation, player in self.game_history:
            row, col = self._gtp_to_coordinate(move_notation)
            if row != -1 and col != -1:
                self.board.place_stone(row, col, player)
        
        if self.game_history:
            self.current_player = 'W' if self.game_history[-1][1] == 'B' else 'B'
        else:
            self.current_player = 'B'
        
        return target_index, len(self.game_history)
    
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
    
    def export_analysis_report(self):
        """
        导出分析报告 - 增强功能
        """
        analysis_report = {
            'game_info': {
                'total_moves': len(self.game_history),
                'current_player': self.current_player,
                'board_size': self.board.size,
                'sgf_loaded': self.current_sgf_path is not None
            },
            'current_analysis': self.get_current_position_analysis(),
            'game_history_sample': self.game_history[:10],  # 前10手作为样本
            'improvement_metrics': self.self_improvement_engine.get_self_improvement_report()
        }
        return analysis_report
    
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
        
        # 战术紧急性分析
        self.ttk.Label(info_frame, text="战术紧急性:").grid(row=8, column=0, sticky=self.tk.W)
        self.tactical_criticality_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(info_frame, textvariable=self.tactical_criticality_var, wraplength=300).grid(row=8, column=1, sticky=self.tk.W)
        
        # 目数影响分析
        self.ttk.Label(info_frame, text="目数影响:").grid(row=9, column=0, sticky=self.tk.W)
        self.territorial_impact_var = self.tk.StringVar(value="等待TW1.0分析...")
        self.ttk.Label(info_frame, textvariable=self.territorial_impact_var, wraplength=300).grid(row=9, column=1, sticky=self.tk.W)
        
        # 控制按钮
        control_frame = self.ttk.Frame(info_frame)
        control_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        # 添加SGF导入按钮
        self.ttk.Button(control_frame, text="导入SGF", command=self.load_sgf_file).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="前进", command=self.next_move).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="后退", command=self.prev_move).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="悔棋", command=self.undo_move).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="重新分析", command=self.reanalyze_position).pack(side=self.tk.LEFT, padx=(0, 5))
        self.ttk.Button(control_frame, text="保存棋谱", command=self.save_sgf).pack(side=self.tk.LEFT)
        self.ttk.Button(control_frame, text="导出报告", command=self.export_report).pack(side=self.tk.LEFT, padx=(5, 0))
        
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
                    self.tactical_criticality_var.set(analysis_result.get('tactical_criticality', ''))
                    self.territorial_impact_var.set(analysis_result.get('territorial_impact', ''))

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
            self.tactical_criticality_var.set(analysis_result.get('tactical_criticality', ''))
            self.territorial_impact_var.set(analysis_result.get('territorial_impact', ''))
    
    def draw_board(self):
        """
        绘制棋盘
        """
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        size = self.system.board.size
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
        
        # 绘制棋子（从系统棋盘获取）
        for i in range(size):
            for j in range(size):
                stone = self.system.board.get_stone(i, j)
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
        """
        处理棋盘点击事件 - TW2.0调用TW1.0分析
        """
        size = self.system.board.size
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
                    self.tactical_criticality_var.set(analysis_result.get('tactical_criticality', ''))
                    self.territorial_impact_var.set(analysis_result.get('territorial_impact', ''))

    def undo_move(self):
        """悔棋功能"""
        if self.system.game_history:
            self.system.game_history.pop()
            self.current_player = 'W' if self.current_player == 'B' else 'B'
            # 重新设置棋盘状态
            from go_commentary_engine.board import GoBoard
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
            self.tactical_criticality_var.set(analysis_result.get('tactical_criticality', ''))
            self.territorial_impact_var.set(analysis_result.get('territorial_impact', ''))
    
    def save_sgf(self):
        """保存SGF棋谱"""
        print("SGF棋谱保存功能待实现")
    
    def load_sgf_file(self):
        """导入SGF棋谱文件 - 增强功能"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="选择SGF棋谱文件",
                filetypes=[("SGF files", "*.sgf"), ("All files", "*.*")]
            )
            if filename:
                success, message = self.system.load_sgf(filename)
                if success:
                    self.draw_board()
                    self.reanalyze_position()
                    print(f"成功加载: {message}")
                else:
                    print(f"加载失败: {message}")
        except ImportError:
            print("tkinter.filedialog不可用，请确保已安装完整版Python")
        except Exception as e:
            print(f"导入SGF文件时出错: {str(e)}")
    
    def next_move(self):
        """下一步 - 增强功能"""
        try:
            # 模拟导航到下一步
            current_idx, total_moves = self.system.navigate_game_history(1)
            self.draw_board()
            self.reanalyze_position()
            print(f"前进到第 {current_idx}/{total_moves} 步")
        except Exception as e:
            print(f"前进时出错: {str(e)}")
    
    def prev_move(self):
        """上一步 - 增强功能"""
        try:
            # 模拟导航到上一步
            current_idx, total_moves = self.system.navigate_game_history(-1)
            self.draw_board()
            self.reanalyze_position()
            print(f"后退到第 {current_idx}/{total_moves} 步")
        except Exception as e:
            print(f"后退时出错: {str(e)}")
    
    def export_report(self):
        """导出分析报告 - 增强功能"""
        try:
            report = self.system.export_analysis_report()
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="保存分析报告",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                print(f"分析报告已保存到: {filename}")
        except Exception as e:
            print(f"导出报告时出错: {str(e)}")


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