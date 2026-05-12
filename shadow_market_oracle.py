"""
SHADOW MARKET ORACLE v2.5 - Síntese de Oráculo com Stealth Layer v3.0.
Evolução do ShadowCrawler com Correlação de Mercado, UA Dinâmicos e Evasão Adaptativa.

ARQUITETURA:
├── ShadowOracle (Orquestrador de Intelligence)
│   ├── StealthLayer (Importada: Fingerprinting dinâmico + Jittering)
│   ├── MarketCorrelator (Correlação notícias ↔ volatilidade)
│   ├── NewsFeeder (RSS feeds de mercados e tecnologia)
│   └── NeuroDispatcher (Despacho para NEURO-TOXIN)
└── Protocolo Oráculo Sombra
"""

import asyncio
import random
import time
import re
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from stealth_layer import StealthLayer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SHADOW-ORACLE - %(levelname)s - %(message)s')
logger = logging.getLogger("SHADOW-ORACLE")

MARKET_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cryptopanic.com/news/",
    "https://www.investing.com/rss/news.rss",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"
]

TECH_FEEDS = [
    "https://lmsys.org/blog/",
    "https://huggingface.co/blog",
    "https://openai.com/news",
    "https://arxiv.org/cs",
    "https://deepmind.google/blog/rss.xml"
]


class MarketCorrelator:
    """
    Correlaciona feeds de notícias com volatilidade de mercado.
    Detecta anomalias e gera sinais de trading.
    """
    
    def __init__(self):
        self.news_buffer: List[Dict[str, Any]] = []
        self.price_buffer: Dict[str, List[float]] = {}
        self.correlation_threshold = 0.7
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        positive_keywords = ["bullish", "surge", "rise", "gain", "growth", "up", "high", "positive", "breakout"]
        negative_keywords = ["bearish", "crash", "fall", "drop", "decline", "down", "low", "negative", "sell"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        total = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / max(total, 1)
        
        return {
            "score": sentiment_score,
            "positive_signals": positive_count,
            "negative_signals": negative_count,
            "classification": "bullish" if sentiment_score > 0.3 else "bearish" if sentiment_score < -0.3 else "neutral"
        }
    
    def correlate_news_with_volatility(self, news: Dict[str, Any], price_change: float) -> Dict[str, Any]:
        sentiment = self.analyze_sentiment(news.get("content", ""))
        
        correlation_score = 0.0
        if price_change > 0.02 and sentiment["score"] > 0:
            correlation_score = sentiment["score"] * price_change * 10
        elif price_change < -0.02 and sentiment["score"] < 0:
            correlation_score = abs(sentiment["score"]) * abs(price_change) * 10
        
        return {
            "news": news,
            "sentiment": sentiment,
            "price_change": price_change,
            "correlation_score": correlation_score,
            "signal": "STRONG_BUY" if correlation_score > 0.5 else "STRONG_SELL" if correlation_score < -0.5 else "HOLD"
        }
    
    def store_news(self, news: Dict[str, Any]):
        self.news_buffer.append({
            **news,
            "timestamp": time.time()
        })
        
        cutoff = time.time() - 3600
        self.news_buffer = [n for n in self.news_buffer if n.get("timestamp", 0) > cutoff]
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        if not self.news_buffer:
            return {"overall_sentiment": "neutral", "score": 0.0, "news_count": 0}
        
        avg_score = sum(n.get("sentiment", {}).get("score", 0) for n in self.news_buffer) / len(self.news_buffer)
        
        return {
            "overall_sentiment": "bullish" if avg_score > 0.2 else "bearish" if avg_score < -0.2 else "neutral",
            "score": avg_score,
            "news_count": len(self.news_buffer)
        }


class NewsFeeder:
    """
    Coletor de Feeds RSS com parsing inteligente.
    Extrai títulos, descrições e locais dos feeds.
    """
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def fetch_feed(self, url: str) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(url, timeout=15.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = []
            for item in soup.find_all('item')[:10]:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                items.append({
                    "title": title.get_text(strip=True) if title else "",
                    "description": description.get_text(strip=True)[:500] if description else "",
                    "link": link.get_text(strip=True) if link else "",
                    "published": pub_date.get_text(strip=True) if pub_date else "",
                    "source": urlparse(url).netloc
                })
            
            return items
            
        except Exception as e:
            logger.debug(f"Erro ao buscar feed {url}: {e}")
            return []


class ShadowOracle:
    """
    SHADOW MARKET ORACLE v2.5 - Síntese de Oráculo.
    Combina: StealthLayer + MarketCorrelator + NewsFeeder + NeuroDispatcher.
    """
    
    def __init__(self, neuro_toxin_endpoint: str = "http://localhost:8002/process", alquimia_endpoint: str = "http://localhost:8001"):
        self.neuro_toxin_endpoint = neuro_toxin_endpoint
        self.alquimia_endpoint = alquimia_endpoint
        self.client = httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20)
        )
        
        self.stealth = StealthLayer()
        self.correlator = MarketCorrelator()
        self.feeder = NewsFeeder(self.client)
        
        self.market_targets = MARKET_FEEDS
        self.tech_targets = TECH_FEEDS
    
    async def send_to_alquimia(self, items: List[Dict[str, Any]]):
        """Envia o Néctar coletado para a Alquimia para destilação e armazenamento."""
        try:
            formatted_items = []
            for item in items:
                if isinstance(item, dict):
                    formatted_items.append({
                        "raw_text": f"{item.get('title', '')} - {item.get('description', '')}",
                        "url": item.get("link", ""),
                        "source": item.get("source", "shadow_oracle"),
                        "nectar_score": item.get("sentiment", {}).get("score", 0.5) + 0.5 
                    })

            if not formatted_items:
                return

            resp = await self.client.post(
                f"{self.alquimia_endpoint}/distill",
                json={
                    "items": formatted_items,
                    "source": "shadow_market_oracle"
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                logger.info(f"Néctar enviado para Alquimia: {len(formatted_items)} itens.")
        except Exception as e:
            logger.warning(f"Falha ao enviar Néctar para Alquimia: {e}")

    async def scrape_target(self, url: str) -> Dict[str, Any]:
        domain = urlparse(url).netloc
        
        # Uso da nova StealthLayer
        await self.stealth.apply_jitter(domain)
        headers = self.stealth.get_headers()
        
        try:
            response = await self.client.get(url, headers=headers, timeout=15.0)
            
            if response.status_code == 403 or response.status_code == 429:
                self.stealth.mark_blocked(domain)
                return {"url": url, "error": "blocked", "status_code": response.status_code}
            
            response.raise_for_status()
            
            # Simple check for RSS content
            if "rss" in url or "application/xml" in response.headers.get("content-type", ""):
                 # Note: fetch_feed in NewsFeeder already does its own get request. 
                 # This is a bit redundant but following existing pattern.
                 items = await self.feeder.fetch_feed(url)
                 return {"url": url, "type": "rss", "items": items, "count": len(items)}
            
            return {
                "url": url,
                "type": "html",
                "content_length": len(response.text),
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.debug(f"Erro ao infiltrar {url}: {e}")
            return {"url": url, "error": str(e)}
    
    async def dispatch_to_neuro_toxin(self, payload: Dict[str, Any]) -> bool:
        try:
            resp = await self.client.post(
                self.neuro_toxin_endpoint,
                json={
                    "task_id": f"SHADOW-{uuid_hex()}",
                    "content": payload,
                    "priority": "HIGH",
                    "type": "ORACLE_INTEL"
                },
                timeout=5.0
            )
            return resp.status_code == 200
        except:
            return False
    
    async def run_market_cycle(self) -> Dict[str, Any]:
        logger.info("Iniciando ciclo de intelligence de mercado...")
        
        all_intel = []
        targets = self.market_targets + self.tech_targets
        random.shuffle(targets)
        
        for url in targets:
            result = await self.scrape_target(url)
            if result.get("items"):
                all_intel.extend(result["items"])
            elif result.get("type") == "html":
                all_intel.append(result)
        
        for item in all_intel:
            if isinstance(item, dict) and "title" in item:
                sentiment = self.correlator.analyze_sentiment(item.get("title", "") + " " + item.get("description", ""))
                item["sentiment"] = sentiment
                self.correlator.store_news(item)
        
        market_sentiment = self.correlator.get_market_sentiment()
        
        return {
            "intel_collected": len(all_intel),
            "market_sentiment": market_sentiment,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_cycle(self):
        logger.info("Protocolo SHADOW ORACLE ativado.")
        
        while True:
            result = await self.run_market_cycle()
            
            logger.info(f"Ciclo concluído: {result['intel_collected']} itens coletados | Sentimento: {result['market_sentiment']['overall_sentiment']}")
            
            if result['intel_collected'] > 0:
                await self.send_to_alquimia(self.correlator.news_buffer)
            
            if result['intel_collected'] > 5:
                await self.dispatch_to_neuro_toxin(result)
            
            wait_time = random.uniform(90, 180)
            logger.info(f"Próxima infiltração em {wait_time:.1f}s.")
            await asyncio.sleep(wait_time)
    
    async def close(self):
        await self.client.aclose()


def uuid_hex() -> str:
    import uuid
    return uuid.uuid4().hex[:8]


if __name__ == "__main__":
    oracle = ShadowOracle()
    try:
        asyncio.run(oracle.run_cycle())
    except KeyboardInterrupt:
        logger.info("SHADOW ORACLE desativado pelo operador.")
