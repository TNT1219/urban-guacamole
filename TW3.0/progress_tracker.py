"""
TW3.0进步追踪系统
记录用户棋力变化曲线
"""

import json
import sqlite3
import os
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass
import matplotlib.pyplot as plt
from io import BytesIO
import base64


@dataclass
class ProgressRecord:
    """进步记录"""
    record_id: str
    user_id: str
    timestamp: datetime
    rating: float  # 评级分
    rank: str  # 段位
    win_rate: float  # 胜率
    strength_estimate: float  # 实力估计
    games_played: int  # 总对局数
    games_won: int  # 获胜局数
    performance_rating: float  # 战绩评级
    improvement_score: float  # 进步分数


class RatingCalculator:
    """评级计算器"""
    
    def __init__(self):
        self.initial_rating = 1500  # 初始等级分
        self.volatility_base = 300  # 波动基数
    
    def calculate_new_rating(self, old_rating: float, opponent_rating: float, 
                           game_result: float, games_played: int) -> float:
        """
        计算新等级分
        game_result: 1=胜, 0=负, 0.5=和
        """
        # 计算期望胜率
        expected = 1.0 / (1 + 10**((opponent_rating - old_rating) / 400))
        
        # 计算K因子（随着对局数增加而减小）
        k_factor = max(20, 60 - games_played * 0.1)  # 最小K值为20
        
        # 更新等级分
        new_rating = old_rating + k_factor * (game_result - expected)
        
        return max(100, new_rating)  # 最低100分
    
    def estimate_strength(self, rating: float) -> str:
        """根据等级分估计实力段位"""
        if rating < 300:
            return "30级"
        elif rating < 600:
            return "25级"
        elif rating < 900:
            return "20级"
        elif rating < 1200:
            return "15级"
        elif rating < 1500:
            return "10级"
        elif rating < 1800:
            return "5级"
        elif rating < 2100:
            return "1段"
        elif rating < 2400:
            return "2段"
        elif rating < 2700:
            return "3段"
        elif rating < 3000:
            return "4段"
        elif rating < 3300:
            return "5段"
        elif rating < 3600:
            return "6段"
        else:
            return "7段+"


class ProgressTracker:
    """进步追踪器"""
    
    def __init__(self, db_path: str = "/root/clawd/TW3.0/user_data.db"):
        self.db_path = db_path
        self.rating_calculator = RatingCalculator()
        self.init_database()
    
    def init_database(self):
        """初始化数据库（如果尚未创建）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建进步记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_records (
                record_id TEXT PRIMARY KEY,
                user_id TEXT,
                timestamp TEXT,
                rating REAL,
                rank TEXT,
                win_rate REAL,
                strength_estimate REAL,
                games_played INTEGER,
                games_won INTEGER,
                performance_rating REAL,
                improvement_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_game_result(self, user_id: str, opponent_rating: float, 
                          game_result: float, opponent_strength: str = "unknown") -> ProgressRecord:
        """
        记录对局结果并更新进步数据
        game_result: 1=胜, 0=负, 0.5=和
        """
        # 获取用户最新记录
        last_record = self.get_latest_record(user_id)
        
        if last_record:
            old_rating = last_record.rating
            games_played = last_record.games_played + 1
            games_won = last_record.games_won + (1 if game_result == 1 else 0)
        else:
            old_rating = self.rating_calculator.initial_rating
            games_played = 1
            games_won = 1 if game_result == 1 else 0
        
        # 计算新等级分
        new_rating = self.rating_calculator.calculate_new_rating(
            old_rating, opponent_rating, game_result, games_played
        )
        
        # 计算胜率
        win_rate = games_won / games_played if games_played > 0 else 0
        
        # 估计实力段位
        strength_rank = self.rating_calculator.estimate_strength(new_rating)
        
        # 计算表现等级分（基于对手等级分和比赛结果）
        performance_rating = opponent_rating + 400 * (game_result - 0.5) * 2
        
        # 计算进步分数（基于等级分增长和近期表现）
        improvement_score = self._calculate_improvement_score(user_id, new_rating, games_played)
        
        # 创建新的记录
        record = ProgressRecord(
            record_id=f"prog_{user_id}_{int(datetime.now().timestamp())}",
            user_id=user_id,
            timestamp=datetime.now(),
            rating=new_rating,
            rank=strength_rank,
            win_rate=win_rate,
            strength_estimate=new_rating,
            games_played=games_played,
            games_won=games_won,
            performance_rating=performance_rating,
            improvement_score=improvement_score
        )
        
        # 保存记录
        self.save_progress_record(record)
        
        return record
    
    def _calculate_improvement_score(self, user_id: str, current_rating: float, 
                                   total_games: int) -> float:
        """计算进步分数"""
        # 获取最近的评级记录
        recent_records = self.get_recent_records(user_id, days=30)
        
        if len(recent_records) < 2:
            return 0.0  # 没有足够的历史数据
        
        # 计算最近的评级趋势
        ratings_over_time = [r.strength_estimate for r in recent_records]
        time_points = list(range(len(ratings_over_time)))
        
        # 使用最小二乘法计算趋势
        n = len(ratings_over_time)
        sum_x = sum(time_points)
        sum_y = sum(ratings_over_time)
        sum_xy = sum(x * y for x, y in zip(time_points, ratings_over_time))
        sum_x2 = sum(x * x for x in time_points)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0.0
        
        # 结合斜率和最近的增长来计算进步分数
        recent_growth = current_rating - ratings_over_time[0] if ratings_over_time else 0
        improvement_score = slope * 0.7 + (recent_growth / max(1, len(ratings_over_time))) * 0.3
        
        return improvement_score
    
    def save_progress_record(self, record: ProgressRecord):
        """保存进步记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO progress_records
            (record_id, user_id, timestamp, rating, rank, win_rate, 
             strength_estimate, games_played, games_won, performance_rating, improvement_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.record_id,
            record.user_id,
            record.timestamp.isoformat(),
            record.rating,
            record.rank,
            record.win_rate,
            record.strength_estimate,
            record.games_played,
            record.games_won,
            record.performance_rating,
            record.improvement_score
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_record(self, user_id: str) -> Optional[ProgressRecord]:
        """获取用户最新记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM progress_records 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ProgressRecord(
                record_id=row[0],
                user_id=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                rating=row[3],
                rank=row[4],
                win_rate=row[5],
                strength_estimate=row[6],
                games_played=row[7],
                games_won=row[8],
                performance_rating=row[9],
                improvement_score=row[10]
            )
        return None
    
    def get_recent_records(self, user_id: str, days: int = 30) -> List[ProgressRecord]:
        """获取用户近期记录"""
        since_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM progress_records 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (user_id, since_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            record = ProgressRecord(
                record_id=row[0],
                user_id=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                rating=row[3],
                rank=row[4],
                win_rate=row[5],
                strength_estimate=row[6],
                games_played=row[7],
                games_won=row[8],
                performance_rating=row[9],
                improvement_score=row[10]
            )
            records.append(record)
        
        return records
    
    def get_progress_summary(self, user_id: str) -> Dict:
        """获取进步汇总"""
        latest = self.get_latest_record(user_id)
        if not latest:
            return {
                'current_rating': self.rating_calculator.initial_rating,
                'current_rank': self.rating_calculator.estimate_strength(self.rating_calculator.initial_rating),
                'total_games': 0,
                'win_rate': 0.0,
                'improvement_trend': 'unknown',
                'last_updated': None
            }
        
        # 获取过去30天的记录以计算趋势
        recent_records = self.get_recent_records(user_id, days=30)
        
        if len(recent_records) >= 2:
            initial_rating = recent_records[0].rating
            final_rating = recent_records[-1].rating
            rating_change = final_rating - initial_rating
            
            if rating_change > 50:
                trend = 'strongly_improving'
            elif rating_change > 10:
                trend = 'improving'
            elif rating_change < -50:
                trend = 'declining'
            elif rating_change < -10:
                trend = 'declining_slowly'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'current_rating': latest.rating,
            'current_rank': latest.rank,
            'total_games': latest.games_played,
            'win_rate': latest.win_rate,
            'improvement_trend': trend,
            'last_updated': latest.timestamp.isoformat()
        }
    
    def generate_progress_chart(self, user_id: str, days: int = 90) -> Optional[str]:
        """生成进步图表并返回base64编码的图像"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 使用非GUI后端
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter
            import matplotlib.dates as mdates
            
            records = self.get_recent_records(user_id, days=days)
            
            if not records:
                return None
            
            dates = [r.timestamp for r in records]
            ratings = [r.rating for r in records]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(dates, ratings, marker='o', linewidth=2, markersize=6)
            ax.set_title(f'{user_id} 的等级分变化趋势 (最近{days}天)', fontsize=14)
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('等级分', fontsize=12)
            
            # 格式化x轴日期
            ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 保存到内存中的字节流
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            
            # 转换为base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close()  # 关闭图形以释放内存
            
            return f"data:image/png;base64,{img_base64}"
            
        except ImportError:
            print("matplotlib未安装，无法生成图表")
            return None
        except Exception as e:
            print(f"生成图表时出错: {e}")
            return None


class MilestoneManager:
    """里程碑管理器"""
    
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker
        self.milestones = {
            'first_game': {'threshold': 1, 'achieved': False, 'name': '首局对战'},
            'ten_games': {'threshold': 10, 'achieved': False, 'name': '十局挑战'},
            'first_win': {'threshold': 1, 'achieved': False, 'name': '首胜'},
            'rating_1600': {'threshold': 1600, 'achieved': False, 'name': '业余高手'},
            'rating_1800': {'threshold': 1800, 'achieved': False, 'name': '业余强手'},
            'rating_2000': {'threshold': 2000, 'achieved': False, 'name': '业余高段'},
            'win_rate_60': {'threshold': 0.6, 'achieved': False, 'name': '六成胜率'},
            'win_rate_70': {'threshold': 0.7, 'achieved': False, 'name': '七成胜率'},
        }
    
    def check_milestones(self, user_id: str) -> List[Dict]:
        """检查并返回新达成的里程碑"""
        summary = self.tracker.get_progress_summary(user_id)
        new_milestones = []
        
        # 检查对局数里程碑
        if summary['total_games'] >= 1 and not self.milestones['first_game']['achieved']:
            self.milestones['first_game']['achieved'] = True
            new_milestones.append(self.milestones['first_game'].copy())
        
        if summary['total_games'] >= 10 and not self.milestones['ten_games']['achieved']:
            self.milestones['ten_games']['achieved'] = True
            new_milestones.append(self.milestones['ten_games'].copy())
        
        # 检查胜率里程碑
        if summary['win_rate'] >= 0.6 and not self.milestones['win_rate_60']['achieved']:
            self.milestones['win_rate_60']['achieved'] = True
            new_milestones.append(self.milestones['win_rate_60'].copy())
        
        if summary['win_rate'] >= 0.7 and not self.milestones['win_rate_70']['achieved']:
            self.milestones['win_rate_70']['achieved'] = True
            new_milestones.append(self.milestones['win_rate_70'].copy())
        
        # 检查等级分里程碑
        current_rating = summary['current_rating']
        if current_rating >= 1600 and not self.milestones['rating_1600']['achieved']:
            self.milestones['rating_1600']['achieved'] = True
            new_milestones.append(self.milestones['rating_1600'].copy())
        
        if current_rating >= 1800 and not self.milestones['rating_1800']['achieved']:
            self.milestones['rating_1800']['achieved'] = True
            new_milestones.append(self.milestones['rating_1800'].copy())
        
        if current_rating >= 2000 and not self.milestones['rating_2000']['achieved']:
            self.milestones['rating_2000']['achieved'] = True
            new_milestones.append(self.milestones['rating_2000'].copy())
        
        # 检查获胜局数（需要额外查询）
        latest_record = self.tracker.get_latest_record(user_id)
        if latest_record and latest_record.games_won >= 1 and not self.milestones['first_win']['achieved']:
            self.milestones['first_win']['achieved'] = True
            new_milestones.append(self.milestones['first_win'].copy())
        
        return new_milestones


def main():
    """主函数：演示进步追踪系统"""
    print("启动TW3.0进步追踪系统")
    
    # 初始化进度追踪器
    tracker = ProgressTracker()
    
    # 创建里程碑管理器
    milestone_manager = MilestoneManager(tracker)
    
    # 模拟一些对局结果
    user_id = "demo_player"
    
    print(f"\n为用户 {user_id} 模拟对局记录...")
    
    # 模拟30局对战
    for i in range(30):
        # 随机生成对手等级分和对战结果
        opponent_rating = 1400 + i * 5  # 对手等级分逐渐提高
        game_result = 1 if i % 3 != 2 else 0  # 约66%胜率
        
        record = tracker.record_game_result(
            user_id=user_id,
            opponent_rating=opponent_rating,
            game_result=game_result
        )
        
        if i % 10 == 9:  # 每10局输出一次状态
            print(f"  第 {i+1} 局: 等级分 {record.rating:.1f}, 段位 {record.rank}, 胜率 {record.win_rate:.1%}")
    
    # 输出最终统计
    summary = tracker.get_progress_summary(user_id)
    print(f"\n最终统计:")
    print(f"  当前等级分: {summary['current_rating']:.1f}")
    print(f"  当前段位: {summary['current_rank']}")
    print(f"  总对局数: {summary['total_games']}")
    print(f"  胜率: {summary['win_rate']:.1%}")
    print(f"  进步趋势: {summary['improvement_trend']}")
    
    # 检查里程碑
    milestones = milestone_manager.check_milestones(user_id)
    if milestones:
        print(f"\n达成的里程碑 ({len(milestones)} 个):")
        for milestone in milestones:
            print(f"  🏆 {milestone['name']}")
    
    # 尝试生成图表（如果matplotlib可用）
    chart_url = tracker.generate_progress_chart(user_id, days=30)
    if chart_url:
        print(f"\n已生成等级分变化图表")
    else:
        print(f"\n无法生成图表（matplotlib可能未安装）")
    
    print("\n进步追踪系统演示完成")


if __name__ == "__main__":
    main()