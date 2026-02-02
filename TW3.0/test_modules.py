"""
TW3.0模块单元测试
"""
import unittest
from intent_recognition import IntentRecognitionEngine
from score_change_analysis import ScoreChangeAnalyzer
from thickness_analysis import ThicknessAnalyzer
from importance_analysis import ImportanceAnalyzer


class TestTW3Modules(unittest.TestCase):
    """测试TW3.0各模块"""
    
    def test_intent_recognition(self):
        """测试意图识别模块"""
        engine = IntentRecognitionEngine()
        self.assertIsNotNone(engine)
        print("意图识别模块测试通过")
    
    def test_score_analysis(self):
        """测试目数分析模块"""
        analyzer = ScoreChangeAnalyzer()
        self.assertIsNotNone(analyzer)
        print("目数分析模块测试通过")
    
    def test_thickness_analysis(self):
        """测试厚薄分析模块"""
        analyzer = ThicknessAnalyzer()
        self.assertIsNotNone(analyzer)
        print("厚薄分析模块测试通过")
    
    def test_importance_analysis(self):
        """测试轻重分析模块"""
        analyzer = ImportanceAnalyzer()
        self.assertIsNotNone(analyzer)
        print("轻重分析模块测试通过")


if __name__ == '__main__':
    unittest.main()
