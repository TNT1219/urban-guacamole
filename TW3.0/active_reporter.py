"""
TW3.0主动汇报程序（改进版）
"""

import time
import threading
from datetime import datetime
import sys
import os

class ActiveReporter:
    def __init__(self, interval_seconds=30):
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.thread = None
        self.start_time = time.time()
        
    def _report_status(self):
        """执行状态汇报"""
        count = 1  # 汇报计数
        
        while self.is_running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # 读取项目状态
                status_content = "正在开发解说能力增强模块"
                try:
                    with open("/root/clawd/TW3.0/project_status.md", "r", encoding="utf-8") as f:
                        status_content = f.read()
                except FileNotFoundError:
                    pass
                
                report_content = f"**项目进展汇报 #{count}**\n"
                report_content += f"时间：{current_time}\n"
                report_content += f"状态：TW3.0开发正常进行中\n"
                report_content += f"详情：\n{status_content}\n"
                
                print(f"ACTIVE_REPORT: {report_content}")
                sys.stdout.flush()  # 确保输出被刷新
                
                count += 1
                time.sleep(self.interval_seconds)
                
            except Exception as e:
                print(f"REPORT_ERROR: {str(e)}")
                time.sleep(self.interval_seconds)
    
    def start(self):
        """启动汇报程序"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._report_status, daemon=True)
            self.thread.start()
            print("ActiveReporter已启动")
    
    def stop(self):
        """停止汇报程序"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
            print("ActiveReporter已停止")

# 全局实例
reporter = None

def start_reporting():
    global reporter
    if reporter is None:
        reporter = ActiveReporter(interval_seconds=30)
        reporter.start()
        return reporter
    else:
        print("汇报程序已在运行")
        return reporter

if __name__ == "__main__":
    print("启动主动汇报程序...")
    reporter = start_reporting()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if reporter:
            reporter.stop()
        print("\n程序已退出")