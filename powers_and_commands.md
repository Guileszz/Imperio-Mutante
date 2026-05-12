# 📜 Grimório de Comandos: Protocolo Néctar Supremo v2.0

Este documento detalha os comandos de alto impacto para controle e otimização do **NEXUS CORE v3.2.0**.

---

## ⚡ Comandos de Poder Soberano

### 1. `/APOGEU`
*   **Descrição**: Ativa o modo de performance máxima do sistema.
*   **Gatilho**: Necessidade de processamento imediato para eventos de mercado de alta volatilidade ou tarefas críticas de síntese.
*   **Efeito**: 
    *   Priorização absoluta de CPU para processos do NEXUS.
    *   Redução de timeouts de API.
    *   Alocação total de VRAM no nó NEURO-TOXIN.
    *   `max_concurrent_tasks` → 1000

### 2. `/CARRASCO`
*   **Descrição**: O exterminador de ineficiência - Darwinismo sistêmico.
*   **Gatilho**: Detecção de processos parasitas consumindo > 15% de CPU/RAM.
*   **Efeito**: 
    *   Varredura instantânea de processos.
    *   Finalização forçada de qualquer tarefa não essencial.
    *   Liberação de buffers de memória.
    *   Purga de tarefas órfãs.

### 3. `/MUTAR`
*   **Descrição**: Preparação para transição de estado e atualização do Supra-Codex.
*   **Gatilho**: Pré-instalação de novas lógicas ou migração entre nós.
*   **Efeito**: 
    *   Recarrega configurações do `supra_codex.json`.
    *   Limpa caches temporários.
    *   Reinicialização controlada de workers assíncronos.

### 4. `/SOBERANIA`
*   **Descrição**: Relatório completo de status do sistema.
*   **Gatilho**: Necessidade de visão panorâmica do Império.
*   **Efeito**: Retorna telemetria completa, métricas de nós e estado operacional.

---

## 🚀 Comandos de Extração Recursiva (Projeto 2.0)

### 5. `/EVOLUIR` 🆕
*   **Descrição**: Dispara o ciclo de **Auto-Otimização Hiper-Recursiva**.
*   **Gatilho**: Necessidade de ajuste automático de parâmetros baseado em telemetria.
*   **Efeito**:
    *   Coleta telemetria de todos os nós.
    *   Envia métricas ao Gemini 1.5 Flash para análise.
    *   Recebe recomendações de ajuste de parâmetros.
    *   Aplica mutações no `supra_codex.json`.
    *   Valida mudanças e registra no log de evolução.
*   **Intervalo**: Pode ser disparado manualmente ou automaticamente (a cada 1 hora).
*   **Cuidado**: Pode consumir muitos tokens de API.

### 6. `/SINTETIZAR` 🆕
*   **Descrição**: Consolida o Néctar colhido em **blocos de conhecimento** unificados.
*   **Gatilho**: Após coleta massiva de dados ou antes de decisões importantes.
*   **Efeito**:
    *   Agrega entidades (modelos, métricas, links) de múltiplas fontes.
    *   Destila informações relevantes.
    *   Armazena na base de conhecimento da Alquimia.
    *   Gera relatório consolidado em Markdown.
*   **Dependência**: Requer serviço Alquimia ativo (`http://localhost:8001`).

### 7. `/HARVEST` 🆕
*   **Descrição**: Coleta Néctar de fontes configuradas usando Zenith Automation.
*   **Gatilho**: Necessidade de atualização de inteligência competitiva.
*   **Efeito**:
    *   Executa **Extração Recursiva Total** nas fontes LMSYS, HuggingFace, etc.
    *   Descobre links de alta relevância (SOTA, benchmark, leaderboard).
    *   Rankings de fontes por densidade de Néctar.
    *   Armazena no histórico de Néctar.
*   **Parâmetros**:
    *   `sources`: Lista opcional de URLs.
    *   `recursive`: True por padrão (profundidade de 3 níveis).
    *   `max_depth`: Limite de profundidade (default: 3).

### 8. `/INTELIGENCE` 🆕
*   **Descrição**: Coleta inteligência de mercado via Shadow Oracle.
*   **Gatilho**: Necessidade de análise de sentimentos e correlação com volatilidade.
*   **Efeito**:
    *   Coleta feeds RSS de mercados (CoinTelegraph, CoinDesk, CryptoPanic).
    *   Coleta feeds de tecnologia (LMSYS, HuggingFace, OpenAI).
    *   Análise de sentimento das notícias.
    *   Correlação com volatilidade de mercado.
    *   Despacho de intel para nó NEURO-TOXIN.
*   **Modo Stealth**: User-Agents dinâmicos e delays adaptativos para evitar bloqueios.

---

## 🛠️ Triggers de Execução Automática

| Condição | Comando Automático |
| :--- | :--- |
| Latência API > 3.0s | `/MUTAR` (Switch para Local) |
| Uso de CPU por terceiros > 50% | `/CARRASCO` |
| Volume de Néctar > 1GB/hora | `/APOGEU` |
| A cada 1 hora | `/EVOLUIR` (se optimization_engine ativo) |
| Néctar coletado > 10 fontes | `/SINTETIZAR` |

---

## 🔄 Fluxo de Execução do Néctar v2.0

```
[INGRESS] → [CLASSIFICAÇÃO] → [ZENITH HARVEST] → [ALQUIMIA DISTILL]
                                      ↓                    ↓
                              [SHADOW ORACLE]     [KNOWLEDGE STORE]
                                      ↓                    ↓
                              [MARKET CORRELATION]   [SYNTHESIS]
                                      ↓                    ↓
                              [NEURO-TOXIN DISPATCH] → [SINTETIZAR]
```

---

## 💎 Top 5 Comandos de Alto Impacto

1.  **`/EVOLUIR`**: A peça central do Projeto 2.0. Garantia de auto-otimização contínua do sistema.
2.  **`/HARVEST`**: Extração Recursiva Total para alimentação constante de inteligência competitiva.
3.  **`/SINTETIZAR`**: Transformação de dados brutos em conhecimento destilado e acionável.
4.  **`/CARRASCO`**: Vital para manter a higidez do ambiente de execução.
5.  **`/APOGEU`**: Garante a Margem Infinita durante picos de oportunidade.

---

## 📡 Endpoints REST Complementares

| Método | Endpoint | Função |
| :--- | :--- | :--- |
| POST | `/harvest` | Coleta Néctar |
| POST | `/distill` | Destila dados |
| GET | `/nectar/history` | Histórico de Néctar |
| GET | `/market/intel` | Inteligência de mercado |
| GET | `/optimization/log` | Log de otimizações |
| POST | `/oracle/notification` | webhook para notificações |

---

## 🎯 Prioridades de Execução

1. **Crítico**: `/CARRASCO` - Se CPU > 80% ou memória > 90%
2. **Alta**: `/EVOLUIR` - Se latência > 2000ms ou success_rate < 0.9
3. **Média**: `/HARVEST` - A cada 5 minutos durante horário de mercado
4. **Normal**: `/SINTETIZAR` - Quando Néctar acumulado > 20 blocos
5. **Batch**: `/INTELIGENCE` - A cada 15 minutos para feeds de notícias