import psutil
import asyncio
import time
from typing import Dict, Any, List
import logging

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TELEMETRY")

class TelemetrySystem:
    """
    Sistema de Telemetria e Monitoramento do Império Mutante.
    Agora com suporte a métricas de GPU (RTX 3050/3070).
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.nvml_initialized = False
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
                logger.info("NVML Inicializado. Monitoramento de GPU ativado.")
            except Exception as e:
                logger.warning(f"Falha ao inicializar NVML: {e}")

    def get_gpu_stats(self) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas das GPUs disponíveis.
        """
        gpu_stats = []
        if self.nvml_initialized:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    
                    gpu_stats.append({
                        "id": i,
                        "name": name,
                        "utilization": util.gpu,
                        "memory_utilization": util.memory,
                        "memory_used": mem.used,
                        "memory_total": mem.total,
                        "temperature": temp
                    })
            except Exception as e:
                logger.debug(f"Erro ao coletar stats de GPU: {e}")
        return gpu_stats

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Coleta estatísticas de hardware do nó local.
        """
        stats = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "cpu_cores": psutil.cpu_count(),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent
            },
            "uptime": time.time() - self.start_time,
            "gpu": self.get_gpu_stats(),
            "supra_codex_sync": "synced"
        }
        return stats

    async def get_node_heartbeat(self, node_name: str) -> Dict[str, Any]:
        """
        Gera um heartbeat para o nó.
        """
        stats = self.get_system_stats()
        return {
            "node": node_name,
            "status": "online",
            "timestamp": time.time(),
            "stats": stats,
            "supra_codex_sync": "synced"
        }

    async def monitor_gemini_performance(self, latency: float, tokens: int = 0) -> Dict[str, Any]:
        """
        Monitora a performance das chamadas ao Gemini.
        """
        return {
            "latency": latency,
            "tokens_estimate": tokens,
            "efficiency": tokens / latency if latency > 0 else 0
        }

    def __del__(self):
        if hasattr(self, 'nvml_initialized') and self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass

# Exemplo de uso
if __name__ == "__main__":
    async def main():
        tel = TelemetrySystem()
        while True:
            stats = tel.get_system_stats()
            print(f"Stats: {stats}")
            await asyncio.sleep(5)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
