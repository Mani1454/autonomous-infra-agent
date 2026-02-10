import psutil
from typing import Dict, List, Any

class SystemMonitor:
    """
    A robust system monitoring utility for fetching real-time infrastructure metrics.

    This class provides methods to collect telemetry data including CPU load,
    memory utilization, disk occupancy, and high-resource process identification.
    It is designed to handle permission errors and missing process information
    gracefully.

    Attributes:
        None
    """

    def __init__(self) -> None:
        """Initializes the SystemMonitor instance."""
        pass

    def get_cpu_usage(self) -> float:
        """
        Fetches the current system-wide CPU utilization percentage.

        Returns:
            float: The CPU usage as a percentage (0.0 to 100.0).
        """
        # interval=1 is used to calculate the utilization over a 1-second period
        return psutil.cpu_percent(interval=1)

    def get_memory_info(self) -> Dict[str, float]:
        """
        Collects detailed virtual memory statistics.

        Returns:
            Dict[str, float]: A dictionary containing:
                - 'used_gb': Amount of memory currently in use in Gigabytes.
                - 'available_gb': Amount of memory available for new processes in Gigabytes.
                - 'percent': Total memory utilization percentage.
        """
        virtual_memory = psutil.virtual_memory()
        bytes_to_gb_factor = 1024 ** 3
        
        return {
            "used_gb": round(virtual_memory.used / bytes_to_gb_factor, 2),
            "available_gb": round(virtual_memory.available / bytes_to_gb_factor, 2),
            "percent": virtual_memory.percent
        }

    def get_disk_usage(self) -> float:
        """
        Calculates the disk usage percentage of the root directory.

        Returns:
            float: Disk occupancy percentage.
        """
        root_disk_usage = psutil.disk_usage('/')
        return root_disk_usage.percent

    def get_top_processes(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Identifies the top N processes with the highest CPU consumption.
        Strictly normalizes CPU usage and filters idle processes.

        Args:
            limit (int): The number of top processes to return. Defaults to 3.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a process
                with keys 'PID', 'Name', and 'CPU %'.
        """
        process_list = []
        cpu_count = psutil.cpu_count() or 1
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                cpu_p = proc.info['cpu_percent']

                # 1. Skip System Idle Process immediately
                if pid == 0:
                    continue
                
                # 2. Double safety check for 'System Idle Process'
                if name == 'System Idle Process':
                    continue

                if cpu_p is None:
                    continue

                # 3. Calculate normalized CPU usage
                normalized_cpu = float(cpu_p / cpu_count)
                
                process_list.append({
                    'PID': int(pid),
                    'Name': str(name),
                    'CPU %': round(normalized_cpu, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 4. Sort by 'CPU %' in Descending order
        sorted_processes = sorted(
            process_list, 
            key=lambda p: p['CPU %'], 
            reverse=True
        )
        
        # 5. Return top N
        return sorted_processes[:limit]

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Aggregates all system telemetry into a single structured report.

        Returns:
            Dict[str, Any]: A nested dictionary containing CPU, memory, 
                disk metrics, and a list of top-consuming processes.
        """
        return {
            "cpu_usage_percent": self.get_cpu_usage(),
            "memory": self.get_memory_info(),
            "disk_usage_percent": self.get_disk_usage(),
            "top_processes": self.get_top_processes(limit=3)
        }

if __name__ == "__main__":
    # Internal validation and testing
    monitor = SystemMonitor()
    print("Capturing System Metrics...")
    print(monitor.get_system_metrics())
