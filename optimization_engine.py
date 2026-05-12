"""
OPTIMIZATION ENGINE v1.0 - Loop de Auto-Otimização Hiper-Recursiva.
Coleta telemetria → Envia métricas ao Gemini → Recebe ajustes → Aplica no Supra-Codex.

ARQUITETURA:
├── OptimizationLoop (Loop principal)
│   ├── TelemetryCollector (Coleta métricas)
│   ├── GeminiAdvisor (Análise e recomendações)
│   ├── CodexMutator (Aplica mudanças no Supra-Codex)
│   └── EvolutionTracker (Rastreia evolução do sistema)
└── Protocolo Darwinismo Sistêmico
"""

import asyncio
import json
import time
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_AVAILABLE = bool(os.getenv("GEMINI_API_KEY"))
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - OPTIMIZATION - %(levelname)s - %(message)s')
logger = logging.getLogger("OPTIMIZATION-ENGINE")


# =============================================================================
# ENUMS E DATACLASSES
# =============================================================================

class OptimizationPhase(str, Enum):
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    MUTATION = "mutation"
    VALIDATION = "validation"
    COMPLETE = "complete"


@dataclass
class TelemetrySnapshot:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    latency_avg: float
    success_rate: float
    nectar_collected: int
    errors_count: int
    active_nodes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationRecommendation:
    phase: str
    action: str
    parameter: str
    current_value: Any
    recommended_value: Any
    reason: str
    expected_impact: str


# =============================================================================
# TELEMETRY COLLECTOR
# =============================================================================

class TelemetryCollector:
    """
    Coleta telemetria de todos os nós e componentes do sistema.
    """
    
    def __init__(self, config_path: str = "supra_codex.json"):
        self.config_path = config_path
        self.history: List[TelemetrySnapshot] = []
        self.max_history = 100
    
    def collect_local(self) -> Dict[str, Any]:
        """Coleta métricas do nó local."""
        import psutil
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime": time.time()
        }
    
    async def collect_node_health(self, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """Coleta saúde de um nó específico via HTTP."""
        import httpx
        
        endpoint = node_config.get("endpoint", "")
        if not endpoint:
            return {"status": "unknown", "node": node_config.get("name", "unknown")}
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                start = time.time()
                resp = await client.get(f"{endpoint}/health")
                latency = time.time() - start
                
                return {
                    "node": node_config.get("name", "unknown"),
                    "status": "online" if resp.status_code == 200 else "degraded",
                    "latency_ms": latency * 1000,
                    "response": resp.json() if resp.status_code == 200 else {}
                }
        except Exception as e:
            return {
                "node": node_config.get("name", "unknown"),
                "status": "offline",
                "error": str(e)
            }
    
    async def collect_all(self) -> TelemetrySnapshot:
        """Coleta telemetria completa de todos os nós."""
        local = self.collect_local()
        
        nodes = self._load_nodes()
        node_health = await asyncio.gather(*[self.collect_node_health(n) for n in nodes.values()])
        
        active_nodes = [n["node"] for n in node_health if n.get("status") == "online"]
        
        snapshot = TelemetrySnapshot(
            timestamp=local["timestamp"],
            cpu_percent=local["cpu_percent"],
            memory_percent=local["memory_percent"],
            disk_percent=local["disk_percent"],
            latency_avg=sum(n.get("latency_ms", 0) for n in node_health) / max(len(node_health), 1),
            success_rate=self._calculate_success_rate(node_health),
            nectar_collected=self._get_nectar_count(),
            errors_count=sum(1 for n in node_health if n.get("status") == "offline"),
            active_nodes=active_nodes
        )
        
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return snapshot
    
    def _load_nodes(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("nodes", {})
        except:
            return {}
    
    def _calculate_success_rate(self, node_health: List[Dict]) -> float:
        if not node_health:
            return 1.0
        online = sum(1 for n in node_health if n.get("status") == "online")
        return online / len(node_health)
    
    def _get_nectar_count(self) -> int:
        try:
            with open("supra_codex.json", "r") as f:
                return 0
        except:
            return 0
    
    def get_trend(self, metric: str, window: int = 10) -> List[float]:
        """Retorna tendência de uma métrica ao longo do tempo."""
        values = []
        for snap in self.history[-window:]:
            val = getattr(snap, metric, None)
            if val is not None:
                values.append(float(val))
        return values


# =============================================================================
# GEMINI ADVISOR
# =============================================================================

class GeminiAdvisor:
    """
    Analisa telemetria e gera recomendações de otimização via Gemini.
    """
    
    def __init__(self):
        self.model = None
        if GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini Advisor inicializado.")
            except Exception as e:
                logger.warning(f"G非得ini não disponível: {e}")
    
    async def analyze_and_recommend(self, snapshot: TelemetrySnapshot, history: List[TelemetrySnapshot]) -> List[OptimizationRecommendation]:
        """Analisa telemetria e retorna recomendações."""
        if not self.model:
            return self._default_recommendations(snapshot)
        
        try:
            prompt = self._build_analysis_prompt(snapshot, history)
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            recommendations = self._parse_recommendations(response.text)
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro na análise Gemini: {e}")
            return self._default_recommendations(snapshot)
    
    def _build_analysis_prompt(self, snapshot: TelemetrySnapshot, history: List[TelemetrySnapshot]) -> str:
        recent_metrics = {
            "cpu": [s.cpu_percent for s in history[-5:]],
            "memory": [s.memory_percent for s in history[-5:]],
            "latency": [s.latency_avg for s in history[-5:]],
            "success_rate": [s.success_rate for s in history[-5:]]
        }
        
        prompt = f"""[SISTEMA: OPTIMIZATION ENGINE]
Analise a telemetria atual e gere recomendações de otimização para o Supra-Codex.

TELEMETRIA ATUAL:
- CPU: {snapshot.cpu_percent:.1f}%
- Memory: {snapshot.memory_percent:.1f}%
- Disk: {snapshot.disk_percent:.1f}%
- Latência Média: {snapshot.latency_avg:.1f}ms
- Taxa de Sucesso: {snapshot.success_rate:.1%}
- Nós Ativos: {', '.join(snapshot.active_nodes)}
- Erros: {snapshot.errors_count}

TENDÊNCIAS RECENTES (últimos 5 ciclos):
{json.dumps(recent_metrics, indent=2)}

_CONFIGURAÇÕES ATUAIS DO SUPRA-CODEX (exemplo):_
- latency_threshold: 2.5
- health_check_interval: 30
- max_concurrent_tasks: 500
- optimization_flags: {{"low_latency_mode": true, "aggressive_gc": true}}

GERE recomendações JSON no formato:
[
  {{"phase": "performance|reliability|efficiency", "action": "increase|decrease|enable|disable", "parameter": "nome_param", "current_value": valor, "recommended_value": novo_valor, "reason": "justificativa", "expected_impact": "impacto_esperado"}}
]

Retorne APENAS o JSON array."""
        
        return prompt
    
    def _parse_recommendations(self, text: str) -> List[OptimizationRecommendation]:
        try:
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text.strip())
            
            recommendations = []
            for item in data:
                if isinstance(item, dict):
                    recommendations.append(OptimizationRecommendation(
                        phase=item.get("phase", "performance"),
                        action=item.get("action", "maintain"),
                        parameter=item.get("parameter", ""),
                        current_value=item.get("current_value"),
                        recommended_value=item.get("recommended_value"),
                        reason=item.get("reason", ""),
                        expected_impact=item.get("expected_impact", "")
                    ))
            
            return recommendations
            
        except json.JSONDecodeError:
            logger.warning("Falha ao parsear recomendações. Usando defaults.")
            return []
    
    def _default_recommendations(self, snapshot: TelemetrySnapshot) -> List[OptimizationRecommendation]:
        recommendations = []
        
        if snapshot.cpu_percent > 80:
            recommendations.append(OptimizationRecommendation(
                phase="performance",
                action="decrease",
                parameter="max_concurrent_tasks",
                current_value=500,
                recommended_value=300,
                reason="CPU muito alto - reduzir concorrência",
                expected_impact="Redução de uso de CPU em ~15%"
            ))
        
        if snapshot.latency_avg > 2000:
            recommendations.append(OptimizationRecommendation(
                phase="reliability",
                action="decrease",
                parameter="health_check_interval",
                current_value=30,
                recommended_value=15,
                reason="Latência alta - aumentar frequência de health checks",
                expected_impact="Detecção mais rápida de problemas"
            ))
        
        if snapshot.success_rate < 0.9:
            recommendations.append(OptimizationRecommendation(
                phase="efficiency",
                action="enable",
                parameter="fallback_mode",
                current_value=False,
                recommended_value=True,
                reason="Taxa de sucesso baixa - ativar modo fallback",
                expected_impact="Melhor resiliência do sistema"
            ))
        
        return recommendations


# =============================================================================
# CODEX MUTATOR
# =============================================================================

class CodexMutator:
    """
    Aplica mudanças recomendadas no Supra-Codex.
    Mantém backup e validação das mudanças.
    """
    
    def __init__(self, config_path: str = "supra_codex.json"):
        self.config_path = config_path
        self.backup_path = config_path + ".backup"
        self.mutation_log: List[Dict[str, Any]] = []
    
    async def apply_recommendations(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Aplica as recomendações no Supra-Codex."""
        if not recommendations:
            return {"applied": 0, "status": "no_changes"}
        
        self._backup_config()
        
        with open(self.config_path, "r") as f:
            config = json.load(f)
        
        applied = 0
        for rec in recommendations:
            if self._apply_single_change(config, rec):
                applied += 1
                self.mutation_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "recommendation": asdict(rec),
                    "status": "applied"
                })
        
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Mutação aplicada: {applied}/{len(recommendations)} mudanças no Supra-Codex.")
        
        return {"applied": applied, "total": len(recommendations), "config_updated": True}
    
    def _apply_single_change(self, config: Dict, recommendation: OptimizationRecommendation) -> bool:
        parameter = recommendation.parameter
        new_value = recommendation.recommended_value
        
        if "." in parameter:
            parts = parameter.split(".")
            current = config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = new_value
            return True
        elif parameter in config.get("settings", {}):
            config["settings"][parameter] = new_value
            return True
        elif parameter in config:
            config[parameter] = new_value
            return True
        
        return False
    
    def _backup_config(self):
        try:
            with open(self.config_path, "r") as src:
                with open(self.backup_path, "w") as dst:
                    dst.write(src.read())
        except Exception as e:
            logger.warning(f"Falha ao criar backup: {e}")
    
    async def rollback(self) -> bool:
        """Restaura o último backup."""
        try:
            with open(self.backup_path, "r") as src:
                with open(self.config_path, "w") as dst:
                    dst.write(src.read())
            logger.info("Rollback realizado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Falha no rollback: {e}")
            return False
    
    def get_mutation_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.mutation_log[-limit:]


# =============================================================================
# EVOLUTION TRACKER
# =============================================================================

class EvolutionTracker:
    """
    Rastreia a evolução do sistema ao longo do tempo.
    Mantém histórico de métricas e otimizações.
    """
    
    def __init__(self):
        self.evolution_log: List[Dict[str, Any]] = []
        self.cycle_count = 0
        self.total_mutations = 0
    
    async def record_cycle(self, snapshot: TelemetrySnapshot, recommendations: List[OptimizationRecommendation], applied: int):
        """Registra um ciclo de otimização completo."""
        self.cycle_count += 1
        self.total_mutations += applied
        
        entry = {
            "cycle": self.cycle_count,
            "timestamp": snapshot.timestamp,
            "metrics": snapshot.to_dict(),
            "recommendations_generated": len(recommendations),
            "mutations_applied": applied,
            "cumulative_mutations": self.total_mutations
        }
        
        self.evolution_log.append(entry)
        
        if len(self.evolution_log) > 1000:
            self.evolution_log = self.evolution_log[-500:]
        
        return entry
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo da evolução do sistema."""
        if not self.evolution_log:
            return {"status": "no_data", "cycles": 0}
        
        recent = self.evolution_log[-10:]
        
        avg_cpu = sum(e["metrics"]["cpu_percent"] for e in recent) / len(recent)
        avg_latency = sum(e["metrics"]["latency_avg"] for e in recent) / len(recent)
        
        return {
            "total_cycles": self.cycle_count,
            "total_mutations": self.total_mutations,
            "recent_avg_cpu": avg_cpu,
            "recent_avg_latency": avg_latency,
            "trend": "improving" if avg_latency < 1000 else "stable"
        }


# =============================================================================
# OPTIMIZATION LOOP (MAIN ORCHESTRATOR)
# =============================================================================

class OptimizationLoop:
    """
    Loop principal de auto-otimização hiper-recursiva.
    Executa: Telemetria → Análise → Mutação → Validação
    """
    
    def __init__(self, interval: int = 3600):
        self.interval = interval
        self.running = False
        self.telemetry = TelemetryCollector()
        self.advisor = GeminiAdvisor()
        self.mutator = CodexMutator()
        self.tracker = EvolutionTracker()
        
        logger.info(f"OptimizationLoop inicializado (intervalo: {interval}s)")
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """Executa um ciclo completo de otimização."""
        logger.info("=" * 50)
        logger.info("INICIANDO CICLO DE OTIMIZAÇÃO")
        logger.info("=" * 50)
        
        phase = OptimizationPhase.COLLECTION
        snapshot = await self.telemetry.collect_all()
        logger.info(f"[{phase.value}] Telemetria coletada: CPU={snapshot.cpu_percent:.1f}%, Mem={snapshot.memory_percent:.1f}%")
        
        phase = OptimizationPhase.ANALYSIS
        recommendations = await self.advisor.analyze_and_recommend(snapshot, self.telemetry.history)
        logger.info(f"[{phase.value}] {len(recommendations)} recomendações geradas")
        
        for rec in recommendations[:3]:
            logger.info(f"  → {rec.parameter}: {rec.current_value} → {rec.recommended_value} ({rec.reason})")
        
        phase = OptimizationPhase.MUTATION
        result = await self.mutator.apply_recommendations(recommendations)
        logger.info(f"[{phase.value}] {result['applied']} mutações aplicadas")
        
        phase = OptimizationPhase.VALIDATION
        await self.tracker.record_cycle(snapshot, recommendations, result["applied"])
        logger.info(f"[{phase.value}] Ciclo completo. Resumo: {self.tracker.get_summary()}")
        
        logger.info("=" * 50)
        logger.info("CICLO DE OTIMIZAÇÃO CONCLUÍDO")
        logger.info("=" * 50)
        
        return {
            "phase": phase.value,
            "snapshot": snapshot.to_dict(),
            "recommendations": [asdict(r) for r in recommendations],
            "applied": result,
            "evolution": self.tracker.get_summary()
        }
    
    async def start(self):
        """Inicia o loop de auto-otimização."""
        self.running = True
        logger.info("🚀 LOOP DE AUTO-OTIMIZAÇÃO INICIADO")
        
        while self.running:
            try:
                await self.execute_cycle()
            except Exception as e:
                logger.error(f"Erro no ciclo de otimização: {e}")
            
            for _ in range(self.interval):
                if not self.running:
                    break
                await asyncio.sleep(1)
    
    def stop(self):
        """Para o loop de otimização."""
        self.running = False
        logger.info("⏹️ LOOP DE AUTO-OTIMIZAÇÃO ENCERRADO")


# =============================================================================
# FASTAPI ENDPOINTS
# =============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

loop_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop_instance
    loop_instance = OptimizationLoop(interval=3600)
    yield
    if loop_instance:
        loop_instance.stop()

app = FastAPI(title="Optimization Engine v1.0", lifespan=lifespan)


class TriggerRequest(BaseModel):
    force: bool = False


@app.post("/evolve")
async def trigger_evolution(request: TriggerRequest = None):
    """Dispara um ciclo de auto-otimização."""
    if not loop_instance:
        raise HTTPException(status_code=503, detail="OtimizationLoop não inicializado")
    
    result = await loop_instance.execute_cycle()
    return result


@app.get("/evolution/summary")
async def get_evolution_summary():
    """Retorna resumo da evolução do sistema."""
    if not loop_instance:
        return {"status": "no_data"}
    return loop_instance.tracker.get_summary()


@app.get("/evolution/log")
async def get_evolution_log(limit: int = 20):
    """Retorna histórico de ciclos de otimização."""
    if not loop_instance:
        return {"log": []}
    return {"log": loop_instance.tracker.evolution_log[-limit:]}


@app.get("/recommendations/current")
async def get_current_recommendations():
    """Retorna recomendações atuais baseadas na telemetria mais recente."""
    if not loop_instance:
        return {"recommendations": []}
    
    snapshot = loop_instance.telemetry.collect_local()
    from dataclasses import dataclass
    snapshot = TelemetrySnapshot(**snapshot, latency_avg=0, success_rate=1.0, nectar_collected=0, errors_count=0, active_nodes=[])
    
    recommendations = await loop_instance.advisor.analyze_and_recommend(
        snapshot, 
        loop_instance.telemetry.history
    )
    
    return {"recommendations": [asdict(r) for r in recommendations]}


@app.get("/mutations/log")
async def get_mutations_log(limit: int = 20):
    """Retorna histórico de mutações aplicadas."""
    if not loop_instance:
        return {"log": []}
    return {"log": loop_instance.mutator.get_mutation_log(limit)}


@app.post("/mutations/rollback")
async def trigger_rollback():
    """Executa rollback para o último backup."""
    if not loop_instance:
        raise HTTPException(status_code=503, detail="OtimizationLoop não inicializado")
    
    success = await loop_instance.mutator.rollback()
    if success:
        return {"status": "success", "message": "Rollback executado com sucesso"}
    raise HTTPException(status_code=500, detail="Falha no rollback")


@app.get("/health")
async def health():
    """Monitoramento de saúde do Optimization Engine."""
    return {
        "status": "operational" if loop_instance else "unavailable",
        "running": loop_instance.running if loop_instance else False,
        "interval": loop_instance.interval if loop_instance else 0,
        "cycles_completed": loop_instance.tracker.cycle_count if loop_instance else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)