"""
[LEGACY] Roteador de Inteligência Assíncrono - Protocolo Trindade 2.5
ESTE MÓDULO FOI SUPERSEDIDO PELO NEXUS CORE v3.1.0 (nexus_core.py)
Mantido apenas para compatibilidade de referência.
"""

import os
import asyncio
import json
import uuid
import logging
from typing import Dict, Optional, Literal, Union, Any
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai
import httpx
from telemetry import TelemetrySystem
from mag_engine import MagEngine

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TRINDADE-ROUTER")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Node definitions - Protocol Trindade 2.5
class NodeType(str, Enum):
    SPECTRUM = "SPECTRUM"      # Eficiência/Nó Linux/3050
    NEURO_TOXIN = "NEURO-TOXIN"  # Agressividade/Cluster Ryzen 9/3070
    GLITCH = "GLITCH"          # Resiliência/Mobile/Laptop/Ally (failover)


# Node configuration with endpoints and capabilities
NODE_CONFIG = {
    NodeType.SPECTRUM: {
        "name": "ESPECTRO",
        "endpoint": os.getenv("SPECTRUM_ENDPOINT", "http://localhost:8001"),
        "capabilities": ["automation", "monitoring", "lightweight"],
        "hardware": "Linux Node / RTX 3050",
        "priority": 1,
    },
    NodeType.NEURO_TOXIN: {
        "name": "NEURO-TOXINA",
        "endpoint": os.getenv("NEUROTOXIN_ENDPOINT", "http://localhost:8002"),
        "capabilities": ["neural_networks", "heavy_processing", "complex_analysis"],
        "hardware": "Ryzen 9 Cluster / RTX 3070",
        "priority": 2,
    },
    NodeType.GLITCH: {
        "name": "GLITCH",
        "endpoint": os.getenv("GLITCH_ENDPOINT", "http://localhost:8003"),
        "capabilities": ["edge_computing", "quick_tasks", "interface"],
        "hardware": "Mobile/Laptop/Ally",
        "priority": 3,
    },
}

# Global state
tasks: Dict[str, Dict] = {}
clients: Dict[str, httpx.AsyncClient] = {}
telemetry = TelemetrySystem()
engine = MagEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage lifecycle of HTTP clients and engines."""
    clients["httpx"] = httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=20))
    yield
    await clients["httpx"].aclose()
    await engine.close()


app = FastAPI(
    title="Roteador Trindade 2.5",
    description="Protocolo Sombra - Classificador Assíncrono com Failover",
    version="2.5.0",
    lifespan=lifespan,
)


# ============== Pydantic Models ==============

class IngressRequest(BaseModel):
    content: Union[str, Dict[str, Any]]
    priority: Optional[str] = Field(None, description="Hint for classification (optional)")
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


class HealthResponse(BaseModel):
    status: str
    nodes: Dict[str, Dict]
    active_tasks: int
    telemetry: Dict[str, Any]


# ============== Classification Logic ==============

async def classify_with_gemini(content: Union[str, Dict[str, Any]], priority_hint: Optional[str] = None) -> NodeType:
    """
    Classify the payload using Gemini API (Trindade 2.5).
    
    Returns:
        NodeType: The target node for processing
    """
    if not GEMINI_API_KEY:
        # Failover to GLITCH if no API key configured
        return NodeType.GLITCH
    
    # Convert dict to formatted string for Gemini
    if isinstance(content, dict):
        content_str = f"[DADOS ESTRUTURADOS]\n{json.dumps(content, indent=2, ensure_ascii=False)}"
    else:
        content_str = content
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""[SISTEMA: TRINDADE 2.5]
[PROTOCOLO: CLASSIFICAÇÃO DE ESPECTRO]

Analise o conteúdo e classifique-o em um dos seguintes nós de processamento:

• SPECTRUM (Nó Linux/3050): Tarefas de eficiência, automação leve, monitoramento, pipelines de dados, scripts de manutenção. Dados de tendência (TREND_DATA, ESPECTRO).

• NEURO-TOXIN (Cluster Ryzen 9/3070): Processamento pesado, redes neurais, análise complexa, machine learning, rendering, simulações. Dados de alta frequência (HF_DATA, NEURO-TOXINA).

• GLITCH (Mobile/Laptop/Ally): Tarefas rápidas, edge computing, interfaces, testes, protótipos, fallback. Anomalias de mercado (GLITCH).

Conteúdo: {content_str}
{'Prioridade sugerida: ' + priority_hint if priority_hint else ''}

Responda APENAS com: SPECTRUM, NEURO-TOXIN ou GLITCH"""

        start_time = asyncio.get_event_loop().time()
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: model.generate_content(prompt)
        )
        end_time = asyncio.get_event_loop().time()
        
        # Track telemetry
        latency = end_time - start_time
        # Simple token estimation: 4 chars per token
        tokens = len(prompt + response.text) // 4
        perf = await telemetry.monitor_gemini_performance(latency, tokens)
        logger.info(f"Gemini Performance: {perf}")
        
        classification = response.text.strip().upper()
        
        # Map to NodeType
        if "NEURO" in classification:
            return NodeType.NEURO_TOXIN
        elif "SPECTRUM" in classification or "ESPECTRO" in classification:
            return NodeType.SPECTRUM
        else:
            return NodeType.GLITCH
            
    except Exception as e:
        # Automatic failover to GLITCH on any error
        return NodeType.GLITCH


async def dispatch_to_node(
    task_id: str, 
    content: Union[str, Dict[str, Any]], 
    node_type: NodeType, 
    max_retries: int = 2
) -> Dict:
    """
    Dispatch task to target node with automatic failover to GLITCH.
    Uses httpx for zero-latency async HTTP calls.
    """
    node_config = NODE_CONFIG[node_type]
    
    for attempt in range(max_retries + 1):
        try:
            client = clients["httpx"]
            response = await client.post(
                f"{node_config['endpoint']}/process",
                json={"task_id": task_id, "content": content},
                timeout=10.0
            )
            
            if response.status_code == 200:
                    return {
                        "status": "completed",
                        "node": node_config["name"],
                        "result": response.json(),
                        "metadata": {
                            "model": "gemini-1.5-flash",
                            "protocol": "Trindade 2.5",
                            "hardware": node_config["hardware"],
                            "attempt": attempt + 1,
                        }
                    }
                    
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError) as e:
            # Log the failure and try next node or failover to GLITCH
            tasks[task_id]["last_error"] = str(e)
            
            if attempt < max_retries:
                # Try same node again
                continue
            elif node_type != NodeType.GLITCH:
                # Failover to GLITCH
                return await dispatch_to_node(task_id, content, NodeType.GLITCH, max_retries=1)
    
    # Final fallback to GLITCH
    return await dispatch_to_node(task_id, content, NodeType.GLITCH, max_retries=1)


async def process_task(task_id: str, content: Union[str, Dict[str, Any]], priority_hint: Optional[str] = None):
    """
    Main processing pipeline: Classify -> Dispatch -> Update status.
    Runs as FastAPI Background Task for zero-latency response.
    """
    tasks[task_id]["status"] = "processing"
    
    try:
        # Step 1: Classify using Gemini API
        node_type = await classify_with_gemini(content, priority_hint)
        
        # Especial logic for SPECTRUM: can trigger MagEngine harvesting
        if node_type == NodeType.SPECTRUM and isinstance(content, str) and "harvest" in content.lower():
            harvest_results = await engine.harvest_nectar(["https://lmsys.org/blog/"])
            tasks[task_id]["harvest_data"] = harvest_results

        # Step 2: Dispatch to classified node
        result = await dispatch_to_node(task_id, content, node_type)
        
        # Step 3: Update task with result
        tasks[task_id].update(result)
        
    except Exception as e:
        # Failover to GLITCH on any processing error
        tasks[task_id]["status"] = "failover"
        try:
            result = await dispatch_to_node(task_id, content, NodeType.GLITCH)
            tasks[task_id].update(result)
        except Exception:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = f"Critical failure: {str(e)}"


# ============== API Endpoints ==============

@app.post("/ingress", response_model=TaskResponse, status_code=202)
async def ingress(request: IngressRequest, background_tasks: BackgroundTasks):
    """
    Ponto de entrada para novas requisições.
    Retorna task_id imediatamente (latência zero).
    Classification happens asynchronously via BackgroundTasks.
    """
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        "status": "queued",
        "content": request.content,
        "priority_hint": request.priority,
        "metadata": request.metadata,
        "created_at": asyncio.get_event_loop().time(),
    }
    
    # Zero-latency: dispatch to background immediately
    background_tasks.add_task(
        process_task, 
        task_id, 
        request.content, 
        request.priority
    )
    
    return TaskResponse(task_id=task_id, status="queued")


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """
    Consulta o status e resultado do processamento.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task.get("status", "unknown"),
        node=task.get("node"),
        result=task.get("result"),
        error=task.get("error"),
        metadata=task.get("metadata"),
    )


@app.delete("/status/{task_id}")
async def delete_task(task_id: str):
    """Remove completed task from memory."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if tasks[task_id].get("status") not in ["completed", "failed"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete task that is still processing"
        )
    
    del tasks[task_id]
    return {"message": "Task deleted", "task_id": task_id}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint with node status and system telemetry.
    """
    return HealthResponse(
        status="operational",
        nodes={
            node.value: {
                "name": config["name"],
                "endpoint": config["endpoint"],
                "hardware": config["hardware"],
                "capabilities": config["capabilities"],
            }
            for node, config in NODE_CONFIG.items()
        },
        active_tasks=sum(1 for t in tasks.values() if t.get("status") == "processing"),
        telemetry=telemetry.get_system_stats(),
    )


@app.get("/nodes")
async def list_nodes():
    """List all available processing nodes."""
    return {
        "nodes": [
            {
                "type": node.value,
                "name": config["name"],
                "hardware": config["hardware"],
                "capabilities": config["capabilities"],
                "priority": config["priority"],
            }
            for node, config in NODE_CONFIG.items()
        ],
        "default_fallback": NodeType.GLITCH.value,
    }


@app.post("/classify")
async def classify_endpoint(request: IngressRequest):
    """
    Direct classification endpoint (no dispatch).
    Useful for testing the classification logic.
    """
    node_type = await classify_with_gemini(request.content, request.priority)
    node_config = NODE_CONFIG[node_type]
    
    return {
        "classification": node_type.value,
        "node_name": node_config["name"],
        "hardware": node_config["hardware"],
        "capabilities": node_config["capabilities"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)