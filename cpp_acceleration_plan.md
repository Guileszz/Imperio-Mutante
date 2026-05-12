# Plano de Aceleração: C++/Mojo Transition (Darwinismo Técnico)

Este documento detalha o plano de refatoração do **NEXUS CORE** e **MAG ENGINE** para superar os limites de performance do Python e atingir latência de nanossegundos.

## 1. Gargalos Identificados

### A. Nexus Core (Orquestração)
- **Overhead do FastAPI/Python**: A pilha HTTP do Python introduz latência de milissegundos que é inaceitável para arbitragem de alta frequência (HFT).
- **GIL (Global Interpreter Lock)**: O roteamento inteligente e a classificação via Gemini (mesmo assíncrona) podem saturar a thread principal durante picos de mercado.
- **Serialização JSON**: O custo de transformar dicionários Python em JSON para cada tarefa entre nós consome ciclos valiosos de CPU.

### B. Mag Engine (Coleta e Processamento)
- **I/O Bloqueante**: Embora use `httpx`, o gerenciamento de milhares de conexões simultâneas para scraping massivo satura o event loop.
- **Parsing de Dados**: O processamento de grandes volumes de HTML/JSON em Python é lento comparado a implementações de baixo nível.

---

## 2. Estratégia de Refatoração

### Fase 1: Introdução do Mojo (Processamento de Dados)
- **O que é**: Mojo combina a sintaxe do Python com a performance do C++.
- **Aplicação**: 
    - Migrar as funções de detecção de anomalias (`detect_glitch`) de `mag_service.py` para Mojo.
    - Utilizar **SIMD (Single Instruction, Multiple Data)** para processar vetores de preços em paralelo.
    - Implementar a lógica de classificação neural local no Mojo para aproveitar aceleração de hardware sem a latência da API externa.

### Fase 2: Core em C++ (Roteamento de Baixa Latência)
- **O que é**: Substituir o núcleo do servidor por uma solução em C++.
- **Aplicação**:
    - Reescrever o roteador `/ingress` usando **Drogon** ou **Crow** (C++ Frameworks).
    - Usar **ZeroMQ** ou **Shared Memory** para comunicação entre o `nexus_core` e o `carrasco_guard`, eliminando o overhead de rede local.
    - Implementar pool de conexões WebSockets em C++ para o `mag_service`.

### Fase 3: Integração Híbrida (Python como Interface)
- Manter o Python apenas para a camada de comando de alto nível (Grimório) e interface com o usuário, chamando os binários otimizados via CFFI ou extensões nativas.

---

## 3. Cronograma de Implementação (Prioridades)

1. **Prioridade 1 (Imediata)**: Refatorar `detect_glitch` para C++ e expor via Python Binding. Redução esperada de 90% na latência de detecção.
2. **Prioridade 2 (Curto Prazo)**: Implementar buffer de memória compartilhada para telemetria e logs, reduzindo uso de disco e IOPS.
3. **Prioridade 3 (Médio Prazo)**: Migrar `shadow_crawler` para um motor assíncrono baseado em C++ (libcurl-multi) para suportar 10x mais fontes simultâneas.

---

## 4. Métricas de Sucesso
- Latência interna do roteador < 500 microsegundos.
- Consumo de CPU por tarefa reduzido em 40%.
- Capacidade de processar > 100.000 eventos de mercado por segundo em um único nó SPECTRUM.
