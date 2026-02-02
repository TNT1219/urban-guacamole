"""
TW3.0性能优化系统
多线程处理，提高分析速度
"""

import threading
import multiprocessing
import time
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Callable, Any
import functools
import psutil
import gc
from datetime import datetime


class PerformanceOptimizer:
    """
    性能优化器
    通过多线程和缓存优化系统性能
    """
    
    def __init__(self):
        self.task_queue = queue.Queue()
        self.result_cache = {}
        self.cache_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=self._get_optimal_workers())
        self.stats = {
            'tasks_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_processing_time': 0.0,
            'peak_memory_usage': 0.0
        }
        self.stats_lock = threading.Lock()
    
    def _get_optimal_workers(self) -> int:
        """获取最优工作线程数"""
        # 使用CPU核心数作为基础，但不超过8个
        cpu_cores = multiprocessing.cpu_count()
        return min(cpu_cores, 8)
    
    def optimize_with_cache(self, cache_key: str = None):
        """装饰器：添加缓存优化"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 如果提供了缓存键，尝试从缓存获取
                if cache_key:
                    full_key = f"{cache_key}:{hash(str(args) + str(kwargs))}"
                    with self.cache_lock:
                        if full_key in self.result_cache:
                            self.stats['cache_hits'] += 1
                            return self.result_cache[full_key]
                
                # 执行原始函数
                start_time = time.time()
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time
                
                # 更新统计信息
                with self.stats_lock:
                    self.stats['tasks_processed'] += 1
                    if cache_key:
                        self.stats['cache_misses'] += 1
                    # 更新平均处理时间
                    old_avg = self.stats['avg_processing_time']
                    total_tasks = self.stats['tasks_processed']
                    self.stats['avg_processing_time'] = (
                        (old_avg * (total_tasks - 1) + processing_time) / total_tasks
                    )
                
                # 如果提供了缓存键，保存到缓存
                if cache_key:
                    with self.cache_lock:
                        self.result_cache[full_key] = result
                        # 限制缓存大小
                        if len(self.result_cache) > 1000:
                            # 删除最早的一半缓存项
                            keys = list(self.result_cache.keys())
                            for k in keys[:len(keys)//2]:
                                del self.result_cache[k]
                
                return result
            return wrapper
        return decorator
    
    def parallel_execute(self, tasks: List[Callable], max_workers: int = None) -> List[Any]:
        """并行执行多个任务"""
        if max_workers is None:
            max_workers = self._get_optimal_workers()
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(task): i for i, task in enumerate(tasks)
            }
            
            # 按原始顺序收集结果
            temp_results = [None] * len(tasks)
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    temp_results[index] = future.result()
                except Exception as e:
                    temp_results[index] = e
            
            results = temp_results
        
        execution_time = time.time() - start_time
        
        # 更新统计
        with self.stats_lock:
            self.stats['tasks_processed'] += len(tasks)
            old_avg = self.stats['avg_processing_time']
            total_tasks = self.stats['tasks_processed']
            self.stats['avg_processing_time'] = (
                (old_avg * (total_tasks - len(tasks)) + execution_time) / total_tasks
            )
        
        return results
    
    def async_execute(self, func: Callable, *args, **kwargs) -> Any:
        """异步执行函数"""
        return self.executor.submit(func, *args, **kwargs)
    
    def clear_cache(self):
        """清空缓存"""
        with self.cache_lock:
            self.result_cache.clear()
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        with self.stats_lock:
            stats_copy = self.stats.copy()
        
        # 添加内存使用情况
        stats_copy['current_memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        stats_copy['cache_size'] = len(self.result_cache)
        
        return stats_copy
    
    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)
        self.clear_cache()


class MultiThreadedProcessor:
    """
    多线程处理器
    专门用于处理大量围棋分析任务
    """
    
    def __init__(self, num_threads: int = None):
        if num_threads is None:
            num_threads = min(multiprocessing.cpu_count(), 6)
        
        self.num_threads = num_threads
        self.workers = []
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.shutdown_event = threading.Event()
        self.stats = {
            'processed_count': 0,
            'error_count': 0,
            'avg_processing_time': 0.0,
            'active_threads': 0
        }
        self.stats_lock = threading.Lock()
    
    def start_workers(self):
        """启动工作线程"""
        for i in range(self.num_threads):
            worker = threading.Thread(target=self._worker, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
        
        self.stats['active_threads'] = self.num_threads
    
    def _worker(self, worker_id: int):
        """工作线程函数"""
        while not self.shutdown_event.is_set():
            try:
                # 获取任务
                task_data = self.task_queue.get(timeout=1)
                if task_data is None:  # 结束信号
                    break
                
                # 处理任务
                start_time = time.time()
                try:
                    result = self._process_single_task(task_data)
                    self.result_queue.put(('success', result))
                    
                    # 更新统计
                    with self.stats_lock:
                        self.stats['processed_count'] += 1
                        processing_time = time.time() - start_time
                        old_avg = self.stats['avg_processing_time']
                        processed = self.stats['processed_count']
                        self.stats['avg_processing_time'] = (
                            (old_avg * (processed - 1) + processing_time) / processed
                        )
                
                except Exception as e:
                    self.result_queue.put(('error', str(e)))
                    with self.stats_lock:
                        self.stats['error_count'] += 1
                
                finally:
                    self.task_queue.task_done()
            
            except queue.Empty:
                continue
    
    def _process_single_task(self, task_data: Dict) -> Any:
        """处理单个任务 - 这里是围棋分析的核心逻辑"""
        # 根据任务类型执行不同的分析
        task_type = task_data.get('type', 'unknown')
        
        if task_type == 'position_analysis':
            return self._analyze_position(task_data)
        elif task_type == 'pattern_match':
            return self._match_pattern(task_data)
        elif task_type == 'life_death':
            return self._analyze_life_death(task_data)
        else:
            raise ValueError(f"未知任务类型: {task_type}")
    
    def _analyze_position(self, task_data: Dict) -> Dict:
        """分析局面 - 模拟实现"""
        import random
        time.sleep(0.1)  # 模拟处理时间
        
        # 返回模拟的分析结果
        return {
            'win_rate': random.uniform(40, 60),
            'best_moves': [f"{chr(65+random.randint(0,18))}{random.randint(1,19)}" for _ in range(3)],
            'intention': 'normal play',
            'processing_time': 0.1
        }
    
    def _match_pattern(self, task_data: Dict) -> Dict:
        """匹配模式 - 模拟实现"""
        import random
        time.sleep(0.05)  # 模拟处理时间
        
        return {
            'pattern_matched': random.choice([True, False]),
            'pattern_type': 'corner_extension',
            'confidence': random.uniform(0.6, 0.95)
        }
    
    def _analyze_life_death(self, task_data: Dict) -> Dict:
        """分析死活 - 模拟实现"""
        import random
        time.sleep(0.15)  # 模拟处理时间
        
        return {
            'alive': random.choice([True, False]),
            'eyes': random.randint(0, 3),
            'libs': random.randint(0, 10),
            'analysis': 'complex position'
        }
    
    def submit_task(self, task_data: Dict):
        """提交任务"""
        self.task_queue.put(task_data)
    
    def get_results(self, timeout: float = None) -> List[tuple]:
        """获取结果"""
        results = []
        try:
            while True:
                result = self.result_queue.get(timeout=timeout or 0.1)
                results.append(result)
        except queue.Empty:
            pass
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.stats_lock:
            return self.stats.copy()
    
    def shutdown(self):
        """关闭处理器"""
        self.shutdown_event.set()
        
        # 发送结束信号给所有工作线程
        for _ in range(self.num_threads):
            self.task_queue.put(None)
        
        # 等待所有线程结束
        for worker in self.workers:
            worker.join(timeout=2)
        
        self.stats['active_threads'] = 0


class AlgorithmOptimizer:
    """
    算法优化器
    优化围棋分析算法的效率
    """
    
    def __init__(self):
        self.optimization_techniques = {
            'memoization': self._apply_memoization,
            'early_exit': self._apply_early_exit,
            'pruning': self._apply_pruning,
            'parallel_search': self._apply_parallel_search
        }
    
    def optimize_analysis_speed(self, analysis_func: Callable) -> Callable:
        """优化分析速度"""
        @functools.wraps(analysis_func)
        def optimized_func(*args, **kwargs):
            # 在这里应用各种优化技术
            start_time = time.time()
            
            # 应用剪枝优化
            if 'board_state' in kwargs:
                if self._should_prune(kwargs['board_state']):
                    return self._quick_estimate(kwargs['board_state'])
            
            # 执行原始分析
            result = analysis_func(*args, **kwargs)
            
            # 记录性能
            elapsed = time.time() - start_time
            
            # 如果处理时间过长，可以考虑提前返回近似结果
            if elapsed > 2.0:  # 如果超过2秒
                result['performance_warning'] = f"Analysis took {elapsed:.2f}s"
            
            return result
        
        return optimized_func
    
    def _should_prune(self, board_state: Dict) -> bool:
        """判断是否应该剪枝"""
        # 如果棋局已经明显偏向某一方，可以简化分析
        if 'win_rate_estimate' in board_state:
            wr = board_state['win_rate_estimate']
            return abs(wr - 50) > 40  # 如果胜率差距超过40%，简化分析
        
        return False
    
    def _quick_estimate(self, board_state: Dict) -> Dict:
        """快速估计"""
        import random
        return {
            'win_rate': board_state.get('win_rate_estimate', 50),
            'best_moves': [f"{chr(65+random.randint(0,18))}{random.randint(1,19)}" for _ in range(2)],
            'confidence': 0.7,
            'quick_estimate': True
        }
    
    def _apply_memoization(self, func: Callable) -> Callable:
        """应用记忆化"""
        cache = {}
        
        @functools.wraps(func)
        def memoized_func(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        
        memoized_func.cache_clear = lambda: cache.clear()
        return memoized_func
    
    def _apply_early_exit(self, func: Callable) -> Callable:
        """应用提前退出优化"""
        @functools.wraps(func)
        def early_exit_func(*args, **kwargs):
            # 可以在这里添加提前退出的逻辑
            return func(*args, **kwargs)
        
        return early_exit_func
    
    def _apply_pruning(self, func: Callable) -> Callable:
        """应用剪枝优化"""
        @functools.wraps(func)
        def pruned_func(*args, **kwargs):
            # 可以在这里添加剪枝逻辑
            return func(*args, **kwargs)
        
        return pruned_func
    
    def _apply_parallel_search(self, func: Callable) -> Callable:
        """应用并行搜索优化"""
        @functools.wraps(func)
        def parallel_func(*args, **kwargs):
            # 可以在这里添加并行搜索逻辑
            return func(*args, **kwargs)
        
        return parallel_func


def benchmark_performance():
    """性能基准测试"""
    print("开始性能基准测试...")
    
    # 创建优化器
    optimizer = PerformanceOptimizer()
    processor = MultiThreadedProcessor(num_threads=4)
    algorithm_optimizer = AlgorithmOptimizer()
    
    # 启动处理器
    processor.start_workers()
    
    # 创建一些测试任务
    test_tasks = []
    for i in range(20):
        task_type = ['position_analysis', 'pattern_match', 'life_death'][i % 3]
        test_tasks.append({
            'type': task_type,
            'task_id': i,
            'board_state': {'position': f"test_pos_{i}"}
        })
    
    print(f"提交 {len(test_tasks)} 个测试任务...")
    
    # 提交任务
    start_time = time.time()
    for task in test_tasks:
        processor.submit_task(task)
    
    # 等待处理完成
    while processor.task_queue.unfinished_tasks > 0:
        time.sleep(0.1)
    
    # 收集结果
    results = processor.get_results()
    total_time = time.time() - start_time
    
    print(f"处理完成！用时: {total_time:.2f}秒")
    print(f"成功处理: {len([r for r in results if r[0] == 'success'])} 个任务")
    print(f"错误: {len([r for r in results if r[0] == 'error'])} 个任务")
    
    # 显示统计
    stats = processor.get_stats()
    print(f"处理统计: {stats}")
    
    # 测试缓存优化
    @optimizer.optimize_with_cache(cache_key="benchmark_test")
    def cached_function(x):
        time.sleep(0.1)  # 模拟耗时操作
        return x * 2
    
    print("\n测试缓存优化...")
    start_time = time.time()
    
    # 第一次调用
    for i in range(5):
        result = cached_function(i)
    
    # 重复调用（应该从缓存获取）
    for i in range(5):
        result = cached_function(i)
    
    cache_time = time.time() - start_time
    print(f"缓存测试完成，用时: {cache_time:.2f}秒")
    
    # 显示最终统计
    final_stats = optimizer.get_stats()
    print(f"优化器统计: {final_stats}")
    
    # 清理资源
    processor.shutdown()
    optimizer.cleanup()
    
    print("性能基准测试完成！")


def main():
    """
    主函数：演示性能优化系统
    """
    print("启动TW3.0性能优化系统")
    
    # 运行基准测试
    benchmark_performance()
    
    print("\n性能优化系统演示完成")
    
    # 创建优化器实例供系统使用
    performance_optimizer = PerformanceOptimizer()
    multi_processor = MultiThreadedProcessor()
    algorithm_optimizer = AlgorithmOptimizer()
    
    # 启动多线程处理器
    multi_processor.start_workers()
    
    print(f"系统已准备好使用优化功能:")
    print(f"- 性能优化器已初始化")
    print(f"- 多线程处理器已启动 {multi_processor.num_threads} 个工作线程")
    print(f"- 算法优化器已准备就绪")
    
    # 返回优化器实例以便在其他模块中使用
    return performance_optimizer, multi_processor, algorithm_optimizer


if __name__ == "__main__":
    main()