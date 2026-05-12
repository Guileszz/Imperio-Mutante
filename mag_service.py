"""
Módulo de Arbitragem Global (MAG)
Conecta a feeds de dados via WebSockets e classifica tráfego para o Roteador Trindade 2.5.

Classificação:
- HF_DATA (NEURO-TOXINA): Dados de alta frequência (trades frequentes)
- TREND_DATA (ESPECTRO): Dados de tendência (resumos temporais)
- GLITCH: Anomalias de mercado > 1.5%
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum

import websockets
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MAG")


class DataType(str, Enum):
    """Tipos de dados para classificação no Trindade 2.5."""
    HF_DATA = "HF_DATA"       # Dados de alta frequência -> NEURO-TOXINA
    TREND_DATA = "TREND_DATA" # Dados de tendência -> ESPECTRO
    GLITCH = "GLITCH"         # Anomalias -> GLITCH


@dataclass
class PriceSnapshot:
    """Snapshot de preço para detecção de anomalias."""
    price: float
    timestamp: float
    quantity: float = 0.0
    is_buyer_maker: bool = False


@dataclass
class TradingStats:
    """Estatísticas de trading para classificação heurística."""
    trade_count: int = 0
    last_trade_time: float = 0.0
    prices: List[float] = field(default_factory=list)
    volumes: List[float] = field(default_factory=list)
    anomalies_detected: int = 0
    last_anomaly_time: float = 0.0


class GlobalArbitrationModule:
    """
    Módulo de Arbitragem Global (MAG).
    
    Conecta a feeds WebSocket de exchanges (Binance como boilerplate),
    processa dados e os classifica antes de enviar ao Roteador Trindade 2.5.
    """
    
    # Configurações
    WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
    ROUTER_URL = "http://localhost:8000"
    INGRESS_ENDPOINT = "/ingress"
    
    # Parâmetros de detecção
    GLITCH_THRESHOLD = 0.015  # 1.5% de variação
    HF_TRADE_THRESHOLD = 5    # Trades por segundo para classificar como HF
    TREND_INTERVAL = 10       # Segundos para agregar dados de tendência
    MAX_RECONNECT_DELAY = 60  # Máximo delay de reconexão (exponential backoff)
    BASE_RECONNECT_DELAY = 1   # Delay base de reconexão
    STATS_RESET_INTERVAL = 60 # Intervalo para resetar estatísticas
    
    def __init__(self, router_url: Optional[str] = None):
        self.router_url = router_url or self.ROUTER_URL
        self.websocket_url = self.WEBSOCKET_URL
        self.running = False
        self.reconnect_delay = self.BASE_RECONNECT_DELAY
        
        # Estado interno
        self.last_price: Optional[PriceSnapshot] = None
        self.stats = TradingStats()
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Estatísticas de运营
        self.total_trades = 0
        self.total_payloads_sent = 0
        self.start_time: Optional[float] = None
    
    async def initialize(self):
        """Inicializa o módulo e conexões."""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.start_time = time.time()
        logger.info(f"MAG inicializado. Router URL: {self.router_url}")
    
    async def cleanup(self):
        """Limpa recursos."""
        self.running = False
        if self.http_client:
            await self.http_client.aclose()
        logger.info("MAG encerrado.")
    
    async def send_to_router(
        self, 
        content: Union[str, Dict[str, Any]], 
        priority_hint: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Envia dados para o Roteador Trindade 2.5 via endpoint /ingress.
        
        Args:
            content: Payload a ser enviado
            priority_hint: Hint de prioridade para classificação
            metadata: Metadados adicionais
            
        Returns:
            task_id se bem-sucedido, None caso contrário
        """
        try:
            payload = {
                "content": content,
                "priority": priority_hint,
                "metadata": metadata or {}
            }
            
            response = await self.http_client.post(
                f"{self.router_url}{self.INGRESS_ENDPOINT}",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 202:
                result = response.json()
                task_id = result.get("task_id")
                logger.debug(f"Payload enviado. Task ID: {task_id}")
                self.total_payloads_sent += 1
                return task_id
            else:
                logger.warning(f"Erro ao enviar payload: {response.status_code}")
                
        except httpx.TimeoutException:
            logger.warning("Timeout ao enviar para o roteador")
        except httpx.ConnectError:
            logger.warning("Falha de conexão com o roteador")
        except Exception as e:
            logger.error(f"Erro ao enviar payload: {e}")
        
        return None
    
    def detect_glitch(self, current_price: float, last_price: Optional[float]) -> bool:
        """
        Detecta anomalias de mercado (Glitch-Trigger).
        
        Args:
            current_price: Preço atual
            last_price: Preço anterior
            
        Returns:
            True se anomalia detectada (> 1.5% de variação)
        """
        if last_price is None or last_price == 0:
            return False
        
        price_change = abs(current_price - last_price) / last_price
        return price_change > self.GLITCH_THRESHOLD
    
    def classify_trade(self, time_diff: float) -> DataType:
        """
        Classifica o tipo de dado baseado em heurísticas.
        
        Args:
            time_diff: Tempo desde o último trade (segundos)
            
        Returns:
            Tipo de dado classificado
        """
        if time_diff < 0:
            return DataType.TREND_DATA
        
        trades_per_second = 1 / time_diff if time_diff > 0 else float('inf')
        
        if trades_per_second >= self.HF_TRADE_THRESHOLD:
            return DataType.HF_DATA
        
        return DataType.TREND_DATA
    
    async def process_trade(self, trade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Processa dados de trade e classifica para envio.
        
        Args:
            trade_data: Dados brutos do WebSocket
            
        Returns:
            Payload formatado para o roteador
        """
        try:
            current_price = float(trade_data.get("p", 0))
            quantity = float(trade_data.get("q", 0))
            trade_time = float(trade_data.get("T", 0)) / 1000  # ms to seconds
            is_buyer_maker = trade_data.get("m", False)
            
            current_snapshot = PriceSnapshot(
                price=current_price,
                timestamp=trade_time,
                quantity=quantity,
                is_buyer_maker=is_buyer_maker
            )
            
            # Atualizar estatísticas
            self.total_trades += 1
            time_diff = trade_time - self.stats.last_trade_time if self.stats.last_trade_time > 0 else 0
            self.stats.trade_count += 1
            self.stats.last_trade_time = trade_time
            
            # Adicionar ao histórico para agregação e estatísticas móveis
            self.stats.prices.append(current_price)
            self.stats.volumes.append(quantity)
            
            # Detectar Glitch
            is_glitch = self.detect_glitch(current_price, self.last_price.price if self.last_price else None)
            if is_glitch:
                self.stats.anomalies_detected += 1
                self.stats.last_anomaly_time = trade_time
            
            # Classificar tipo de dado
            data_type = self.classify_trade(time_diff) if not is_glitch else DataType.GLITCH
            
            # Construir payload estruturado
            payload = {
                "protocolo": "MAG",
                "data_type": data_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "price": current_price,
                "quantity": quantity,
                "is_buyer_maker": is_buyer_maker,
                "anomaly_detected": is_glitch,
                "glitch_threshold": self.GLITCH_THRESHOLD,
                "trade_stats": {
                    "total_trades": self.total_trades,
                    "trade_count_session": self.stats.trade_count,
                    "anomalies_detected": self.stats.anomalies_detected,
                    "avg_price": sum(self.stats.prices) / len(self.stats.prices) if self.stats.prices else 0,
                    "total_volume": sum(self.stats.volumes),
                },
                "source": "binance",
                "pair": "BTCUSDT",
                "stream": "aggTrade"
            }
            
            # Determinar hint de prioridade baseado na classificação
            if data_type == DataType.HF_DATA:
                priority_hint = "NEURO-TOXINA"
            elif data_type == DataType.GLITCH:
                priority_hint = "GLITCH"
            else:
                priority_hint = "ESPECTRO"
            
            self.last_price = current_snapshot
            
            return {
                "payload": payload,
                "priority_hint": priority_hint
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar trade: {e}")
            return None
    
    async def aggregate_trend_data_direct(self, prices: List[float], volumes: List[float]) -> Dict[str, Any]:
        """
        Agrega dados de tendência a partir de listas de preços e volumes.
        
        Returns:
            Payload com dados agregados
        """
        if not prices:
            return {}
        
        trend_payload = {
            "protocolo": "MAG",
            "data_type": DataType.TREND_DATA.value,
            "timestamp": datetime.utcnow().isoformat(),
            "aggregated_stats": {
                "samples": len(prices),
                "price_min": min(prices),
                "price_max": max(prices),
                "price_avg": sum(prices) / len(prices),
                "price_std": self._calculate_std(prices),
                "volume_total": sum(volumes),
                "anomalies_detected": self.stats.anomalies_detected,
            },
            "source": "binance",
            "pair": "BTCUSDT",
            "aggregation_period": f"{self.TREND_INTERVAL}s"
        }
        
        return trend_payload
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calcula desvio padrão."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    async def websocket_reconnect(self) -> bool:
        """
        Reconexão com exponential backoff.
        
        Returns:
            True se reconectado com sucesso
        """
        delay = self.BASE_RECONNECT_DELAY
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Tentativa de reconexão {attempt + 1}/{max_attempts}")
                async with websockets.connect(self.websocket_url) as ws:
                    self.reconnect_delay = self.BASE_RECONNECT_DELAY
                    logger.info("Reconectado com sucesso")
                    return True
            except Exception as e:
                logger.warning(f"Falha na reconexão: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.MAX_RECONNECT_DELAY)
        
        logger.error("Máximo de tentativas de reconexão excedido")
        return False
    
    async def run(self):
        """
        Loop principal do MAG.
        Conecta ao WebSocket, processa trades e envia para o roteador.
        """
        await self.initialize()
        self.running = True
        
        trend_aggregation_task: Optional[asyncio.Task] = None
        
        async def aggregate_trends():
            """Task periódica para agregar dados de tendência."""
            while self.running:
                await asyncio.sleep(self.TREND_INTERVAL)
                if self.running and self.stats.prices:
                    # Capturar dados atuais e limpar para evitar perda durante o envio
                    current_prices = self.stats.prices[:]
                    current_volumes = self.stats.volumes[:]
                    self.stats.prices.clear()
                    self.stats.volumes.clear()
                    
                    trend_data = await self.aggregate_trend_data_direct(current_prices, current_volumes)
                    if trend_data:
                        await self.send_to_router(
                            content=trend_data,
                            priority_hint="ESPECTRO",
                            metadata={"source": "mag_trends", "type": "aggregation"}
                        )

        while self.running:
            try:
                if not trend_aggregation_task or trend_aggregation_task.done():
                    trend_aggregation_task = asyncio.create_task(aggregate_trends())
                
                async with websockets.connect(self.websocket_url) as ws:
                    logger.info(f"Conectado ao stream: {self.websocket_url}")
                    self.reconnect_delay = self.BASE_RECONNECT_DELAY
                    
                    while self.running:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                            trade_data = json.loads(message)
                            
                            processed = await self.process_trade(trade_data)
                            if processed:
                                await self.send_to_router(
                                    content=processed["payload"],
                                    priority_hint=processed["priority_hint"],
                                    metadata={
                                        "source": "mag_realtime",
                                        "data_type": processed["payload"]["data_type"]
                                    }
                                )
                                
                        except asyncio.TimeoutError:
                            # Heartbeat/keepalive
                            logger.debug("Heartbeat - conexão ativa")
                            continue
                            
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Conexão WebSocket fechada: {e}")
            except Exception as e:
                logger.error(f"Erro na conexão WebSocket: {e}")
            
            # Tentar reconectar
            if self.running:
                if not await self.websocket_reconnect():
                    break
        
        # Cleanup
        if trend_aggregation_task:
            trend_aggregation_task.cancel()
        
        await self.cleanup()
    
    async def test_connectivity(self) -> bool:
        """
        Testa conectividade com o roteador.
        
        Returns:
            True se o roteador estiver acessível
        """
        try:
            response = await self.http_client.get(
                f"{self.router_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do módulo.
        
        Returns:
            Dicionário com estatísticas e estado atual
        """
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "running": self.running,
            "uptime_seconds": uptime,
            "total_trades": self.total_trades,
            "total_payloads_sent": self.total_payloads_sent,
            "anomalies_detected": self.stats.anomalies_detected,
            "websocket_url": self.websocket_url,
            "router_url": self.router_url,
            "last_reconnect_delay": self.reconnect_delay
        }


async def main():
    """Ponto de entrada principal."""
    mag = GlobalArbitrationModule()
    
    # Testar conectividade com o roteador
    router_reachable = await mag.test_connectivity()
    if not router_reachable:
        logger.warning(
            "Roteador não está acessível. "
            "Iniciando MAG mesmo assim (modems podem iniciar antes do roteador)."
        )
    
    try:
        await mag.run()
    except KeyboardInterrupt:
        logger.info("Interrupção manual recebida")
    finally:
        status = mag.get_status()
        logger.info(f"Status final do MAG: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())