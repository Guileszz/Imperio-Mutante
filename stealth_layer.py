"""
STEALTH LAYER v3.0 - Camada de Furtividade Avançada.
Implementa fingerprinting dinâmico, jittering adaptativo e evasão de detecção.
"""

import random
import time
import asyncio
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - STEALTH-LAYER - %(levelname)s - %(message)s')
logger = logging.getLogger("STEALTH-LAYER")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
]

class StealthLayer:
    """
    Camada de Stealth: Fingerprinting dinâmico e jittering adaptativo.
    """
    
    def __init__(self):
        self.request_count = 0
        self.last_reset = time.time()
        self.blocked_domains = {}
        self.adaptive_delay = True
        self.session_fingerprint = self._generate_session_fingerprint()

    def _generate_session_fingerprint(self) -> Dict[str, str]:
        """Gera um conjunto consistente de headers para uma 'sessão' simulada."""
        ua = random.choice(USER_AGENTS)
        platform = "Windows" if "Windows" in ua else "macOS" if "Macintosh" in ua else "Linux"
        
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua-Platform": f'"{platform}"'
        }

    def get_headers(self, rotate: bool = False) -> Dict[str, str]:
        """Retorna headers com fingerprinting dinâmico."""
        if rotate:
            self.session_fingerprint = self._generate_session_fingerprint()
            
        headers = self.session_fingerprint.copy()
        
        # Jittering de versão no Sec-Ch-Ua
        version = random.randint(119, 123)
        headers["Sec-Ch-Ua"] = f'"Chromium";v="{version}", "Google Chrome";v="{version}", "Not=A?Brand";v="99"'
        
        return headers

    def get_delay(self, domain: str) -> float:
        """Calcula delay com jittering para evitar detecção por padrão temporal."""
        self.request_count += 1
        
        if time.time() - self.last_reset > 60:
            self.request_count = 0
            self.last_reset = time.time()
        
        # Delay base entre 2 e 5 segundos
        base_delay = random.uniform(2.0, 5.0)
        
        # Adiciona Jitter (ruído aleatório)
        jitter = random.uniform(-0.5, 1.5)
        
        final_delay = base_delay + jitter
        
        # Se houver muitos requests, aumenta exponencialmente o delay
        if self.request_count > 10:
            final_delay *= (1.2 ** (self.request_count - 10))
            
        # Verifica se o domínio está marcado como bloqueado
        if domain in self.blocked_domains:
            block_time = self.blocked_domains[domain]
            if time.time() - block_time < 600: # 10 minutos de cooldown
                return random.uniform(60.0, 120.0)
            else:
                del self.blocked_domains[domain]
        
        return max(final_delay, 1.0)

    def mark_blocked(self, domain: str):
        self.blocked_domains[domain] = time.time()
        logger.warning(f"⚠️ Detecção de Bloqueio em {domain}. Ativando cooldown de 10min.")

    async def apply_jitter(self, domain: str):
        """Aplica o delay de forma assíncrona."""
        delay = self.get_delay(domain)
        if delay > 10:
            logger.info(f"Stealth: Delay preventivo de {delay:.2f}s para {domain}")
        await asyncio.sleep(delay)
