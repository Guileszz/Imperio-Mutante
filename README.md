# 🧬 Império-Mutante: NEXUS CORE v3.2.0

![Status](https://img.shields.io/badge/Status-Operacional-brightgreen)
![Version](https://img.shields.io/badge/Version-3.2.0-blue)
![Protocol](https://img.shields.io/badge/Protocol-Or%C3%A1culo-red)

> *"Na Margem Infinita, apenas o que muta sobrevive."*

## 🎯 Missão

O **Império-Mutante** é um ecossistema de inteligência artificial distribuída que opera na "Margem Infinita". 
A versão v3.2.0 consolida todos os módulos para operação completa:

- **ORÁCULO**: Comando & Controle via Telegram
- **NEXUS CORE**: Cérebro central com persistência SQLite
- **MAG Engine**: Coleta assíncrona de "Néctar" e benchmarks globais
- **Zenith Automation**: Automação recursiva de tarefas
- **Shadow Oracle**: Coleta furtiva de inteligência de mercado
- **Alquimia Processing**: Distilação e síntese de conhecimento
- **Carrasco Guard**: Proteção e monitoramento de segurança
- **Telemetry**: Coleta de métricas operacionais

## 🏗️ Arquitetura Consolidada (v3.2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                      NEXUS CORE v3.2.0                         │
│             (Cérebro Central + SQLite Persistence)              │
├──────────────────────┬───────────────────────┬──────────────────┤
│     ORÁCULO Bot      │      NodeManager      │    MAG Engine    │
│    (Telegram C2)     │    + Health Check     │    (Harvesting)  │
├──────────────────────┼───────────────────────┼──────────────────┤
│  ZENITH Automation   │   SHADOW ORACLE       │  ALQUIMIA Proc.  │
│  (Recursive Tasks)   │  (Market Intel)       │  (Distillation)  │
├──────────────────────┴───────────────────────┴──────────────────┤
│                    CARRASCO GUARD                               │
│                  (Security & Monitoring)                        │
├─────────────────────────────────────────────────────────────────┤
│                       TELEMETRY                                 │
│                    (Metrics & Stats)                            │
└─────────────────────────────────────────────────────────────────┘
           │                       │                    │
  ┌────────▼────────┐     ┌────────▼────────┐  ┌────────▼────────┐
  │  SPECTRUM Node  │     │NEURO-TOXIN Node │  │  GLITCH Node    │
  │  (Automation)   │     │ (Heavy Neural)  │  │   (Fallback)    │
  └─────────────────┘     └─────────────────┘  └─────────────────┘
```

## 🚀 Novos Recursos da Versão 3.2.0

- **C2 via Telegram**: Controle total do cluster via comandos `/apogeu`, `/carrasco`, `/status`
- **Persistência de Dados**: Histórico completo de tarefas e detecções salvo em SQLite
- **Notificações em Tempo Real**: Alertas instantâneos de "Néctar" e falhas críticas
- **Proxy Rotation**: ShadowCrawler utiliza lista de proxies para evitar detecção
- **Protocolo Néctar**: Detecção automática de mudanças no ranking LMSYS Arena
- **Zenith Automation**: Automação recursiva com profundidade configurável
- **Alquimia Processing**: Distilação e síntese de conhecimento coletado
- **Carrasco Guard**: Proteção e monitoramento de segurança em tempo real

## 📜 Grimório de Comandos (Telegram)

| Comando | Função |
|:--------|:-------|
| `/apogeu` | Ativa performance máxima e retorna status do cluster |
| `/carrasco` | Ciclo Darwinista (Purga de tarefas e processos) |
| `/status` | Exibe saúde dos nós e as últimas 5 tarefas do histórico |
| `/health` | Relatório rápido de telemetria e uptime |

## 🗂️ Estrutura de Arquivos

| Arquivo | Descrição |
|:--------|:----------|
| `nexus_core.py` | Cérebro central com persistência SQLite |
| `oracle_bot.py` | Interface Telegram para C2 |
| `mag_engine.py` | Motor de coleta assíncrona de benchmarks |
| `mag_service.py` | Serviço MAG com métricas em tempo real |
| `zenith_automation.py` | Automação recursiva de tarefas |
| `shadow_crawler.py` | Coletor furtivo com proxy rotation |
| `shadow_market_oracle.py` | Oráculo de mercado com análise de feeds |
| `alquimia_processing.py` | Distilação e síntese de conhecimento |
| `carrasco_guard.py` | Proteção e monitoramento de segurança |
| `telemetry.py` | Coleta de métricas operacionais |
| `optimization_engine.py` | Motor de otimização com mutação |
| `supra_codex.json` | Configuração centralizada do sistema |
| `MANUAL.md` | Documentação operacional completa |
| `SYSTEM_MAP.md` | Mapa do sistema e topologia |

## 🛠️ Instalação e Uso

```bash
pip install -r requirements.txt
# Configure seu .env com TELEGRAM_TOKEN e ALLOWED_LIST
python nexus_core.py
python oracle_bot.py
```

Consulte o [MANUAL.md](./MANUAL.md) para um guia detalhado de setup e operação.

---

*Mantido pelo Protocolo ORÁCULO - Império Mutante v3.2.0*
*Consolidado em: 2024-05-12*