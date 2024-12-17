import os
import sys
import time
import psutil
import logging
import threading
from typing import Dict, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    thread_count: int
    response_time: float

class SystemPerformanceTester:
    def __init__(self, log_file: str = "performance_test.log"):
        self.logger = self._setup_logging(log_file)
        
    def _setup_logging(self, log_file: str) -> logging.Logger:
        """Configure logging to file and console"""
        logger = logging.getLogger("PerformanceTester")
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger

    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        process = psutil.Process()
        
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=process.memory_percent(),
            disk_usage_percent=psutil.disk_usage('/').percent,
            thread_count=threading.active_count(),
            response_time=self.measure_response_time()
        )

    def measure_response_time(self) -> float:
        """Measure system response time using a simple operation"""
        start_time = time.time()
        # Perform a basic file operation
        with open("test.txt", "w") as f:
            f.write("test")
        os.remove("test.txt")
        return time.time() - start_time

    def cpu_stress_test(self, duration: int = 10, threads: int = 4) -> Dict:
        """Run CPU stress test for specified duration using multiple threads"""
        self.logger.info(f"Starting CPU stress test with {threads} threads for {duration} seconds")
        
        def cpu_intensive_task():
            end_time = time.time() + duration
            while time.time() < end_time:
                _ = [i * i for i in range(10000)]

        metrics_before = self.get_system_metrics()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(threads)]
            for future in futures:
                future.result()
                
        metrics_after = self.get_system_metrics()
        
        results = {
            "cpu_impact": metrics_after.cpu_percent - metrics_before.cpu_percent,
            "memory_impact": metrics_after.memory_percent - metrics_before.memory_percent,
            "response_time_impact": metrics_after.response_time - metrics_before.response_time
        }
        
        self.logger.info(f"CPU stress test results: {results}")
        return results

    def memory_stress_test(self, size_mb: int = 500) -> Dict:
        """Test memory allocation and deallocation"""
        self.logger.info(f"Starting memory stress test with {size_mb}MB")
        
        metrics_before = self.get_system_metrics()
        
        # Allocate memory
        data = []
        try:
            for _ in range(size_mb):
                data.append(b'0' * (1024 * 1024))  # Allocate 1MB
                time.sleep(0.1)  # Gradual allocation
                
        except MemoryError:
            self.logger.warning("Memory allocation failed - system limit reached")
            
        metrics_during = self.get_system_metrics()
        
        # Clean up
        data = None
        
        metrics_after = self.get_system_metrics()
        
        results = {
            "peak_memory_usage": metrics_during.memory_percent,
            "memory_not_freed": metrics_after.memory_percent - metrics_before.memory_percent,
            "system_response_impact": metrics_during.response_time - metrics_before.response_time
        }
        
        self.logger.info(f"Memory stress test results: {results}")
        return results

    def run_comprehensive_test(self) -> Dict[str, Dict]:
        """Run all performance tests and collect results"""
        self.logger.info("Starting comprehensive system performance test")
        
        results = {
            "baseline_metrics": vars(self.get_system_metrics()),
            "cpu_test": self.cpu_stress_test(),
            "memory_test": self.memory_stress_test()
        }
        
        self.logger.info("Comprehensive test completed")
        return results

def main():
    tester = SystemPerformanceTester()
    results = tester.run_comprehensive_test()
    print("\nTest Results:")
    for test_name, test_results in results.items():
        print(f"\n{test_name}:")
        for metric, value in test_results.items():
            print(f"  {metric}: {value}")

if __name__ == "__main__":
    main()