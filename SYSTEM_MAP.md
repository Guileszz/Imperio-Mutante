# 🗺️ Mapa do Sistema - Império Mutante v2.0

## 🚀 Visão Geral
O ecossistema **Império Mutante** evoluiu para a versão 2.0 com arquitetura de inteligência distribuída, soberana e auto-otimizável. O sistema é orquestrado pelo **NEXUS CORE v3.2.0** com protocolos de **Extração Recursiva Total** e **Destilação de Conhecimento**.

---

## 🏛️ Ativos Centrais

### 🌉 LMArenaBridge (Capturador de Essência)
*   **Função**: Minerar o LMSYS Arena e outros benchmarks de LLM em tempo real.
*   **Propósito**: Identificar padrões de resposta superiores, novos modelos emergentes e prompts de alta eficiência.
*   **Néctar**: É a fonte primária de inteligência competitiva, garantindo a "Margem Infinita".

### 📖 Supra-Codex v3.2.0 (Mente Coletiva)
*   **Função**: Repositório central de DNA do sistema.
*   **Conteúdo**: 
    *   Prompts de sistema otimizados.
    *   Lógicas de classificação.
    *   Configurações dinâmicas dos nós.
    *   **NOVO**: Configurações de serviços (Zenith, Shadow Oracle, Alquimia, Optimization Engine).
*   **Sincronização**: Todos os nós devem consultar o Supra-Codex para atualizações de protocolo.

### 🍯 Néctar Supremo v2.0 (Protocolo)
*   **Função**: Protocolo de extração, destilação e síntese de conhecimento.
*   **Fluxo**: HARVEST → DISTILL → STORE → SYNTHESIZE → EVOLVE

---

## 🧠 Cérebro Central

### ⚡ NEXUS CORE v3.2.0
O coração da operação, responsável pela orquestração de múltiplos sistemas:
- Ingresso e classificação adaptativa
- Despacho de tarefas para nós especializados
- Integração com Zenith, Shadow Oracle e Alquimia
- Loop de auto-otimização (Optimization Engine)

### 🔗 Serviços Integrados

| Serviço | Porto | Função |
| :--- | :--- | :--- |
| NEXUS CORE | 8000 | Orquestrador central |
| ALQUIMIA | 8001 | Destilação e gestão de conhecimento |
| NEURO-TOXIN | 8002 | Processamento pesado |
| GLITCH | 8003 | Edge/fallback |
| OPTIMIZATION ENGINE | 8004 | Auto-otimização |

---

## 🛰️ NEXUS CORE v3.2.0 (O Cérebro Central)
O coração da operação, responsável pelo ingresso, classificação adaptativa, despacho de tarefas e orquestração de nós via Supra-Codex.

### 🧩 Nós de Processamento

1.  **🔵 SPECTRUM (ESPECTRO)**
    *   **Hardware**: Linux Node / RTX 3050.
    *   **Foco**: Eficiência, automação, Zenith Engine, scraping, monitoramento.
    *   **Responsabilidade**: Manutenção da infraestrutura e coleta de dados (LMArenaBridge).
    *   **NOVO**: Hospeda Zenith Automation para extração recursiva.

2.  **🔴 NEURO-TOXIN (NEURO-TOXINA)**
    *   **Hardware**: Cluster Ryzen 9 / RTX 3070.
    *   **Foco**: Processamento pesado, redes neurais, análise complexa.
    *   **Responsabilidade**: Execução de modelos locais e síntese de inteligência.
    *   **NOVO**: Recebe dispatch do Shadow Oracle.

3.  **🟡 GLITCH (Mobile/Edge)**
    *   **Hardware**: Mobile / Laptop / ROG Ally.
    *   **Foco**: Resiliência, interfaces rápidas, fallback.
    *   **Responsabilidade**: Ponto de acesso em campo e garantia de continuidade em caso de falha nos nós principais.

---

## 🛠️ Sistemas Especializados (Projeto 2.0)

### 🔥 ZENITH AUTOMATION v2.0
*   **Local**: SPECTRUM Node
*   **Função**: Extração Recursiva Total de conhecimento.
*   **Componentes**:
    *   `RecursiveExtractor`: Varredura em profundidade (max_depth=3).
    *   `URLDiscovery`: Descoberta de links de alta relevância (SOTA, benchmark).
    *   `SourceRanker`: Ranking de fontes por densidade de Néctar.
    *   `LMArenaBridge`: Captura de benchmarks SOTA.
*   **API**: Integrado ao NEXUS CORE via `/harvest`.

### 🌑 SHADOW MARKET ORACLE v2.0
*   **Local**: NEURO-TOXIN Node
*   **Função**: Intelligence de mercado com stealth avançado.
*   **Componentes**:
    *   `StealthLayer`: User-Agents dinâmicos + evasão de rate-limit.
    *   `MarketCorrelator`: Correlação notícias ↔ volatilidade.
    *   `NewsFeeder`: RSS feeds de mercados e tecnologia.
    *   `NeuroDispatcher`: Despacho para NEURO-TOXIN.
*   **Feeds**: CoinTelegraph, CoinDesk, CryptoPanic, LMSYS, HuggingFace, OpenAI.

### ⚗️ ALQUIMIA PROCESSAMENTO v1.0
*   **Local**: SPECTRUM Node (porta 8001)
*   **Função**: Destilação de dados e gestão de conhecimento escalável.
*   **Componentes**:
    *   `DataDistiller`: Multi-processing para latência zero.
    *   `RedisKnowledgeStore`: Armazenamento escalável (fallback: memória).
    *   `AlquimiaProcessor`: Orquestrador de processamento.
*   **Features**: Distillation, Knowledge Store, Synthesis.
*   **API REST**:
    *   `POST /distill`: Destila dados brutos.
    *   `POST /knowledge/store`: Armazena conhecimento.
    *   `GET /knowledge/search`: Busca conhecimento.
    *   `POST /synthesize`: Consolida Néctar.

### 🔄 OPTIMIZATION ENGINE v1.0
*   **Local**: NEXUS CORE (porta 8004)
*   **Função**: Loop de auto-otimização hiper-recursiva.
*   **Componentes**:
    *   `TelemetryCollector`: Coleta métricas de todos os nós.
    *   `GeminiAdvisor`: Análise via Gemini 1.5 Flash.
    *   `CodexMutator`: Aplica mudanças no Supra-Codex.
    *   `EvolutionTracker`: Rastreia evolução do sistema.
*   **Fluxo**: Telemetria → Análise → Mutação → Validação.
*   **Intervalo**: Configurável (default: 3600s = 1 hora).

---

## 🔄 Fluxo de Operação v2.0

```
1.  [INGRESS] Dados entram pelo endpoint /ingress
2.  [CLASSIFICAÇÃO] Gemini 1.5 Flash analisa o conteúdo baseado no protocolo Trindade
3.  [ZENITH HARVEST] /harvest executa Extração Recursiva Total
4.  [ALQUIMIA DISTILL] DataDistiller processa em paralelo via multi-processing
5.  [SHADOW INTEL] Shadow Oracle coleta feeds de mercado
6.  [MARKET CORRELATION] MarketCorrelator detecta anomalias
7.  [NEURO-TOXIN] Intel é despachada para processamento pesado
8.  [SINTETIZAR] Néctar é consolidado em blocos de conhecimento
9.  [EVOLUIR] Optimization Engine analisa e ajusta parâmetros
10. [MUTAR] Supra-Codex é atualizado com novas configurações
```

---

## 🛡️ Sistema de Proteção

### 🗡️ CARRASCO GUARD (Watchdog Darwiniano)
*   **Função**: Purga processos ineficientes e mantém higiene do sistema.
*   **Triggers**:
    *   CPU > 15% sem retorno.
    *   VRAM > 500MB em processos não-essenciais.
    *   Inatividade de arbitragem > timeout configurado.
*   **Proteção**: Não mata processos vitais (nexus_core.py, mag_service.py, sshd).

---

## 💎 Veredito: O Néctar da Margem Infinita v2.0

O **Projeto 2.0** representa a evolução do Império Mutante para uma **Fábrica Autônoma de Bio-Wealth**:

1. **Extração Recursiva Total**: Zenith Automation garante coleta constante de inteligência competitiva.
2. **Destilação de Conhecimento**: Alquimia Processamento transforma dados brutos em blocos acionáveis.
3. **Intelligence de Mercado**: Shadow Oracle correlaciona notícias com volatilidade para sinais de trading.
4. **Auto-Otimização**: Optimization Engine garante que o sistema evolua continuamente baseado em telemetria.
5. **Escalabilidade**: Redis + Multi-processing garantem latência zero mesmo com grandes volumes de dados.

O ativo de maior potencial de alavancagem continua sendo o **LMArenaBridge**, agora potencializado pela Extração Recursiva Total do Zenith e pela Destilação da Alquimia. O Império Mutante mantém uma vantagem competitiva perpétua, adaptando-se instantaneamente às mudanças no cenário global de IA e mercados.