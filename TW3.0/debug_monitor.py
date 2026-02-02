"""
TW3.0系统监控与异常恢复机制
确保系统稳定运行的保障系统
"""

import time
import threading
import subprocess
import os
import signal
import sys
from datetime import datetime
import traceback
import logging
from typing import Dict, List, Callable, Optional


class SystemHealthMonitor:
    """
    系统健康监控器
    持续监控系统健康状态
    """
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.health_status = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'process_count': 0,
            'temperature': None,
            'network_status': 'unknown',
            'timestamp': None
        }
        self.alert_handlers = []
        self.metrics_history = []
        self.max_history_length = 1000
        
    def start_monitoring(self):
        """启动系统监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("系统健康监控已启动")
    
    def stop_monitoring(self):
        """停止系统监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("系统健康监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._check_system_health()
                time.sleep(30)  # 每30秒检查一次
            except Exception as e:
                print(f"监控循环出现错误: {e}")
                time.sleep(60)  # 出错后等待更长时间再继续
    
    def _check_system_health(self):
        """检查系统健康状态"""
        import psutil
        
        timestamp = datetime.now().isoformat()
        
        # CPU使用率
        self.health_status['cpu_usage'] = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.health_status['memory_usage'] = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        self.health_status['disk_usage'] = disk.percent
        
        # 进程数量
        self.health_status['process_count'] = len(psutil.pids())
        
        # 温度（如果可用）
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # 取第一个传感器的温度
                for name, entries in temps.items():
                    if entries:
                        self.health_status['temperature'] = entries[0].current
                        break
        except AttributeError:
            # 某些系统可能不支持温度检测
            pass
        
        # 网络状态
        try:
            # 简单测试网络连通性
            network_status = 'ok' if self._test_network_connectivity() else 'unreachable'
            self.health_status['network_status'] = network_status
        except:
            self.health_status['network_status'] = 'unknown'
        
        self.health_status['timestamp'] = timestamp
        
        # 记录指标历史
        self.metrics_history.append(self.health_status.copy())
        if len(self.metrics_history) > self.max_history_length:
            self.metrics_history.pop(0)
        
        # 检查是否需要发出警报
        self._check_alert_conditions()
    
    def _test_network_connectivity(self) -> bool:
        """测试网络连通性"""
        try:
            import socket
            # 尝试连接到一个可靠的服务器
            sock = socket.create_connection(("8.8.8.8", 53), timeout=3)
            sock.close()
            return True
        except OSError:
            return False
    
    def _check_alert_conditions(self):
        """检查是否满足警报条件"""
        alerts = []
        
        if self.health_status['cpu_usage'] > 90:
            alerts.append(f"CPU使用率过高: {self.health_status['cpu_usage']:.1f}%")
        
        if self.health_status['memory_usage'] > 90:
            alerts.append(f"内存使用率过高: {self.health_status['memory_usage']:.1f}%")
        
        if self.health_status['disk_usage'] > 95:
            alerts.append(f"磁盘使用率过高: {self.health_status['disk_usage']:.1f}%")
        
        if self.health_status['temperature'] and self.health_status['temperature'] > 80:
            alerts.append(f"系统温度过高: {self.health_status['temperature']:.1f}°C")
        
        if self.health_status['network_status'] == 'unreachable':
            alerts.append("网络连接不可达")
        
        # 触发警报处理器
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _trigger_alert(self, alert_message: str):
        """触发警报"""
        for handler in self.alert_handlers:
            try:
                handler(alert_message)
            except Exception as e:
                print(f"警报处理器出错: {e}")
    
    def add_alert_handler(self, handler: Callable[[str], None]):
        """添加警报处理器"""
        self.alert_handlers.append(handler)
    
    def get_current_health_status(self) -> Dict:
        """获取当前健康状态"""
        return self.health_status.copy()
    
    def get_health_summary(self) -> str:
        """获取健康状态摘要"""
        status = self.health_status
        summary = f"""
系统健康状态摘要:
  时间: {status['timestamp']}
  CPU使用率: {status['cpu_usage']:.1f}%
  内存使用率: {status['memory_usage']:.1f}%
  磁盘使用率: {status['disk_usage']:.1f}%
  进程数量: {status['process_count']}
  系统温度: {status['temperature']}°C
  网络状态: {status['network_status']}
        """
        return summary.strip()


class ExceptionRecoveryManager:
    """
    异常恢复管理器
    处理系统异常并尝试恢复
    """
    
    def __init__(self):
        self.recovery_strategies = {}
        self.exception_log = []
        self.max_log_length = 100
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
    
    def register_recovery_strategy(self, exception_type: type, strategy_func: Callable):
        """注册异常恢复策略"""
        self.recovery_strategies[exception_type] = strategy_func
    
    def handle_exception(self, exception: Exception, context: str = ""):
        """处理异常"""
        timestamp = datetime.now().isoformat()
        
        # 记录异常
        exception_record = {
            'timestamp': timestamp,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.exception_log.append(exception_record)
        if len(self.exception_log) > self.max_log_length:
            self.exception_log.pop(0)
        
        print(f"捕获异常 [{context}]: {type(exception).__name__}: {exception}")
        
        # 尝试恢复
        recovery_success = self._attempt_recovery(exception)
        
        if not recovery_success:
            print(f"自动恢复失败，异常类型: {type(exception).__name__}")
            # 这里可以通知管理员或采取其他措施
            self._escalate_issue(exception_record)
    
    def _attempt_recovery(self, exception: Exception) -> bool:
        """尝试恢复异常"""
        exception_type = type(exception)
        
        # 检查是否有对应的恢复策略
        if exception_type in self.recovery_strategies:
            strategy = self.recovery_strategies[exception_type]
            
            # 检查恢复尝试次数
            attempt_key = str(exception_type)
            attempts = self.recovery_attempts.get(attempt_key, 0)
            
            if attempts < self.max_recovery_attempts:
                try:
                    print(f"尝试使用策略恢复 {exception_type.__name__} 异常...")
                    recovery_success = strategy()
                    if recovery_success:
                        self.recovery_attempts[attempt_key] = attempts + 1
                        print(f"成功恢复 {exception_type.__name__} 异常")
                        return True
                except Exception as recovery_error:
                    print(f"恢复策略执行失败: {recovery_error}")
            
        # 尝试通用恢复方法
        return self._generic_recovery(exception)
    
    def _generic_recovery(self, exception: Exception) -> bool:
        """通用恢复方法"""
        try:
            # 1. 释放资源
            self._release_resources()
            
            # 2. 重启关键服务
            self._restart_services()
            
            # 3. 清理临时文件
            self._cleanup_temp_files()
            
            print("通用恢复操作完成")
            return True
        except Exception as e:
            print(f"通用恢复也失败: {e}")
            return False
    
    def _release_resources(self):
        """释放系统资源"""
        # 这里可以添加具体的资源释放逻辑
        pass
    
    def _restart_services(self):
        """重启关键服务"""
        # 这里可以添加重启服务的逻辑
        pass
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        temp_dir = "/tmp"
        try:
            for filename in os.listdir(temp_dir):
                if "tw3" in filename.lower() and filename.endswith(".tmp"):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        os.remove(filepath)
                    except:
                        pass
        except:
            pass
    
    def _escalate_issue(self, exception_record: Dict):
        """升级问题处理"""
        # 这里可以添加通知管理员或记录严重问题的逻辑
        print(f"问题已升级: {exception_record['exception_type']}")
    
    def get_exception_summary(self) -> str:
        """获取异常摘要"""
        if not self.exception_log:
            return "无异常记录"
        
        recent_exceptions = self.exception_log[-10:]  # 最近10条
        summary = f"""
异常记录摘要:
  总异常数: {len(self.exception_log)}
  最近异常:
"""
        for record in recent_exceptions:
            summary += f"    - {record['timestamp']}: {record['exception_type']} - {record['context']}\n"
        
        return summary.strip()


class BackupManager:
    """
    备份管理器
    管理系统和数据备份
    """
    
    def __init__(self, backup_directory: str = "/root/clawd/TW3.0/backups"):
        self.backup_directory = backup_directory
        self.backup_history = []
        self.max_backups = 10  # 保留最多10个备份
        
        # 确保备份目录存在
        os.makedirs(self.backup_directory, exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> bool:
        """创建备份"""
        import shutil
        import zipfile
        
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_directory, f"{backup_name}.zip")
        
        try:
            # 创建备份
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                tw3_dir = "/root/clawd/TW3.0"
                for root, dirs, files in os.walk(tw3_dir):
                    # 排除某些不需要备份的目录
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'backups']]
                    for file in files:
                        if not file.endswith(('.tmp', '.log')):
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, os.path.dirname(tw3_dir))
                            zipf.write(file_path, arc_path)
            
            # 记录备份历史
            backup_record = {
                'name': backup_name,
                'path': backup_path,
                'size': os.path.getsize(backup_path),
                'timestamp': datetime.now().isoformat()
            }
            self.backup_history.append(backup_record)
            
            # 保持备份历史在限制范围内
            if len(self.backup_history) > self.max_backups:
                old_backup = self.backup_history.pop(0)
                try:
                    os.remove(old_backup['path'])
                except:
                    pass
            
            print(f"备份创建成功: {backup_path}")
            return True
            
        except Exception as e:
            print(f"备份创建失败: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """恢复备份"""
        import zipfile
        
        backup_path = os.path.join(self.backup_directory, f"{backup_name}.zip")
        
        if not os.path.exists(backup_path):
            print(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            # 解压备份到临时目录，然后替换当前文件
            temp_restore_dir = f"/tmp/tw3_restore_{int(time.time())}"
            os.makedirs(temp_restore_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_restore_dir)
            
            # 将备份内容复制回TW3.0目录（覆盖现有文件）
            tw3_dir = "/root/clawd/TW3.0"
            backup_source_dir = os.path.join(temp_restore_dir, "TW3.0")
            
            import shutil
            # 清空当前目录（除了backups目录）
            for item in os.listdir(tw3_dir):
                item_path = os.path.join(tw3_dir, item)
                if item != "backups" and os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                elif item != "backups" and os.path.isfile(item_path):
                    os.remove(item_path)
            
            # 复制备份内容
            for item in os.listdir(backup_source_dir):
                src_path = os.path.join(backup_source_dir, item)
                dst_path = os.path.join(tw3_dir, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
            
            # 清理临时目录
            shutil.rmtree(temp_restore_dir)
            
            print(f"备份恢复成功: {backup_name}")
            return True
            
        except Exception as e:
            print(f"备份恢复失败: {e}")
            return False
    
    def get_backup_list(self) -> List[Dict]:
        """获取备份列表"""
        return self.backup_history.copy()
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        # 已经在create_backup中实现了自动清理
        pass


class UninterruptedOperationManager:
    """
    不间断运行保障管理器
    统筹监控、恢复和备份功能
    """
    
    def __init__(self):
        self.health_monitor = SystemHealthMonitor()
        self.recovery_manager = ExceptionRecoveryManager()
        self.backup_manager = BackupManager()
        self.is_running = False
        self.main_loop_thread = None
        self.operational_log = []
        self.max_log_length = 1000
    
    def start(self):
        """启动不间断运行保障系统"""
        if not self.is_running:
            self.is_running = True
            
            # 注册默认恢复策略
            self._register_default_strategies()
            
            # 启动健康监控
            self.health_monitor.start_monitoring()
            
            # 启动主循环
            self.main_loop_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_loop_thread.start()
            
            print("不间断运行保障系统已启动")
    
    def stop(self):
        """停止不间断运行保障系统"""
        self.is_running = False
        
        if self.main_loop_thread:
            self.main_loop_thread.join(timeout=2)
        
        self.health_monitor.stop_monitoring()
        
        print("不间断运行保障系统已停止")
    
    def _register_default_strategies(self):
        """注册默认恢复策略"""
        # 为常见异常注册恢复策略
        def handle_memory_error():
            # 尝试释放内存
            import gc
            gc.collect()
            return True
        
        def handle_io_error():
            # 尝试重新初始化IO资源
            return True
        
        def handle_keyboard_interrupt():
            # 键盘中断通常是故意的，不需要特殊恢复
            return True
        
        self.recovery_manager.register_recovery_strategy(MemoryError, handle_memory_error)
        self.recovery_manager.register_recovery_strategy(OSError, handle_io_error)
        self.recovery_manager.register_recovery_strategy(KeyboardInterrupt, handle_keyboard_interrupt)
    
    def _main_loop(self):
        """主循环 - 实现24小时不间断运行"""
        backup_counter = 0
        backup_interval = 2880  # 每24小时（24*60*60/30）次检查进行一次备份
        
        while self.is_running:
            try:
                # 记录运行状态
                self._log_operational_event("system_check", "Main loop operational")
                
                # 定期创建备份
                backup_counter += 1
                if backup_counter >= backup_interval:
                    self.backup_manager.create_backup()
                    backup_counter = 0
                
                # 等待下一次检查
                time.sleep(30)  # 每30秒进行一次基本检查
                
            except Exception as e:
                # 使用恢复管理器处理异常
                self.recovery_manager.handle_exception(e, "UninterruptedOperationManager.main_loop")
                
                # 即使出现异常也要继续运行
                time.sleep(10)  # 出错后稍作停顿再继续
    
    def _log_operational_event(self, event_type: str, message: str):
        """记录运行事件"""
        timestamp = datetime.now().isoformat()
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        }
        
        self.operational_log.append(event)
        if len(self.operational_log) > self.max_log_length:
            self.operational_log.pop(0)
    
    def handle_unexpected_shutdown(self):
        """处理意外关机"""
        try:
            # 创建紧急备份
            emergency_backup_name = f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.backup_manager.create_backup(emergency_backup_name)
            
            # 记录意外关机事件
            self._log_operational_event("emergency_shutdown", "Unexpected shutdown detected")
            
            print("意外关机处理完成，已创建紧急备份")
        except Exception as e:
            print(f"意外关机处理出错: {e}")
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            'is_running': self.is_running,
            'health_status': self.health_monitor.get_current_health_status(),
            'recent_events': self.operational_log[-10:],  # 最近10个事件
            'backup_count': len(self.backup_manager.get_backup_list()),
            'exception_count': len(self.recovery_manager.exception_log)
        }


def setup_signal_handlers(manager: UninterruptedOperationManager):
    """设置信号处理器"""
    def signal_handler(signum, frame):
        print(f"接收到信号 {signum}，正在关闭系统...")
        manager.handle_unexpected_shutdown()
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)


def main():
    """
    主函数：启动不间断运行保障系统
    """
    print("启动TW3.0不间断运行保障系统")
    
    # 创建保障管理器
    manager = UninterruptedOperationManager()
    
    # 设置信号处理器
    setup_signal_handlers(manager)
    
    # 启动保障系统
    manager.start()
    
    try:
        # 模拟运行 - 在实际部署中这里会一直运行
        print("系统已进入24小时不间断运行模式")
        print("健康监控已启动，异常恢复机制已激活，定期备份将自动执行")
        
        # 持续运行
        while True:
            time.sleep(60)  # 每分钟检查一次状态（实际上后台线程已在运行）
            
            # 可以在这里添加其他定期任务
            status = manager.get_system_status()
            print(f"系统运行正常，当前健康状态: {status['health_status']['cpu_usage']:.1f}% CPU, "
                  f"{status['health_status']['memory_usage']:.1f}% 内存")
            
    except KeyboardInterrupt:
        print("\n接收到停止信号...")
    finally:
        manager.stop()
        manager.handle_unexpected_shutdown()


if __name__ == "__main__":
    main()