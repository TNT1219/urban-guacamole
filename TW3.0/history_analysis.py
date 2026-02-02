"""
TW3.0历史数据分析系统
分析用户的下棋习惯和弱点
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass


@dataclass
class UserPattern:
    """用户模式数据"""
    pattern_type: str  # 'opening', 'middlegame', 'endgame', 'tactical', 'strategic'
    pattern_name: str  # 具体模式名称
    frequency: float   # 出现频率 (0-1)
    success_rate: float  # 成功率 (0-1)
    average_score: float  # 平均得分
    weakness_level: float  # 弱点程度 (0-1, 1为最弱)


@dataclass
class GameRecord:
    """棋局记录"""
    game_id: str
    timestamp: datetime
    player_color: str  # 'B' or 'W'
    opponent_strength: str  # 对手强度描述
    game_result: str  # 'win', 'loss', 'draw'
    komi: float
    game_length: int  # 手数
    opening_pattern: str  # 开局模式
    score_difference: float  # 输赢分数差
    mistakes_count: int  # 明显失误次数
    blunders_count: int  # 严重失误次数
    avg_thinking_time: float  # 平均思考时间(秒)


class UserDataStorage:
    """用户数据存储结构"""
    
    def __init__(self, db_path: str = "/root/clawd/TW3.0/user_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建棋局记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                timestamp TEXT,
                player_color TEXT,
                opponent_strength TEXT,
                game_result TEXT,
                komi REAL,
                game_length INTEGER,
                opening_pattern TEXT,
                score_difference REAL,
                mistakes_count INTEGER,
                blunders_count INTEGER,
                avg_thinking_time REAL
            )
        ''')
        
        # 创建用户模式表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                pattern_type TEXT,
                pattern_name TEXT,
                frequency REAL,
                success_rate REAL,
                average_score REAL,
                weakness_level REAL,
                recorded_at TEXT
            )
        ''')
        
        # 创建分析报告表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                report_type TEXT,
                report_data TEXT,
                generated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_game_record(self, game_record: GameRecord):
        """保存棋局记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO games 
            (game_id, timestamp, player_color, opponent_strength, game_result, 
             komi, game_length, opening_pattern, score_difference, 
             mistakes_count, blunders_count, avg_thinking_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_record.game_id,
            game_record.timestamp.isoformat(),
            game_record.player_color,
            game_record.opponent_strength,
            game_record.game_result,
            game_record.komi,
            game_record.game_length,
            game_record.opening_pattern,
            game_record.score_difference,
            game_record.mistakes_count,
            game_record.blunders_count,
            game_record.avg_thinking_time
        ))
        
        conn.commit()
        conn.close()
    
    def save_user_pattern(self, user_id: str, pattern: UserPattern):
        """保存用户模式"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_patterns 
            (user_id, pattern_type, pattern_name, frequency, success_rate, 
             average_score, weakness_level, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            pattern.pattern_type,
            pattern.pattern_name,
            pattern.frequency,
            pattern.success_rate,
            pattern.average_score,
            pattern.weakness_level,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_games(self, user_id: str, limit: int = 100) -> List[GameRecord]:
        """获取用户棋局记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM games 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        games = []
        for row in rows:
            game = GameRecord(
                game_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                player_color=row[2],
                opponent_strength=row[3],
                game_result=row[4],
                komi=row[5],
                game_length=row[6],
                opening_pattern=row[7],
                score_difference=row[8],
                mistakes_count=row[9],
                blunders_count=row[10],
                avg_thinking_time=row[11]
            )
            games.append(game)
        
        return games
    
    def get_user_patterns(self, user_id: str, pattern_type: str = None) -> List[UserPattern]:
        """获取用户模式"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pattern_type:
            cursor.execute('''
                SELECT pattern_type, pattern_name, frequency, success_rate, 
                       average_score, weakness_level
                FROM user_patterns
                WHERE user_id = ? AND pattern_type = ?
                ORDER BY weakness_level DESC
            ''', (user_id, pattern_type))
        else:
            cursor.execute('''
                SELECT pattern_type, pattern_name, frequency, success_rate, 
                       average_score, weakness_level
                FROM user_patterns
                WHERE user_id = ?
                ORDER BY weakness_level DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            pattern = UserPattern(
                pattern_type=row[0],
                pattern_name=row[1],
                frequency=row[2],
                success_rate=row[3],
                average_score=row[4],
                weakness_level=row[5]
            )
            patterns.append(pattern)
        
        return patterns


class HabitAnalyzer:
    """习惯分析算法"""
    
    def __init__(self, storage: UserDataStorage):
        self.storage = storage
    
    def analyze_opening_habits(self, user_id: str) -> List[UserPattern]:
        """分析开局习惯"""
        games = self.storage.get_user_games(user_id, limit=50)  # 最近50局
        
        if not games:
            return []
        
        # 统计开局模式
        opening_counts = {}
        opening_success = {}
        
        for game in games:
            opening = game.opening_pattern
            if opening not in opening_counts:
                opening_counts[opening] = 0
                opening_success[opening] = {'wins': 0, 'total': 0}
            
            opening_counts[opening] += 1
            opening_success[opening]['total'] += 1
            
            if game.game_result == 'win':
                opening_success[opening]['wins'] += 1
        
        patterns = []
        total_games = len(games)
        
        for opening, count in opening_counts.items():
            success_data = opening_success[opening]
            success_rate = success_data['wins'] / success_data['total'] if success_data['total'] > 0 else 0
            frequency = count / total_games
            weakness_level = (1 - success_rate) * frequency  # 弱点程度
            
            pattern = UserPattern(
                pattern_type='opening',
                pattern_name=opening,
                frequency=frequency,
                success_rate=success_rate,
                average_score=0,  # 暂时不用
                weakness_level=weakness_level
            )
            patterns.append(pattern)
        
        # 按弱点程度排序
        patterns.sort(key=lambda x: x.weakness_level, reverse=True)
        return patterns
    
    def analyze_middlegame_habits(self, user_id: str) -> List[UserPattern]:
        """分析中盘习惯"""
        games = self.storage.get_user_games(user_id, limit=50)
        
        if not games:
            return []
        
        # 分析中盘失误模式
        mistake_types = ['tactical_blunder', 'strategic_mistake', 'time_trouble', 'over_concentration']
        pattern_stats = {mt: {'count': 0, 'impact': 0} for mt in mistake_types}
        
        for game in games:
            # 简化：根据失误数量和类型推断模式
            total_mistakes = game.mistakes_count + game.blunders_count
            
            if total_mistakes > 5:
                pattern_stats['tactical_blunder']['count'] += 1
                pattern_stats['tactical_blunder']['impact'] += total_mistakes
            elif game.avg_thinking_time < 10:  # 思考时间少
                pattern_stats['time_trouble']['count'] += 1
                pattern_stats['time_trouble']['impact'] += 1
            # 可以继续添加更多模式识别逻辑
        
        patterns = []
        for mtype, stats in pattern_stats.items():
            if stats['count'] > 0:
                avg_impact = stats['impact'] / stats['count']
                frequency = stats['count'] / len(games)
                weakness_level = frequency * (avg_impact / 10)  # 简化的弱点计算
                
                pattern = UserPattern(
                    pattern_type='middlegame',
                    pattern_name=mtype,
                    frequency=frequency,
                    success_rate=1 - (stats['count'] / len(games)),  # 简化计算
                    average_score=-avg_impact,  # 负值表示负面影响
                    weakness_level=min(weakness_level, 1.0)
                )
                patterns.append(pattern)
        
        patterns.sort(key=lambda x: x.weakness_level, reverse=True)
        return patterns
    
    def analyze_endgame_habits(self, user_id: str) -> List[UserPattern]:
        """分析官子习惯"""
        games = self.storage.get_user_games(user_id, limit=50)
        
        if not games:
            return []
        
        # 分析官子阶段的表现
        close_games = [g for g in games if abs(g.score_difference) <= 5]  # 细分的棋局
        
        if not close_games:
            return []
        
        # 计算在细微局面下的表现
        winning_close_games = sum(1 for g in close_games if 
                                 (g.game_result == 'win' and g.player_color == 'B') or 
                                 (g.game_result == 'loss' and g.player_color == 'W'))
        
        success_rate = winning_close_games / len(close_games) if close_games else 0
        frequency = len(close_games) / len(games)
        weakness_level = (1 - success_rate) * frequency
        
        pattern = UserPattern(
            pattern_type='endgame',
            pattern_name='close_game_performance',
            frequency=frequency,
            success_rate=success_rate,
            average_score=sum(g.score_difference for g in close_games) / len(close_games) if close_games else 0,
            weakness_level=weakness_level
        )
        
        return [pattern]
    
    def analyze_all_habits(self, user_id: str) -> List[UserPattern]:
        """分析所有习惯"""
        patterns = []
        patterns.extend(self.analyze_opening_habits(user_id))
        patterns.extend(self.analyze_middlegame_habits(user_id))
        patterns.extend(self.analyze_endgame_habits(user_id))
        
        # 去重并排序
        unique_patterns = {}
        for pattern in patterns:
            key = f"{pattern.pattern_type}:{pattern.pattern_name}"
            if key not in unique_patterns or unique_patterns[key].weakness_level < pattern.weakness_level:
                unique_patterns[key] = pattern
        
        sorted_patterns = sorted(unique_patterns.values(), key=lambda x: x.weakness_level, reverse=True)
        return sorted_patterns


class WeaknessIdentifier:
    """识别用户弱点模式"""
    
    def __init__(self, storage: UserDataStorage):
        self.storage = storage
        self.habit_analyzer = HabitAnalyzer(storage)
    
    def identify_weaknesses(self, user_id: str) -> Dict[str, List[Dict]]:
        """识别用户弱点"""
        patterns = self.habit_analyzer.analyze_all_habits(user_id)
        
        # 按类型组织弱点
        weaknesses = {
            'opening': [],
            'middlegame': [],
            'endgame': [],
            'tactical': [],
            'strategic': []
        }
        
        # 识别高弱点级别的模式
        high_weakness_patterns = [p for p in patterns if p.weakness_level > 0.3]
        
        for pattern in high_weakness_patterns:
            weakness_info = {
                'name': pattern.pattern_name,
                'frequency': pattern.frequency,
                'success_rate': pattern.success_rate,
                'weakness_level': pattern.weakness_level,
                'description': self._get_weakness_description(pattern)
            }
            
            if pattern.pattern_type in weaknesses:
                weaknesses[pattern.pattern_type].append(weakness_info)
        
        return weaknesses
    
    def _get_weakness_description(self, pattern: UserPattern) -> str:
        """获取弱点描述"""
        if pattern.pattern_type == 'opening':
            if pattern.weakness_level > 0.7:
                return "开局选择存在问题，胜率明显偏低"
            elif pattern.weakness_level > 0.5:
                return "开局掌握不够熟练，需要加强练习"
            else:
                return "开局表现一般，有改进空间"
        
        elif pattern.pattern_type == 'middlegame':
            if pattern.weakness_level > 0.7:
                return "中盘战斗能力严重不足，容易出现重大失误"
            elif pattern.weakness_level > 0.5:
                return "中盘需要加强，注意减少不必要的失误"
            else:
                return "中盘表现尚可，但仍有提升空间"
        
        elif pattern.pattern_type == 'endgame':
            if pattern.weakness_level > 0.7:
                return "官子阶段表现糟糕，经常在细微局面失利"
            elif pattern.weakness_level > 0.5:
                return "官子技巧有待提高"
            else:
                return "官子表现一般"
        
        else:
            return "存在需要改进的问题"
    
    def generate_weakness_report(self, user_id: str) -> str:
        """生成弱点报告"""
        weaknesses = self.identify_weaknesses(user_id)
        
        report = "=== 用户弱点分析报告 ===\n\n"
        
        total_weaknesses = sum(len(v) for v in weaknesses.values())
        
        if total_weaknesses == 0:
            report += "恭喜！未发现明显弱点，继续保持！\n"
        else:
            for category, items in weaknesses.items():
                if items:
                    report += f"【{category.upper()}】\n"
                    for item in items:
                        report += f"  • {item['name']}: {item['description']}\n"
                        report += f"    频率: {item['frequency']:.2%}, 胜率: {item['success_rate']:.2%}, 弱点程度: {item['weakness_level']:.2%}\n"
                    report += "\n"
        
        report += f"总计识别 {total_weaknesses} 个主要弱点领域\n"
        report += f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report


def main():
    """主函数：演示历史数据分析系统"""
    print("启动TW3.0历史数据分析系统")
    
    # 初始化存储
    storage = UserDataStorage()
    
    # 创建分析器
    habit_analyzer = HabitAnalyzer(storage)
    weakness_identifier = WeaknessIdentifier(storage)
    
    # 模拟一些棋局数据用于演示
    sample_games = [
        GameRecord(
            game_id=f"game_{i:03d}",
            timestamp=datetime.now() - timedelta(days=i),
            player_color='B',
            opponent_strength='intermediate',
            game_result='win' if i % 3 != 0 else 'loss',
            komi=7.5,
            game_length=234 + i * 2,
            opening_pattern='Chinese' if i % 2 == 0 else 'Shimari',
            score_difference=12.5 - i % 5,
            mistakes_count=max(0, 3 - i % 4),
            blunders_count=1 if i % 7 == 0 else 0,
            avg_thinking_time=25.5 + i % 10
        )
        for i in range(30)
    ]
    
    # 保存示例数据
    for game in sample_games:
        storage.save_game_record(game)
    
    print(f"已保存 {len(sample_games)} 局示例棋局数据")
    
    # 分析用户习惯
    print("\n正在分析用户习惯...")
    user_patterns = habit_analyzer.analyze_all_habits("demo_user")
    
    print(f"识别到 {len(user_patterns)} 个用户模式:")
    for i, pattern in enumerate(user_patterns[:5]):  # 显示前5个
        print(f"  {i+1}. {pattern.pattern_type}: {pattern.pattern_name} "
              f"(弱点程度: {pattern.weakness_level:.3f})")
    
    # 生成弱点报告
    print("\n生成弱点分析报告...")
    weakness_report = weakness_identifier.generate_weakness_report("demo_user")
    print(weakness_report)
    
    print("历史数据分析系统演示完成")


if __name__ == "__main__":
    main()