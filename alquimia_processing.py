"""
ALQUIMIA PROCESSAMENTO v1.0 - Destiladora de Conhecimento Escalável.
Plataforma de processamento de dados com FastAPI + Redis para gestão de 
conhecimento de longo prazo e latência zero via multi-processing.

ARQUITETURA:
├── AlquimiaAPI (FastAPI)
│   ├── /distill - Destilação de conteúdo
│   ├── /knowledge - Store/Retrieve conhecimento
│   ├── /synthesize - Consolidação de Néctar
│   └── /health - Monitoramento
├── DataDistiller (Multi-processing)
│   ├── HTMLCleaner
│   ├── TextNormalizer
│   ├── EntityExtractor
│   └── KnowledgeVectorizer
├── RedisCache (Gestão de conhecimento)
│   ├── NectarStore
│   ├── KnowledgeBase
│   └── VectorCache
└── Protocolo Alquimia
"""

import asyncio
import json
import time
import hashlib
import multiprocessing as mp
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from functools import partial
import logging

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ALQUIMIA - %(levelname)s - %(message)s')
logger = logging.getLogger("ALQUIMIA-PROCESSING")


# =============================================================================
# WORKER FUNCTIONS (Multi-processing)
# =============================================================================

def _clean_html_worker(raw_html: str) -> str:
    """Worker para limpeza de HTML em processo separado."""
    if not BS4_AVAILABLE:
        return raw_html[:5000]
    
    try:
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            element.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned = "\n".join(lines)
        
        return cleaned[:10000]
    except Exception:
        return raw_html[:5000]


def _extract_entities_worker(text: str) -> Dict[str, Any]:
    """Worker para extração de entidades e padrões."""
    entities = {
        "models": [],
        "metrics": [],
        "links": []
    }
    
    import re
    
    model_patterns = [
        r'(?:gpt|claude|gemini|llama|mistral|phi|qwen|mixtral)[\- ]?[0-9]+(?:\.[0-9]+)?',
        r'(?:model|version|v)[0-9]+(?:\.[0-9]+)?',
        r'(?:openai|anthropic|google|meta|microsoft)[\- ]?(?:ai|llm)?',
    ]
    
    for pattern in model_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["models"].extend(matches[:5])
    
    metric_patterns = [
        r'\b(?:accuracy|precision|recall|f1|mse|mae|bleu|rouge)[_\s]?(?:score|rate)?\s*[=:]\s*[0-9.]+',
        r'\b[0-9]+(?:\.[0-9]+)?\s*%',
        r'\b(?:benchmark|sota)\s*[=:]\s*[0-9.]+',
    ]
    
    for pattern in metric_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["metrics"].extend(matches[:5])
    
    link_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    entities["links"] = re.findall(link_pattern, text)[:10]
    
    entities["models"] = list(set(entities["models"]))[:10]
    entities["metrics"] = list(set(entities["metrics"]))[:10]
    
    return entities


def _normalize_text_worker(text: str) -> str:
    """Worker para normalização de texto."""
    import re
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n+', r'\n\n', text)
    
    # Keep only alphanumeric, spaces, and safe punctuation
    # Be conservative with special characters
    allowed = re.compile('[^a-zA-Z0-9 .,;:!?()\\[\\]{}]')
    text = allowed.sub('', text)
    
    text = text[:8000]
    
    return text.strip()


def _process_chunk_worker(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Worker principal para processar um chunk de dados."""
    result = {
        "original_hash": chunk.get("hash", ""),
        "processed_at": datetime.now().isoformat(),
        "status": "success"
    }
    
    if "html" in chunk:
        result["text"] = _clean_html_worker(chunk["html"])
    elif "raw_text" in chunk:
        result["text"] = _normalize_text_worker(chunk["raw_text"])
    else:
        result["text"] = str(chunk.get("content", ""))[:5000]
    
    result["entities"] = _extract_entities_worker(result["text"])
    
    text_hash = hashlib.sha256(result["text"].encode()).hexdigest()
    result["content_hash"] = text_hash
    
    return result


# =============================================================================
# DATA DISTILLER (Multi-processing Pool)
# =============================================================================

class DataDistiller:
    """
    Destilador de Dados via Multi-processing.
    Processa grandes volumes de texto/HTML em paralelo para latência zero.
    """
    
    def __init__(self, workers: int = None):
        self.workers = workers or max(mp.cpu_count() - 1, 2)
        self.pool = None
        logger.info(f"DataDistiller inicializado com {self.workers} workers.")
    
    def start(self):
        self.pool = mp.Pool(processes=self.workers)
        logger.info(f"Pool de processamento iniciado com {self.workers} processos.")
    
    def stop(self):
        if self.pool:
            self.pool.close()
            self.pool.join()
            logger.info("Pool de processamento encerrado.")
    
    def distill(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Destila uma lista de itens usando multi-processing.
        Retorna resultados processados e limpos.
        """
        if not self.pool:
            self.start()
        
        chunks = []
        for item in data:
            chunk = {
                "hash": hashlib.md5(str(item).encode()).hexdigest(),
                **item
            }
            chunks.append(chunk)
        
        logger.info(f"Iniciando destilação de {len(chunks)} itens com {self.workers} workers...")
        
        results = self.pool.map(_process_chunk_worker, chunks)
        
        success_count = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Destilação concluída: {success_count}/{len(chunks)} itens processados com sucesso.")
        
        return results
    
    async def distill_async(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Versão assíncrona para integração com FastAPI."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.distill, data)


# =============================================================================
# REDIS KNOWLEDGE STORE
# =============================================================================

@dataclass
class KnowledgeBlock:
    id: str
    content: str
    source: str
    entities: Dict[str, Any]
    nectar_score: float
    timestamp: str
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeBlock":
        return cls(**data)


class RedisKnowledgeStore:
    """
    Gestão de conhecimento escalável usando Redis.
    Fallback para dicionário em memória se Redis não disponível.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.fallback_store: Dict[str, KnowledgeBlock] = {}
        self.connected = False
        
        if REDIS_AVAILABLE:
            self._connect_task = asyncio.create_task(self._connect())
        else:
            logger.warning("Redis não disponível. Usando armazenamento em memória.")
    
    async def _connect(self):
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            self.connected = True
            logger.info("Redis conectado para gestão de conhecimento.")
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}. Usando fallback em memória.")
            self.connected = False
    
    async def wait_connected(self, timeout: float = 5.0):
        start = time.time()
        while not self.connected and time.time() - start < timeout:
            await asyncio.sleep(0.1)
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    self.connected = True
                except:
                    pass
    
    def _generate_id(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def store(self, block: KnowledgeBlock) -> bool:
        try:
            if self.connected and self.redis_client:
                key = f"knowledge:{block.id}"
                await self.redis_client.hset(key, mapping={
                    "id": block.id,
                    "content": block.content[:5000],
                    "source": block.source,
                    "entities": json.dumps(block.entities),
                    "nectar_score": str(block.nectar_score),
                    "timestamp": block.timestamp,
                    "tags": json.dumps(block.tags)
                })
                await self.redis_client.expire(key, 86400 * 7)
                
                await self.redis_client.sadd("knowledge:index", block.id)
                
                return True
            else:
                self.fallback_store[block.id] = block
                return True
        except Exception as e:
            logger.error(f"Erro ao armazenar knowledge: {e}")
            self.fallback_store[block.id] = block
            return True
    
    async def retrieve(self, block_id: str) -> Optional[KnowledgeBlock]:
        try:
            if self.connected and self.redis_client:
                key = f"knowledge:{block_id}"
                data = await self.redis_client.hgetall(key)
                if data:
                    return KnowledgeBlock(
                        id=data["id"],
                        content=data["content"],
                        source=data["source"],
                        entities=json.loads(data["entities"]),
                        nectar_score=float(data["nectar_score"]),
                        timestamp=data["timestamp"],
                        tags=json.loads(data["tags"])
                    )
            else:
                return self.fallback_store.get(block_id)
        except Exception as e:
            logger.debug(f"Erro ao recuperar knowledge: {e}")
            return self.fallback_store.get(block_id)
    
    async def search(self, query: str, limit: int = 10) -> List[KnowledgeBlock]:
        results = []
        
        try:
            if self.connected and self.redis_client:
                all_ids = await self.redis_client.smembers("knowledge:index")
                
                for block_id in list(all_ids)[:100]:
                    block = await self.retrieve(block_id)
                    if block and query.lower() in block.content.lower():
                        results.append(block)
                        if len(results) >= limit:
                            break
            else:
                for block in self.fallback_store.values():
                    if query.lower() in block.content.lower():
                        results.append(block)
                        if len(results) >= limit:
                            break
        except Exception as e:
            logger.debug(f"Erro na busca: {e}")
        
        return results[:limit]
    
    async def get_all(self, limit: int = 100) -> List[KnowledgeBlock]:
        results = []
        
        try:
            if self.connected and self.redis_client:
                all_ids = await self.redis_client.smembers("knowledge:index")
                for block_id in list(all_ids)[:limit]:
                    block = await self.retrieve(block_id)
                    if block:
                        results.append(block)
            else:
                results = list(self.fallback_store.values())[:limit]
        except Exception as e:
            logger.debug(f"Erro ao listar knowledge: {e}")
        
        return results
    
    async def get_stats(self) -> Dict[str, Any]:
        total = len(self.fallback_store)
        
        if self.connected and self.redis_client:
            try:
                total = await self.redis_client.scard("knowledge:index")
            except:
                pass
        
        return {
            "total_blocks": total,
            "redis_connected": self.connected,
            "fallback_size": len(self.fallback_store)
        }


# =============================================================================
# ALQUIMIA PROCESSOR
# =============================================================================

class AlquimiaProcessor:
    """
    Processador central da Alquimia.
    Coordena: DataDistiller + RedisKnowledgeStore + Synthesis.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.distiller = DataDistiller()
        self.knowledge_store = RedisKnowledgeStore(redis_url)
        self.distiller.start()
        
        logger.info("AlquimiaProcessor inicializado.")
    
    async def process_and_store(self, raw_data: List[Dict[str, Any]], source: str = "unknown") -> Dict[str, Any]:
        """
        Processa dados brutos e os armazena na base de conhecimento.
        """
        logger.info(f"Processando {len(raw_data)} itens de {source}...")
        
        distilled = await self.distiller.distill_async(raw_data)
        
        stored_count = 0
        for item in distilled:
            block = KnowledgeBlock(
                id=self.knowledge_store._generate_id(item.get("text", "")),
                content=item.get("text", "")[:5000],
                source=source,
                entities=item.get("entities", {}),
                nectar_score=item.get("nectar_score", 1.0),
                timestamp=item.get("processed_at", datetime.now().isoformat()),
                tags=[]
            )
            
            if await self.knowledge_store.store(block):
                stored_count += 1
        
        logger.info(f"Conhecimento destilado e armazenado: {stored_count}/{len(raw_data)} blocos.")
        
        return {
            "processed": len(distilled),
            "stored": stored_count,
            "timestamp": datetime.now().isoformat()
        }
    
    async def synthesize_nectar(self, nectar_items: List[Dict], max_blocks: int = 20) -> str:
        """
        Consolida Néctar colhido em blocos de conhecimento unificados.
        """
        logger.info(f"Sintetizando {len(nectar_items)} itens de Néctar...")
        
        all_entities = {"models": [], "metrics": [], "links": []}
        
        for item in nectar_items:
            entities = item.get("entities", {})
            for key in all_entities:
                all_entities[key].extend(entities.get(key, []))
        
        synthesis = []
        synthesis.append("# 🍯 CONSOLIDADO DE NÉCTAR")
        synthesis.append(f"**Data:** {datetime.now().isoformat()}")
        synthesis.append(f"**Fontes processadas:** {len(nectar_items)}")
        synthesis.append("")
        
        if all_entities["models"]:
            synthesis.append("## 🤖 Modelos Identificados")
            unique_models = list(set(all_entities["models"]))[:15]
            for model in unique_models:
                synthesis.append(f"- {model}")
            synthesis.append("")
        
        if all_entities["metrics"]:
            synthesis.append("## 📊 Métricas Extraídas")
            unique_metrics = list(set(all_entities["metrics"]))[:10]
            for metric in unique_metrics:
                synthesis.append(f"- {metric}")
            synthesis.append("")
        
        if all_entities["links"]:
            synthesis.append("## 🔗 Recursos de Alta Densidade")
            unique_links = list(set(all_entities["links"]))[:10]
            for link in unique_links:
                synthesis.append(f"- {link}")
            synthesis.append("")
        
        return "\n".join(synthesis)
    
    def stop(self):
        self.distiller.stop()
        logger.info("AlquimiaProcessor encerrado.")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global processor
    processor = AlquimiaProcessor()
    logger.info("Alquimia Processing API iniciada.")
    yield
    if processor:
        processor.stop()
    logger.info("Alquimia Processing API encerrada.")

app = FastAPI(title="Alquimia Processing v1.0", lifespan=lifespan)


class DistillRequest(BaseModel):
    items: List[Dict[str, Any]]
    source: str = "unknown"
    tags: List[str] = Field(default_factory=list)


class SynthesizeRequest(BaseModel):
    nectar_ids: List[str] = Field(default_factory=list)
    raw_items: List[Dict[str, Any]] = Field(default_factory=list)


class StoreRequest(BaseModel):
    content: str
    source: str = "unknown"
    tags: List[str] = Field(default_factory=list)


@app.post("/distill")
async def distill(request: DistillRequest, background_tasks: BackgroundTasks):
    """Destila dados brutos usando multi-processing."""
    result = await processor.process_and_store(request.items, request.source)
    return {"status": "success", "result": result}


@app.post("/knowledge/store")
async def store_knowledge(request: StoreRequest):
    """Armazena um bloco de conhecimento diretamente."""
    block = KnowledgeBlock(
        id=hashlib.sha256(request.content.encode()).hexdigest()[:16],
        content=request.content[:5000],
        source=request.source,
        entities={},
        nectar_score=1.0,
        timestamp=datetime.now().isoformat(),
        tags=request.tags
    )
    
    success = await processor.knowledge_store.store(block)
    
    if success:
        return {"status": "stored", "id": block.id}
    raise HTTPException(status_code=500, detail="Falha ao armazenar conhecimento")


@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 10):
    """Busca conhecimento armazenado."""
    results = await processor.knowledge_store.search(query, limit)
    return {"results": [r.to_dict() for r in results], "count": len(results)}


@app.get("/knowledge/all")
async def get_all_knowledge(limit: int = 100):
    """Lista todo o conhecimento armazenado."""
    blocks = await processor.knowledge_store.get_all(limit)
    return {"blocks": [b.to_dict() for b in blocks], "count": len(blocks)}


@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Retorna estatísticas da base de conhecimento."""
    return await processor.knowledge_store.get_stats()


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """Consolida Néctar em blocos de conhecimento."""
    nectar_items = []
    
    if request.nectar_ids:
        for nid in request.nectar_ids:
            block = await processor.knowledge_store.retrieve(nid)
            if block:
                nectar_items.append(block.to_dict())
    
    if request.raw_items:
        distilled = await processor.distiller.distill_async(request.raw_items)
        nectar_items.extend(distilled)
    
    if not nectar_items:
        raise HTTPException(status_code=400, detail="Nenhum item para sintetizar")
    
    synthesis = await processor.synthesize_nectar(nectar_items)
    
    return {"synthesis": synthesis, "items_processed": len(nectar_items)}


@app.get("/health")
async def health():
    """Monitoramento de saúde da Alquimia."""
    stats = await processor.knowledge_store.get_stats()
    return {
        "status": "operational",
        "distiller_workers": processor.distiller.workers,
        "knowledge_store": stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)