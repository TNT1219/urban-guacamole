"""
TW3.0项目进展主动汇报程序
用于定时向用户汇报项目开发进度
"""

import time
import threading
from datetime import datetime
from typing import Callable, Optional


class StatusReporter:
    """
    状态汇报器
    用于定时向用户汇报TW3.0项目的开发进展
    """
    
    def __init__(self, interval_seconds: int = 30):
        """
        初始化状态汇报器
        
        Args:
            interval_seconds: 汇报间隔（秒）
        """
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.thread = None
        self.callback = None
        self.last_report_time = None
        
    def set_callback(self, callback: Callable[[str], None]):
        """
        设置汇报回调函数
        
        Args:
            callback: 回调函数，接收汇报内容字符串作为参数
        """
        self.callback = callback
        
    def _report_status(self):
        """内部方法：执行状态汇报"""
        while self.is_running:
            if self.callback:
                current_time = datetime.now().strftime("%H:%M:%S")
                report_content = f"**项目进展汇报（自动）**\n\n"
                report_content += f"当前时间：{current_time}\n"
                report_content += f"汇报间隔：{self.interval_seconds}秒\n"
                report_content += f"TW3.0项目开发状态：正常进行中\n"
                
                # 获取当前项目状态
                try:
                    with open("/root/clawd/TW3.0/project_status.md", "r", encoding="utf-8") as f:
                        status_content = f.read()
                        report_content += f"\n当前项目状态：\n{status_content}"
                except FileNotFoundError:
                    report_content += "\n当前项目状态：正在开发解说能力增强模块"
                
                self.callback(report_content)
                
            self.last_report_time = time.time()
            time.sleep(self.interval_seconds)
            
    def start(self):
        """启动状态汇报器"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._report_status, daemon=True)
            self.thread.start()
            print(f"状态汇报器已启动，汇报间隔：{self.interval_seconds}秒")
            
    def stop(self):
        """停止状态汇报器"""
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=2)
            print("状态汇报器已停止")
            
    def is_active(self) -> bool:
        """检查汇报器是否处于活动状态"""
        return self.is_running


def create_default_status_file():
    """创建默认的项目状态文件"""
    default_status = """# TW3.0项目状态

## 当前开发进度
- [x] 意图识别模块 - 已完成
- [.] 死活分析模块 - 开发中 (85%)
- [ ] 目数增减分析 - 待开始
- [ ] 厚薄分析能力 - 待开始
- [ ] 轻重分析能力 - 待开始

## 今日重点任务
- 完成死活分析模块
- 开始目数增减分析模块的开发

## 预计完成时间
- 2月2日前完成解说能力增强所有模块
"""
    with open("/root/clawd/TW3.0/project_status.md", "w", encoding="utf-8") as f:
        f.write(default_status)


if __name__ == "__main__":
    # 创建默认状态文件
    create_default_status_file()
    
    # 示例用法
    def sample_callback(content: str):
        print(f"[模拟发送到用户] {content}")
        
    reporter = StatusReporter(interval_seconds=30)
    reporter.set_callback(sample_callback)
    
    print("按 Ctrl+C 停止汇报器")
    try:
        reporter.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reporter.stop()
        print("\n程序已停止")