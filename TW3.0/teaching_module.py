"""
TW3.0教学功能
针对初学者的教学模式
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Lesson:
    """课程"""
    lesson_id: str
    title: str
    description: str
    category: str  # "basic", "intermediate", "advanced"
    difficulty: int  # 1-10
    content: str   # 课程内容（Markdown格式）
    prerequisites: List[str]  # 前置课程ID
    estimated_time: int  # 预估学习时间（分钟）
    created_at: str


@dataclass
class Exercise:
    """练习"""
    exercise_id: str
    lesson_id: str
    title: str
    description: str
    problem_board: Dict  # 棋盘问题
    solution: List[str]  # 解决方案
    hints: List[str]     # 提示
    feedback: str        # 反馈信息
    difficulty: int      # 1-10


@dataclass
class StudentProgress:
    """学生进度"""
    student_id: str
    lesson_id: str
    status: str  # "not_started", "in_progress", "completed"
    score: float  # 0-100
    started_at: str
    completed_at: Optional[str]
    attempts: int
    last_practice: Optional[str]


class TeachingModule:
    """教学模块"""
    
    def __init__(self, db_path: str = "/root/clawd/TW3.0/user_data.db"):
        self.db_path = db_path
        self.init_database()
        self._load_default_curriculum()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建课程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                lesson_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                category TEXT,
                difficulty INTEGER,
                content TEXT,
                prerequisites TEXT,
                estimated_time INTEGER,
                created_at TEXT
            )
        ''')
        
        # 创建练习表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                exercise_id TEXT PRIMARY KEY,
                lesson_id TEXT,
                title TEXT,
                description TEXT,
                problem_board TEXT,
                solution TEXT,
                hints TEXT,
                feedback TEXT,
                difficulty INTEGER,
                FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
            )
        ''')
        
        # 创建学生进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_progress (
                student_id TEXT,
                lesson_id TEXT,
                status TEXT,
                score REAL,
                started_at TEXT,
                completed_at TEXT,
                attempts INTEGER,
                last_practice TEXT,
                PRIMARY KEY (student_id, lesson_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_default_curriculum(self):
        """加载默认课程大纲"""
        default_lessons = [
            Lesson(
                lesson_id="basic_001",
                title="围棋基础：棋盘与棋子",
                description="了解围棋的基本元素",
                category="basic",
                difficulty=1,
                content="""
# 围棋基础：棋盘与棋子

## 棋盘
- 19×19的网格
- 九个小圆点（星位）
- 正中央的星位称为“天元”

## 棋子
- 黑子和白子
- 黑子先行
- 棋子下在线的交叉点上

## 基本规则
- 交替落子
- 棋子一旦落下不能移动
- 地盘大的一方获胜
                """,
                prerequisites=[],
                estimated_time=15,
                created_at=datetime.now().isoformat()
            ),
            Lesson(
                lesson_id="basic_002",
                title="围棋基础：气的概念",
                description="理解棋子的气和提子规则",
                category="basic",
                difficulty=2,
                content="""
# 围棋基础：气的概念

## 什么是“气”
- 棋子或棋块紧邻的空交叉点称为“气”
- 一个棋子最多有4口气（角落2口，边线3口，中央4口）

## 提子规则
- 当一颗棋子或一组棋子的所有气都被对方棋子占据时，就被提掉
- 提掉的棋子要从棋盘上拿走
                """,
                prerequisites=["basic_001"],
                estimated_time=20,
                created_at=datetime.now().isoformat()
            ),
            Lesson(
                lesson_id="basic_003",
                title="围棋基础：死活初步",
                description="学习简单的死活概念",
                category="basic",
                difficulty=3,
                content="""
# 围棋基础：死活初步

## 眼的概念
- 被己方棋子围住的空点称为“眼”
- 有两个真眼的棋块是活棋
- 只有一个眼或没有眼的棋块是死棋

## 活棋的条件
- 一块棋要有两个或两个以上的眼才能活
- 眼必须是真的，不能是假眼
                """,
                prerequisites=["basic_002"],
                estimated_time=25,
                created_at=datetime.now().isoformat()
            )
        ]
        
        # 添加默认课程
        for lesson in default_lessons:
            self.add_lesson(lesson)
    
    def add_lesson(self, lesson: Lesson):
        """添加课程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO lessons
            (lesson_id, title, description, category, difficulty, content, 
             prerequisites, estimated_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lesson.lesson_id,
            lesson.title,
            lesson.description,
            lesson.category,
            lesson.difficulty,
            lesson.content,
            json.dumps(lesson.prerequisites),
            lesson.estimated_time,
            lesson.created_at
        ))
        
        conn.commit()
        conn.close()
    
    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """获取课程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons WHERE lesson_id = ?
        ''', (lesson_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Lesson(
                lesson_id=row[0],
                title=row[1],
                description=row[2],
                category=row[3],
                difficulty=row[4],
                content=row[5],
                prerequisites=json.loads(row[6]),
                estimated_time=row[7],
                created_at=row[8]
            )
        return None
    
    def get_lessons_by_category(self, category: str) -> List[Lesson]:
        """按类别获取课程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons WHERE category = ?
            ORDER BY difficulty
        ''', (category,))
        
        rows = cursor.fetchall()
        conn.close()
        
        lessons = []
        for row in rows:
            lesson = Lesson(
                lesson_id=row[0],
                title=row[1],
                description=row[2],
                category=row[3],
                difficulty=row[4],
                content=row[5],
                prerequisites=json.loads(row[6]),
                estimated_time=row[7],
                created_at=row[8]
            )
            lessons.append(lesson)
        
        return lessons
    
    def add_exercise(self, exercise: Exercise):
        """添加练习"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO exercises
            (exercise_id, lesson_id, title, description, problem_board, 
             solution, hints, feedback, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exercise.exercise_id,
            exercise.lesson_id,
            exercise.title,
            exercise.description,
            json.dumps(exercise.problem_board),
            json.dumps(exercise.solution),
            json.dumps(exercise.hints),
            exercise.feedback,
            exercise.difficulty
        ))
        
        conn.commit()
        conn.close()
    
    def get_exercises_for_lesson(self, lesson_id: str) -> List[Exercise]:
        """获取课程的练习"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM exercises WHERE lesson_id = ?
        ''', (lesson_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        exercises = []
        for row in rows:
            exercise = Exercise(
                exercise_id=row[0],
                lesson_id=row[1],
                title=row[2],
                description=row[3],
                problem_board=json.loads(row[4]),
                solution=json.loads(row[5]),
                hints=json.loads(row[6]),
                feedback=row[7],
                difficulty=row[8]
            )
            exercises.append(exercise)
        
        return exercises
    
    def update_student_progress(self, progress: StudentProgress):
        """更新学生进度"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO student_progress
            (student_id, lesson_id, status, score, started_at, 
             completed_at, attempts, last_practice)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            progress.student_id,
            progress.lesson_id,
            progress.status,
            progress.score,
            progress.started_at,
            progress.completed_at,
            progress.attempts,
            progress.last_practice
        ))
        
        conn.commit()
        conn.close()
    
    def get_student_progress(self, student_id: str, lesson_id: str) -> Optional[StudentProgress]:
        """获取学生课程进度"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM student_progress 
            WHERE student_id = ? AND lesson_id = ?
        ''', (student_id, lesson_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return StudentProgress(
                student_id=row[0],
                lesson_id=row[1],
                status=row[2],
                score=row[3],
                started_at=row[4],
                completed_at=row[5],
                attempts=row[6],
                last_practice=row[7]
            )
        return None
    
    def get_student_completed_lessons(self, student_id: str) -> List[str]:
        """获取学生已完成的课程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lesson_id FROM student_progress 
            WHERE student_id = ? AND status = 'completed'
        ''', (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_next_lesson_for_student(self, student_id: str) -> Optional[Lesson]:
        """获取学生应该学习的下一门课程"""
        completed = self.get_student_completed_lessons(student_id)
        
        # 获取所有基础课程
        basic_lessons = self.get_lessons_by_category("basic")
        
        # 找到第一个未完成且前置条件满足的课程
        for lesson in basic_lessons:
            # 检查前置条件是否都已完成
            prereq_met = all(prereq in completed for prereq in lesson.prerequisites)
            lesson_completed = lesson.lesson_id in completed
            
            if prereq_met and not lesson_completed:
                return lesson
        
        return None


class InteractiveTeachingMode:
    """互动教学模式"""
    
    def __init__(self, teaching_module: TeachingModule):
        self.module = teaching_module
        self.current_lesson = None
        self.current_exercise = None
        self.student_id = None
    
    def start_teaching_session(self, student_id: str):
        """开始教学会话"""
        self.student_id = student_id
        self.start_time = datetime.now().isoformat()  # 记录开始时间
        next_lesson = self.module.get_next_lesson_for_student(student_id)
        
        if next_lesson:
            self.current_lesson = next_lesson
            print(f"开始学习课程: {next_lesson.title}")
            
            # 更新进度
            progress = StudentProgress(
                student_id=student_id,
                lesson_id=next_lesson.lesson_id,
                status="in_progress",
                score=0.0,
                started_at=self.start_time,
                completed_at=None,
                attempts=1,
                last_practice=datetime.now().isoformat()
            )
            self.module.update_student_progress(progress)
            
            return next_lesson
        else:
            print("恭喜！您已经完成了所有基础课程。")
            return None
    
    def get_current_lesson_content(self) -> str:
        """获取当前课程内容"""
        if self.current_lesson:
            return self.current_lesson.content
        return "没有正在进行的课程"
    
    def get_exercises_for_current_lesson(self) -> List[Exercise]:
        """获取当前课程的练习"""
        if self.current_lesson:
            return self.module.get_exercises_for_lesson(self.current_lesson.lesson_id)
        return []
    
    def submit_exercise_answer(self, exercise_id: str, answer: List[str]) -> Dict:
        """提交练习答案"""
        exercise = None
        exercises = self.get_exercises_for_current_lesson()
        
        for ex in exercises:
            if ex.exercise_id == exercise_id:
                exercise = ex
                break
        
        if not exercise:
            return {"success": False, "message": "未找到指定练习"}
        
        # 检查答案（简化版本，实际应该更复杂的比较）
        correct = answer == exercise.solution
        
        result = {
            "success": True,
            "correct": correct,
            "solution": exercise.solution,
            "feedback": exercise.feedback,
            "hints": exercise.hints
        }
        
        if correct:
            result["message"] = "回答正确！"
        else:
            result["message"] = "答案不完全正确，请再试试。"
            if exercise.hints:
                result["hint"] = exercise.hints[0]  # 提供第一个提示
        
        return result
    
    def complete_lesson(self):
        """完成当前课程"""
        if self.current_lesson and self.student_id:
            # 更新进度为完成
            progress = StudentProgress(
                student_id=self.student_id,
                lesson_id=self.current_lesson.lesson_id,
                status="completed",
                score=100.0,  # 简化处理
                started_at=getattr(self, 'start_time', datetime.now().isoformat()),
                completed_at=datetime.now().isoformat(),
                attempts=1,
                last_practice=datetime.now().isoformat()
            )
            self.module.update_student_progress(progress)
            
            print(f"课程 '{self.current_lesson.title}' 已完成！")
            
            # 设置为无当前课程
            self.current_lesson = None


def main():
    """主函数：演示教学功能"""
    print("启动TW3.0教学功能")
    
    # 创建教学模块
    teaching_module = TeachingModule()
    
    # 创建互动教学模式
    interactive_mode = InteractiveTeachingMode(teaching_module)
    
    # 模拟学生ID
    student_id = "student_001"
    
    print(f"\n为学生 {student_id} 开始教学会话...")
    
    # 开始学习
    lesson = interactive_mode.start_teaching_session(student_id)
    
    if lesson:
        print(f"\n课程标题: {lesson.title}")
        print(f"难度: {lesson.difficulty}/10")
        print(f"预估时间: {lesson.estimated_time}分钟")
        print(f"\n课程内容:\n{lesson.content}")
        
        # 获取练习
        exercises = interactive_mode.get_exercises_for_current_lesson()
        print(f"\n本课程包含 {len(exercises)} 个练习")
        
        # 添加一个示例练习
        example_exercise = Exercise(
            exercise_id="ex_001",
            lesson_id=lesson.lesson_id,
            title="气的计算练习",
            description="计算图中黑棋的气数",
            problem_board={
                "black_stones": ["D4", "D5", "E4"],
                "white_stones": ["C4", "D3"],
                "question": "计算黑棋的气数"
            },
            solution=["D6", "E5", "E3"],  # 假设的答案
            hints=["观察黑棋周围的空点", "注意边线上的特殊情况"],
            feedback="正确！你很好地掌握了气的概念。",
            difficulty=2
        )
        teaching_module.add_exercise(example_exercise)
        
        print(f"\n练习: {example_exercise.title}")
        print(f"描述: {example_exercise.description}")
        
        # 模拟提交答案
        answer = ["D6", "E5", "E3"]  # 正确答案
        result = interactive_mode.submit_exercise_answer("ex_001", answer)
        
        print(f"\n练习结果: {result['message']}")
        print(f"反馈: {result['feedback']}")
        
        # 完成课程
        interactive_mode.complete_lesson()
    else:
        print("没有找到适合的课程")
    
    print("\n教学功能演示完成")


if __name__ == "__main__":
    main()