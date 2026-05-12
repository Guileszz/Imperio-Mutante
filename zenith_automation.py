"""
ZENITH AUTOMATION v2.0 - Motor de Extração Recursiva Total
Evolução do MagEngine com Extração Recursiva, URL Discovery e Ranking de Fontes.

ARQUITETURA:
├── ZenithEngine (Orquestrador de Extração)
│   ├── RecursiveExtractor (Coleta em profundidade)
│   ├── URLDiscovery (Descoberta de links de alta relevância)
│   ├── SourceRanker (Ranking de Néctar por densidade)
│   └── LMArenaBridge (Captura de benchmarks SOTA)
└── Protocolo Néctar Supremo v2.0
"""

import asyncio
import httpx
import re
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ZENITH - %(levelname)s - %(message)s')
logger = logging.getLogger("ZENITH-AUTOMATION")

HIGH_RELEVANCE_KEYWORDS = [
    "SOTA", "state-of-the-art", "leaderboard", "benchmark", "model-release",
    "performance", "ranking", "evaluation", "accuracy", "win", "best",
    "new-model", "release-notes", "changelog", "improvement", "breakthrough"
]

SOURCE_WEIGHTS = {
    "lmsys.org": 2.5,
    "huggingface.co": 2.0,
    "arxiv.org": 1.8,
    "openai.com": 1.5,
    "anthropic.com": 1.5,
    "github.com": 1.2,
    "deepmind.com": 1.5,
    "meta.ai": 1.5
}


class RecursiveExtractor:
    """
    Extrator Recursivo: Varredura em profundidade de páginas e sub-páginas.
    Segue links internos para capturar a estrutura completa de conhecimento.
    """
    
    def __init__(self, client: httpx.AsyncClient, max_depth: int = 3, max_urls: int = 50):
        self.client = client
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.visited: Set[str] = set()
    
    async def extract(self, url: str, depth: int = 0) -> List[Dict[str, Any]]:
        results = []
        
        if depth >= self.max_depth or len(self.visited) >= self.max_urls:
            return results
        
        normalized_url = self._normalize_url(url)
        if normalized_url in self.visited:
            return results
        
        self.visited.add(normalized_url)
        
        try:
            response = await self.client.get(normalized_url, timeout=15.0)
            if response.status_code != 200:
                return results
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = self._extract_content(soup)
            if content:
                results.append({
                    "url": normalized_url,
                    "depth": depth,
                    "title": soup.title.string if soup.title else "",
                    "content": content[:2000],
                    "timestamp": datetime.now().isoformat(),
                    "links": self._extract_links(soup, normalized_url)
                })
            
            if depth < self.max_depth:
                links = self._extract_links(soup, normalized_url)
                high_value_links = self._filter_high_relevance(links)
                
                tasks = [self.extract(link, depth + 1) for link in high_value_links[:5]]
                sub_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for sub_result in sub_results:
                    if isinstance(sub_result, list):
                        results.extend(sub_result)
                        
        except Exception as e:
            logger.debug(f"Erro ao extrair {url}: {e}")
        
        return results
    
    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http'):
                links.append(href)
            elif href.startswith('/'):
                links.append(urljoin(base_url, href))
        return links[:20]
    
    def _filter_high_relevance(self, links: List[str]) -> List[str]:
        filtered = []
        for link in links:
            link_lower = link.lower()
            for keyword in HIGH_RELEVANCE_KEYWORDS:
                if keyword.lower() in link_lower:
                    filtered.append(link)
                    break
        return filtered or links[:3]


class URLDiscovery:
    """
    Descoberta de URLs de Alta Relevância.
    Baseado em palavras-chave de alta densidade de conhecimento (Néctar).
    """
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.discovery_patterns = [
            (r"(?i)(sota|state.of.the.art)", "benchmark_sota"),
            (r"(?i)(leaderboard|ranking)", "leaderboard"),
            (r"(?i)(model.release|release.notes)", "release_notes"),
            (r"(?i)(benchmark|evaluation)", "evaluation"),
            (r"(?i)(accuracy|performance)", "performance")
        ]
    
    async def discover(self, base_url: str) -> List[Dict[str, Any]]:
        discovered = []
        
        try:
            response = await self.client.get(base_url, timeout=15.0)
            if response.status_code != 200:
                return discovered
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href) if not href.startswith('http') else href
                
                for pattern, category in self.discovery_patterns:
                    if re.search(pattern, href + str(a.get_text())):
                        discovered.append({
                            "url": full_url,
                            "category": category,
                            "anchor_text": a.get_text(strip=True),
                            "weight": self._calculate_weight(full_url)
                        })
                        break
                        
        except Exception as e:
            logger.debug(f"Erro na descoberta em {base_url}: {e}")
        
        return discovered[:15]
    
    def _calculate_weight(self, url: str) -> float:
        weight = 1.0
        parsed = urlparse(url)
        
        for domain, multiplier in SOURCE_WEIGHTS.items():
            if domain in parsed.netloc:
                weight *= multiplier
                break
        
        for keyword in HIGH_RELEVANCE_KEYWORDS:
            if keyword.lower() in url.lower():
                weight *= 1.5
                break
        
        return weight


class SourceRanker:
    """
    Ranking de Fontes por Densidade de Néctar.
    Prioriza fontes com maior potencial de inteligência competitiva.
    """
    
    def __init__(self):
        self.source_scores: Dict[str, float] = {}
    
    def rank(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for source in sources:
            url = source.get("url", "")
            base_domain = urlparse(url).netloc
            
            score = source.get("weight", 1.0) * source.get("relevance_score", 1.0)
            
            for domain, multiplier in SOURCE_WEIGHTS.items():
                if domain in base_domain:
                    score *= multiplier
                    break
            
            source["nectar_score"] = score
            self.source_scores[url] = score
        
        return sorted(sources, key=lambda x: x.get("nectar_score", 0), reverse=True)
    
    def get_top_sources(self, sources: List[Dict], top_n: int = 5) -> List[Dict]:
        ranked = self.rank(sources)
        return ranked[:top_n]


class ZenithEngine:
    """
    ZENITH AUTOMATION v2.0 - Motor de Extração Recursiva Total.
    Combina: RecursiveExtractor + URLDiscovery + SourceRanker + LMArenaBridge.
    """
    
    def __init__(self, alquimia_endpoint: str = "http://localhost:8001"):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20)
        )
        self.alquimia_endpoint = alquimia_endpoint
        self.extractor = RecursiveExtractor(self.client)
        self.discovery = URLDiscovery(self.client)
        self.ranker = SourceRanker()
        self.base_sources = [
            "https://lmsys.org/blog/",
            "https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard",
            "https://huggingface.co/blog",
            "https://openai.com/news",
            "https://arxiv.org/cs"
        ]
    
    async def send_to_alquimia(self, nectar_data: List[Dict[str, Any]]):
        """Envia o Néctar colhido para a Alquimia para destilação e cache Redis."""
        try:
            formatted_items = []
            for item in nectar_data:
                formatted_items.append({
                    "raw_text": item.get("content", ""),
                    "url": item.get("url", ""),
                    "source": "zenith_automation",
                    "nectar_score": item.get("nectar_score", 1.0),
                    "metadata": {
                        "title": item.get("title", ""),
                        "depth": item.get("depth", 0),
                        "category": item.get("category", "extraction")
                    }
                })
            
            if not formatted_items:
                return

            await self.client.post(
                f"{self.alquimia_endpoint}/distill",
                json={
                    "items": formatted_items,
                    "source": "zenith_automation"
                },
                timeout=15.0
            )
            logger.info(f"Zenith alimentou Alquimia com {len(formatted_items)} itens.")
        except Exception as e:
            logger.warning(f"Falha ao enviar dados do Zenith para Alquimia: {e}")

    async def harvest_nectar(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Coleta principal de Néctar usando todos os módulos.
        """
        target_sources = sources or self.base_sources
        all_nectar = []
        
        logger.info(f"Iniciando extração recursiva em {len(target_sources)} fontes...")
        
        for source_url in target_sources:
            try:
                logger.info(f"Coletando em: {source_url}")
                
                discovered = await self.discovery.discover(source_url)
                logger.info(f"  Descobertos {len(discovered)} links de alta relevância.")
                
                recursive_data = await self.extractor.extract(source_url)
                logger.info(f"  Extraídos {len(recursive_data)} nós de conteúdo.")
                
                for item in discovered + recursive_data:
                    item["source_domain"] = urlparse(item.get("url", source_url)).netloc
                
                all_nectar.extend(discovered)
                all_nectar.extend(recursive_data)
                
            except Exception as e:
                logger.error(f"Erro ao coletar {source_url}: {e}")
        
        ranked_nectar = self.ranker.rank(all_nectar)
        top_nectar = self.ranker.get_top_sources(ranked_nectar, top_n=10)
        
        # Alimenta Alquimia instantaneamente
        if ranked_nectar:
            await self.send_to_alquimia(ranked_nectar)
        
        return {
            "total_collected": len(all_nectar),
            "ranked_sources": ranked_nectar[:30],
            "top_nectar": top_nectar,
            "timestamp": datetime.now().isoformat()
        }
    
    async def harvest_lm_arena(self) -> Dict[str, Any]:
        """
        Protocolo LMArenaBridge: Extração especializada de benchmarks.
        """
        logger.info("Executando Protocolo LMArenaBridge...")
        
        sources = [
            "https://lmsys.org/blog/",
            "https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard"
        ]
        
        results = []
        for source in sources:
            data = await self.extractor.extract(source)
            results.extend(data)
        
        return {
            "benchmark_data": results,
            "source": "LMArenaBridge",
            "timestamp": datetime.now().isoformat()
        }
    
    async def sync_with_supra_codex(self, codex_url: str = "http://localhost:8000/health"):
        """
        Verifica sincronia com o NEXUS CORE.
        """
        try:
            resp = await self.client.get(codex_url, timeout=5.0)
            return {"status": "synced", "response": resp.status_code == 200}
        except:
            return {"status": "desync", "response": False}
    
    async def alert_oracle(self, message: str, data: Dict[str, Any] = None):
        """
        Envia alerta para o NEXUS CORE.
        """
        try:
            await self.client.post(
                "http://localhost:8000/oracle/notification",
                json={
                    "message": message,
                    "type": "ZENITH_EVENT",
                    "event_type": data.get("type", "nectar_harvest") if data else "nectar_harvest",
                    "relevance": "high",
                    "source": "ZENITH-AUTOMATION",
                    "data": data or {}
                }
            )
        except Exception as e:
            logger.debug(f"Falha ao alertar Oráculo: {e}")
    
    async def close(self):
        await self.client.aclose()


if __name__ == "__main__":
    async def main():
        engine = ZenithEngine()
        nectar = await engine.harvest_nectar()
        print(f"🍯 Néctar colhido: {nectar['total_collected']} fontes")
        print(f"⭐ Top Néctar: {[n['url'] for n in nectar['top_nectar']]}")
        await engine.close()
    
    asyncio.run(main())