"""
NEXUS CORE v3.2.0 - O Cérebro Central do Império Mutante
Fusão de Trindade 2.5, MagEngine, LMArenaBridge, Zenith, Shadow Oracle e Alquimia.
Roteamento Adaptativo com Auto-Otimização Hiper-Recursiva.

ARQUITETURA:
├── NEXUS CORE (Cérebro Central)
│   ├── NodeManager (Gerenciamento de Nós com Telemetria Ativa)
│   ├── TelemetrySystem (Monitoramento em Tempo Real)
│   ├── ZenithEngine (Extração Recursiva / LMArenaBridge)
│   ├── ShadowOracle (Intelligence de Mercado)
│   ├── AlquimiaProcessor (Destilação e Gestão de Conhecimento)
│   ├── OptimizationLoop (Auto-Otimização)
│   └── CommandExecutor (Comandos Soberanos)
├── Nós de Processamento
│   ├── SPECTRUM (Eficiência/Linux/RTX 3050)
│   ├── NEURO-TOXIN (Agressividade/Ryzen/RTX 3070)
│   └── GLITCH (Resiliência/Fallback)
└── Protocolo Néctar Supremo v2.0
"""

import os
import asyncio
import json
import uuid
import logging
import time
import psutil
import aiosqlite
from typing import Dict, Optional, Literal, Union, Any, List, Callable
from enum import Enum
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, HTTPException, Response, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai
import httpx

# =============================================================================
# CONFIGURAÇÃO E INICIALIZAÇÃO
# =============================================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - NEXUS-CORE - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NEXUS-CORE")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_PATH = "imperio_mutante.db"

# =============================================================================
# PERSISTÊNCIA E NOTIFICAÇÕES
# =============================================================================

class PersistenceManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT,
                    node TEXT,
                    created_at TIMESTAMP,
                    result TEXT,
                    error TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mag_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    type TEXT,
                    relevance TEXT,
                    timestamp TIMESTAMP,
                    data TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS nectar_harvest (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    nectar_score REAL,
                    content_hash TEXT,
                    entities TEXT,
                    timestamp TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS optimization_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle INTEGER,
                    metric TEXT,
                    value REAL,
                    recommendation TEXT,
                    applied INTEGER,
                    timestamp TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("Persistência SQLite v3.2.0 inicializada.")

    async def save_task(self, task_id: str, status: str, node: str = None, result: Any = None, error: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO tasks (task_id, status, node, created_at, result, error) VALUES (?, ?, ?, ?, ?, ?)",
                (task_id, status, node, datetime.now().isoformat(), json.dumps(result) if result else None, error)
            )
            await db.commit()

    async def get_recent_tasks(self, limit: int = 10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def save_mag_event(self, source: str, event_type: str, relevance: str, data: Any):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO mag_history (source, type, relevance, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                (source, event_type, relevance, datetime.now().isoformat(), json.dumps(data))
            )
            await db.commit()

    async def save_nectar_harvest(self, url: str, nectar_score: float, content_hash: str, entities: Dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO nectar_harvest (url, nectar_score, content_hash, entities, timestamp) VALUES (?, ?, ?, ?, ?)",
                (url, nectar_score, content_hash, json.dumps(entities), datetime.now().isoformat())
            )
            await db.commit()

    async def save_optimization_log(self, cycle: int, metric: str, value: float, recommendation: str, applied: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO optimization_log (cycle, metric, value, recommendation, applied, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (cycle, metric, value, recommendation, applied, datetime.now().isoformat())
            )
            await db.commit()

class TelegramNotifier:
    def __init__(self, token: str, default_chat_id: str):
        self.token = token
        self.default_chat_id = default_chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    async def send_message(self, text: str, chat_id: str = None):
        target_chat = chat_id or self.default_chat_id
        if not self.token or not target_chat:
            logger.warning("Telegram Notifier não configurado corretamente.")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.api_url, json={
                    "chat_id": target_chat,
                    "text": text,
                    "parse_mode": "HTML"
                })
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Telegram: {e}")

# =============================================================================
# SISTEMA DE TELEMETRIA
# =============================================================================

class TelemetrySystem:
    def __init__(self):
        self.start_time = time.time()
        self.cycle_count = 0

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {"percent": psutil.disk_usage('/').percent},
            "uptime": time.time() - self.start_time,
            "timestamp": time.time(),
            "version": "3.2.0"
        }

    async def monitor_gemini_performance(self, latency: float, tokens: int = 0) -> Dict[str, Any]:
        return {
            "latency": latency,
            "tokens_estimate": tokens,
            "efficiency": tokens / latency if latency > 0 else 0
        }

# =============================================================================
# MODELOS E ENUMS
# =============================================================================

class NodeType(str, Enum):
    SPECTRUM = "SPECTRUM"
    NEURO_TOXIN = "NEURO-TOXIN"
    GLITCH = "GLITCH"

class IngressRequest(BaseModel):
    content: Union[str, Dict[str, Any]]
    priority: Optional[str] = None
    metadata: Optional[Dict] = Field(default_factory=dict)

class TaskResponse(BaseModel):
    task_id: str
    status: str
    node: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    node: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    nectar: Optional[List[Dict[str, Any]]] = None
    telemetry: Optional[Dict[str, Any]] = None

class CommandRequest(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = Field(default_factory=dict)

class HarvestRequest(BaseModel):
    sources: Optional[List[str]] = None
    recursive: bool = True
    max_depth: int = 3

class DistillRequest(BaseModel):
    raw_data: List[Dict[str, Any]]
    source: str = "nexus_core"

class SynthesizeRequest(BaseModel):
    nectar_ids: Optional[List[str]] = None
    raw_items: Optional[List[Dict[str, Any]]] = None

@dataclass
class NodeMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    last_latency: float = 0.0
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0

# =============================================================================
# NODE MANAGER
# =============================================================================

class NodeManager:
    def __init__(self, config_path: str = "supra_codex.json"):
        self.config_path = config_path
        self.nodes: Dict[str, Dict] = {}
        self.metrics: Dict[str, NodeMetrics] = {}
        self.settings: Dict[str, Any] = {
            "latency_threshold": 2.5,
            "health_check_interval": 30,
            "circuit_breaker_threshold": 5
        }
        self.load_config()
        
    def load_config(self) -> None:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.nodes = config.get("nodes", {})
                    self.settings.update(config.get("settings", {}))
                    for nid in self.nodes:
                        if nid not in self.metrics: self.metrics[nid] = NodeMetrics()
                logger.info(f"Supra-Codex v{config.get('meta', {}).get('version')} carregado.")
            else:
                self._set_defaults()
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            self._set_defaults()
    
    def _set_defaults(self):
        self.nodes = {
            "SPECTRUM": {"name": "ESPECTRO", "endpoint": "http://localhost:8001", "status": "unknown"},
            "NEURO-TOXIN": {"name": "NEURO-TOXINA", "endpoint": "http://localhost:8002", "status": "unknown"},
            "GLITCH": {"name": "GLITCH", "endpoint": "http://localhost:8003", "status": "unknown"}
        }
        for nid in self.nodes: self.metrics[nid] = NodeMetrics()

    async def start_health_checks(self, client: httpx.AsyncClient):
        self._client = client
        asyncio.create_task(self._health_loop())
    
    async def _health_loop(self):
        while True:
            await asyncio.gather(*[self.check_node(nid) for nid in self.nodes])
            await asyncio.sleep(self.settings.get("health_check_interval", 30))
    
    async def check_node(self, node_id: str):
        config = self.nodes[node_id]
        try:
            start = time.time()
            resp = await self._client.get(f"{config['endpoint']}/health", timeout=3.0)
            latency = (time.time() - start) * 1000
            if resp.status_code == 200:
                config["status"] = "online"
                config["latency_ms"] = latency
                self._update_metrics(node_id, latency, True)
            else:
                config["status"] = "degraded"
                self._update_metrics(node_id, latency, False)
        except Exception:
            config["status"] = "offline"
            self._update_metrics(node_id, 0, False)

    def _update_metrics(self, node_id: str, latency: float, success: bool):
        m = self.metrics[node_id]
        m.total_requests += 1
        if success:
            m.successful_requests += 1
            m.total_latency += latency
            m.last_latency = latency
            m.consecutive_failures = 0
        else:
            m.failed_requests += 1
            m.consecutive_failures += 1
            if m.consecutive_failures >= self.settings["circuit_breaker_threshold"]:
                self.nodes[node_id]["status"] = "circuit_open"

    def get_best_node(self, node_type: NodeType) -> Dict:
        node = self.nodes.get(node_type.value, {})
        if node.get("status") == "online": return node
        for n in self.nodes.values():
            if n.get("status") == "online": return n
        return self.nodes.get("GLITCH", {})

    def get_all_telemetry(self) -> Dict[str, Any]:
        return {
            nid: {
                "status": self.nodes[nid].get("status"),
                "metrics": {
                    "success_rate": self.metrics[nid].success_rate,
                    "avg_latency": self.metrics[nid].total_latency / self.metrics[nid].successful_requests if self.metrics[nid].successful_requests > 0 else 0,
                    "total_requests": self.metrics[nid].total_requests
                }
            } for nid in self.nodes
        }

# =============================================================================
# ZENITH ENGINE INTEGRATION
# =============================================================================

class ZenithBridge:
    """Ponte entre NEXUS CORE e ZenithAutomation."""
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_sources = [
            "https://lmsys.org/blog/",
            "https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard",
            "https://huggingface.co/blog"
        ]
    
    async def harvest_nectar(self, sources: List[str] = None, recursive: bool = True) -> Dict[str, Any]:
        """Coleta Néctar usando o módulo Zenith."""
        try:
            response = await self.client.post(
                "http://localhost:8001/distill",
                json={
                    "items": [{"url": s, "type": "source"} for s in (sources or self.base_sources)],
                    "source": "zenith_bridge"
                },
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            logger.warning(f"Zenith Bridge não disponível: {e}")
            return {"status": "fallback", "collected": 0}

# =============================================================================
# SHADOW ORACLE INTEGRATION
# =============================================================================

class ShadowBridge:
    """Ponte entre NEXUS CORE e ShadowMarketOracle."""
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def get_market_intel(self) -> Dict[str, Any]:
        """Coleta inteligência de mercado."""
        try:
            response = await self.client.get(
                "http://localhost:8005/market/sentiment",
                timeout=10.0
            )
            return response.json()
        except Exception as e:
            logger.warning(f"Shadow Bridge não disponível: {e}")
            return {"status": "offline", "sentiment": "unknown"}

# =============================================================================
# ROTEAMENTO E COMANDOS
# =============================================================================

async def classify_with_gemini(content: Any) -> NodeType:
    if not GEMINI_API_KEY: return NodeType.GLITCH
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"[SISTEMA: NEXUS CORE v3.2.0] Classifique: SPECTRUM (automação), NEURO-TOXIN (heavy AI) ou GLITCH (edge/fallback). Conteúdo: {str(content)[:1000]}"
        response = await asyncio.to_thread(model.generate_content, prompt)
        res = response.text.upper()
        if "NEURO" in res: return NodeType.NEURO_TOXIN
        if "SPECTRUM" in res: return NodeType.SPECTRUM
        return NodeType.GLITCH
    except: return NodeType.GLITCH

async def process_task(task_id: str, content: Any, priority: Optional[str]):
    tasks[task_id]["status"] = "processing"
    await persistence.save_task(task_id, "processing")
    
    node_type = await classify_with_gemini(content)
    node = node_manager.get_best_node(node_type)
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{node['endpoint']}/process", json={"task_id": task_id, "content": content})
            result = resp.json()
            tasks[task_id].update({"status": "completed", "result": result, "node": node["name"]})
            await persistence.save_task(task_id, "completed", node["name"], result)
            
            if priority == "HIGH":
                await notifier.send_message(f"✅ <b>Tarefa Concluída</b>\nID: {task_id[:8]}\nNó: {node['name']}")

    except Exception as e:
        tasks[task_id].update({"status": "failed", "error": str(e)})
        await persistence.save_task(task_id, "failed", error=str(e))

# =============================================================================
# API ENDPOINTS
# =============================================================================

tasks: Dict[str, Dict] = {}
node_manager = NodeManager()
telemetry = TelemetrySystem()
persistence = PersistenceManager(DB_PATH)
notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
zenith_bridge = None
shadow_bridge = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global zenith_bridge, shadow_bridge
    
    async with httpx.AsyncClient() as client:
        app.state.client = client
        app.state.engine = None
        
        try:
            from zenith_automation import ZenithEngine
            app.state.zenith = ZenithEngine()
        except ImportError:
            logger.warning("Zenith Automation não disponível.")
            app.state.zenith = None
        
        zenith_bridge = ZenithBridge(client)
        shadow_bridge = ShadowBridge(client)
        
        await node_manager.start_health_checks(client)
        await persistence.init_db()
        
        logger.info("🚀 NEXUS CORE v3.2.0 - Protocolo Néctar Supremo v2.0 ATIVADO")
        yield
        
        if app.state.zenith:
            await app.state.zenith.close()
        logger.info("NEXUS CORE encerrado.")

app = FastAPI(title="NEXUS CORE v3.2.0 - Império Mutante", lifespan=lifespan)

@app.post("/ingress", response_model=TaskResponse, status_code=202)
async def ingress(request: IngressRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "queued", "created_at": time.time(), "metadata": request.metadata}
    await persistence.save_task(task_id, "queued")
    background_tasks.add_task(process_task, task_id, request.content, request.priority)
    return TaskResponse(task_id=task_id, status="queued")

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    if task_id in tasks:
        return {**tasks[task_id], "task_id": task_id}
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                d = dict(row)
                return {
                    "task_id": d["task_id"],
                    "status": d["status"],
                    "node": d["node"],
                    "result": json.loads(d["result"]) if d["result"] else None,
                    "error": d["error"]
                }
    
    raise HTTPException(status_code=404)

@app.get("/history")
async def get_history(limit: int = 10):
    return await persistence.get_recent_tasks(limit)

@app.post("/oracle/notification")
async def oracle_notification(request: Request):
    data = await request.json()
    message = data.get("message")
    if message:
        await notifier.send_message(message)
        if data.get("type") == "MAG_EVENT" or data.get("type") == "ZENITH_EVENT":
            await persistence.save_mag_event(
                source=data.get("source", "unknown"),
                event_type=data.get("event_type", "alert"),
                relevance=data.get("relevance", "medium"),
                data=data.get("data", {})
            )
        return {"status": "sent"}
    return {"status": "ignored"}

@app.get("/health")
async def health():
    return {
        "status": "operational",
        "version": "3.2.0",
        "nodes": node_manager.nodes,
        "telemetry": telemetry.get_system_stats()
    }

# =============================================================================
# COMMAND ENDPOINTS
# =============================================================================

@app.post("/command")
async def command(request: CommandRequest):
    cmd = request.command.upper()
    
    if cmd == "/SOBERANIA":
        return {
            "status": "success",
            "system": telemetry.get_system_stats(),
            "nodes": node_manager.get_all_telemetry()
        }
    
    if cmd == "/MUTAR":
        node_manager.load_config()
        return {"status": "success", "message": "Supra-Codex mutado."}
    
    if cmd == "/APOGEU":
        node_manager.settings["low_latency_mode"] = True
        node_manager.settings["max_concurrent_tasks"] = 1000
        return {"status": "success", "message": "Modo APOGEU ativado. Performance máxima."}
    
    if cmd == "/CARRASCO":
        purged = len(tasks)
        tasks.clear()
        return {"status": "success", "message": f"Ciclo CARRASCO executado. {purged} processos purgados."}
    
    if cmd == "/EVOLUIR":
        try:
            response = await app.state.client.post("http://localhost:8004/evolve", timeout=60.0)
            if response.status_code == 200:
                result = response.json()
                telemetry.cycle_count += 1
                return {
                    "status": "success",
                    "message": "Ciclo de evolução executado.",
                    "result": result
                }
        except Exception as e:
            logger.warning(f"Optimization Engine não disponível: {e}")
        return {
            "status": "partial",
            "message": "Evolution Engine não conectado. Telemetria atualizada.",
            "metrics": telemetry.get_system_stats()
        }
    
    if cmd == "/SINTETIZAR":
        raw_data = request.args.get("raw_items", [])
        try:
            response = await app.state.client.post(
                "http://localhost:8001/synthesize",
                json={"raw_items": raw_data},
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                await notifier.send_message(f"🍯 <b>Síntese de Néctar Concluída</b>\n{result.get('synthesis', '')[:500]}")
                return result
        except Exception as e:
            logger.warning(f"Alquimia não disponível: {e}")
        
        return {
            "status": "partial",
            "message": "Alquimia não disponível. use /HARVEST primeiro."
        }
    
    return {"status": "error", "message": "Comando desconhecido."}

# =============================================================================
# NÉCTAR HARVESTING ENDPOINTS
# =============================================================================

@app.post("/harvest")
async def harvest(request: HarvestRequest):
    """Endpoint para coleta de Néctar via Zenith."""
    sources = request.sources or zenith_bridge.base_sources if zenith_bridge else []
    
    if app.state.zenith:
        try:
            result = await app.state.zenith.harvest_nectar(sources)
            
            for nectar in result.get("top_nectar", []):
                await persistence.save_nectar_harvest(
                    url=nectar.get("url", ""),
                    nectar_score=nectar.get("nectar_score", 0),
                    content_hash=nectar.get("content_hash", ""),
                    entities=nectar.get("entities", {})
                )
            
            await notifier.send_message(f"🍯 <b>Néctar Colhido</b>\nTotal: {result.get('total_collected', 0)}\nTop: {len(result.get('top_nectar', []))} fontes")
            
            return result
        except Exception as e:
            logger.error(f"Erro no harvesting: {e}")
    
    return {"status": "fallback", "message": "Zenith não disponível."}

@app.post("/distill")
async def distill(request: DistillRequest):
    """Endpoint para destilação de dados via Alquimia."""
    try:
        response = await app.state.client.post(
            "http://localhost:8001/distill",
            json={"items": request.raw_data, "source": request.source},
            timeout=30.0
        )
        return response.json()
    except Exception as e:
        logger.warning(f"Alquimia não disponível: {e}")
        return {"status": "fallback", "processed": len(request.raw_data)}

@app.get("/nectar/history")
async def get_nectar_history(limit: int = 50):
    """Retorna histórico de Néctar colhido."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM nectar_harvest ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return {"history": [dict(row) for row in rows], "count": len(rows)}

@app.get("/optimization/log")
async def get_optimization_log(limit: int = 50):
    """Retorna histórico de otimizações."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM optimization_log ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return {"log": [dict(row) for row in rows], "count": len(rows)}

# =============================================================================
# MARKET INTEL ENDPOINT
# =============================================================================

@app.get("/market/intel")
async def get_market_intel():
    """Retorna inteligência de mercado do Shadow Oracle."""
    return await shadow_bridge.get_market_intel() if shadow_bridge else {"status": "offline"}

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)