import asyncio
import random
import time
import httpx
import logging
from typing import List, Dict, Any

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SHADOW-CRAWLER - %(levelname)s - %(message)s')
logger = logging.getLogger("SHADOW-CRAWLER")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

class ShadowCrawler:
    """
    SHADOW CRAWLER - Coletor Furtivo Assíncrono.
    Opera nas sombras para alimentar o nó NEURO-TOXINA com inteligência de mercado.
    """
    def __init__(self, neuro_toxin_endpoint="http://localhost:8002/process"):
        self.neuro_toxin_endpoint = neuro_toxin_endpoint
        self.proxies = self._load_proxies()
        self.client = httpx.AsyncClient(
            timeout=20.0, 
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20)
        )
        self.targets = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cryptopanic.com/news/",
            "https://lmsys.org/blog/",
            "https://huggingface.co/blog",
            "https://openai.com/news"
        ]

    def _load_proxies(self) -> List[str]:
        try:
            with open("supra_codex.json", "r") as f:
                import json
                config = json.load(f)
                return config.get("settings", {}).get("proxies", [])
        except Exception:
            return []

    def _get_stealth_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    async def scrape_source(self, url: str):
        """Coleta furtiva de uma fonte com rotação de proxy."""
        try:
            # Delay aleatório para evitar detecção de padrão (Stealth)
            await asyncio.sleep(random.uniform(2.0, 5.0))
            
            headers = self._get_stealth_headers()
            proxy = random.choice(self.proxies) if self.proxies else None
            
            logger.info(f"Infiltrando em: {url} {'(Proxy: ' + proxy + ')' if proxy else ''}")
            
            async with httpx.AsyncClient(proxies=proxy, timeout=20.0, headers=headers) as client:
                response = await client.get(url)
            
            if response.status_code == 200:
                logger.info(f"Sucesso na coleta: {url} ({len(response.text)} bytes)")
                
                # Payload para o processamento neural
                payload = {
                    "source": url,
                    "content": response.text[:5000], # Enviando fatia significativa para análise
                    "metadata": {
                        "crawler": "shadow_crawler_v1",
                        "timestamp": time.time(),
                        "status_code": response.status_code
                    }
                }
                
                await self.dispatch_to_neuro_toxin(payload)
            else:
                logger.warning(f"Bloqueio ou falha em {url}: Status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao infiltrar {url}: {str(e)}")

    async def dispatch_to_neuro_toxin(self, payload: Dict[str, Any]):
        """Despacha o 'Néctar' coletado para o cérebro agressivo."""
        try:
            # Tentativa de despacho para o nó NEURO-TOXINA
            resp = await self.client.post(
                self.neuro_toxin_endpoint,
                json={
                    "task_id": f"SHADOW-{uuid_hex()}", 
                    "content": payload,
                    "priority": "HIGH"
                },
                timeout=5.0
            )
            if resp.status_code == 200:
                logger.info("Inteligência entregue ao nó NEURO-TOXINA.")
        except Exception:
            # Fallback silencioso se o nó estiver offline (comum em arquiteturas distribuídas)
            logger.debug("Nó NEURO-TOXINA offline. Inteligência descartada ou em buffer local (não implementado).")

    async def run_cycle(self):
        """Loop infinito de coleta furtiva."""
        logger.info("Protocolo SHADOW CRAWLER ativado.")
        while True:
            # Embaralha alvos para não manter ordem fixa
            targets = self.targets.copy()
            random.shuffle(targets)
            
            tasks = [self.scrape_source(url) for url in targets]
            await asyncio.gather(*tasks)
            
            # Intervalo entre ondas de coleta
            wait_time = random.uniform(60, 120)
            logger.info(f"Onda de coleta concluída. Próxima infiltração em {wait_time:.1f}s.")
            await asyncio.sleep(wait_time)

def uuid_hex():
    import uuid
    return uuid.uuid4().hex[:8]

if __name__ == "__main__":
    crawler = ShadowCrawler()
    try:
        asyncio.run(crawler.run_cycle())
    except KeyboardInterrupt:
        logger.info("SHADOW CRAWLER desativado pelo operador.")
