import os
import time
import asyncio
import psutil
import logging
import json
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CARRASCO - %(levelname)s - %(message)s')
logger = logging.getLogger("CARRASCO")

class CarrascoGuard:
    """
    CARRASCO GUARD - O Watchdog de Darwinismo do Império Mutante.
    Monitora VRAM e lucratividade. Purga processos ineficientes se
    gaps de arbitragem não forem encontrados.
    """
    def __init__(self, glitch_threshold=0.015, timeout=5):
        self.glitch_threshold = glitch_threshold
        self.timeout = timeout
        self.last_glitch_time = time.time()
        self.running = True
        self.vram_available = False
        
        try:
            import pynvml
            pynvml.nvmlInit()
            self.vram_available = True
            logger.info("NVIDIA VRAM monitoring enabled via pynvml.")
        except Exception:
            logger.warning("NVIDIA VRAM monitoring not available. Falling back to CPU/RAM only.")

    def get_vram_usage(self) -> List[Dict[str, Any]]:
        if not self.vram_available:
            return []
        
        try:
            import pynvml
            devices = []
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                devices.append({
                    "index": i,
                    "total": info.total,
                    "free": info.free,
                    "used": info.used,
                    "processes": [{"pid": p.pid, "used": p.usedGpuMemory} for p in processes]
                })
            return devices
        except Exception as e:
            logger.error(f"Error reading VRAM: {e}")
            return []

    def purge_inefficient_tasks(self):
        """
        Adapte-se ou morra. 
        Encerra processos que consomem recursos sem gerar lucro (anomalias).
        """
        logger.info("Executando Ciclo de Darwinismo: Purgando tarefas ineficientes...")
        current_pid = os.getpid()
        killed_count = 0
        
        # 1. Purga por CPU > 15%
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'cmdline']):
            try:
                pinfo = proc.info
                if pinfo['pid'] == current_pid:
                    continue
                
                # Proteção para processos vitais do sistema
                cmdline = " ".join(pinfo['cmdline'] or [])
                if any(x in cmdline for x in ['nexus_core.py', 'mag_service.py', 'sshd']):
                    continue
                
                if pinfo['cpu_percent'] > 15.0:
                    logger.warning(f"PURGE: Processo '{pinfo['name']}' (PID: {pinfo['pid']}) consumindo {pinfo['cpu_percent']}% CPU sem retorno.")
                    proc.terminate()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 2. Purga por VRAM (Processos gulosos)
        if self.vram_available:
            vram_data = self.get_vram_usage()
            for device in vram_data:
                for p_info in device['processes']:
                    try:
                        if p_info['pid'] == current_pid: continue
                        
                        proc = psutil.Process(p_info['pid'])
                        cmdline = " ".join(proc.cmdline())
                        if any(x in cmdline for x in ['nexus_core.py', 'mag_service.py']):
                            continue
                            
                        # Limite de 500MB para processos não-essenciais durante o expurgo
                        if p_info['used'] > 500 * 1024 * 1024:
                            logger.warning(f"PURGE: Processo (PID: {p_info['pid']}) ocupando {p_info['used'] / 1024**2:.2f}MB VRAM ineficientemente.")
                            proc.terminate()
                            killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        
        if killed_count > 0:
            logger.info(f"Darwinismo aplicado: {killed_count} processos eliminados.")
        else:
            logger.info("Nenhum processo ineficiente detectado neste ciclo.")

    async def monitor_market(self):
        """
        Monitora o mercado em busca do Gap de Arbitragem > 1.5%.
        Simula a lógica do mag_service para autonomia total.
        """
        import websockets
        url = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
        last_price = None
        
        while self.running:
            try:
                async with websockets.connect(url) as ws:
                    logger.info("CARRASCO conectado ao feed de mercado para monitoramento de lucro.")
                    while self.running:
                        message = await asyncio.wait_for(ws.recv(), timeout=10.0)
                        data = json.loads(message)
                        price = float(data['p'])
                        
                        if last_price:
                            change = abs(price - last_price) / last_price
                            if change > self.glitch_threshold:
                                logger.info(f"GAP DE ARBITRAGEM DETECTADO: {change*100:.2f}%! Resetando timer de Darwinismo.")
                                self.last_glitch_time = time.time()
                        
                        last_price = price
            except Exception as e:
                logger.warning(f"Conexão com feed de mercado interrompida: {e}. Tentando reconectar...")
                await asyncio.sleep(2)

    async def run_logic(self):
        """Loop principal de decisão."""
        while self.running:
            await asyncio.sleep(1)
            time_since_glitch = time.time() - self.last_glitch_time
            
            if time_since_glitch > self.timeout:
                self.purge_inefficient_tasks()
                # Resetamos para evitar purga em massa contínua se o mercado estiver parado
                self.last_glitch_time = time.time()

    async def start(self):
        logger.info("Iniciando Protocolo de Darwinismo Autônomo...")
        await asyncio.gather(
            self.monitor_market(),
            self.run_logic()
        )

if __name__ == "__main__":
    guard = CarrascoGuard()
    try:
        asyncio.run(guard.start())
    except KeyboardInterrupt:
        logger.info("CARRASCO GUARD desativado.")
