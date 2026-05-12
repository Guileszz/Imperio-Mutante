# 📖 MANUAL OPERACIONAL: IMPÉRIO-MUTANTE (v3.2.0)

## 🌌 Resumo Executivo: Soberania de Dados e Arbitragem Global

O **Império-Mutante** é um ecossistema de inteligência artificial soberana projetado para a **Margem Infinita**. 
A versão 3.2.0 consolida todos os módulos: Nexus Core, MAG Engine, Zenith Automation, 
Shadow Oracle, Alquimia Processing, Carrasco Guard e Telemetry.

### O que o projeto faz?
1. **Soberania de Dados:** Processamento distribuído entre nós locais (NEURO-TOXIN, SPECTRUM, GLITCH) e nuvem.
2. **Comando & Controle (ORÁCULO):** Interface via Telegram para monitoramento e execução de comandos remotos.
3. **Persistência Resiliente:** Armazenamento local via SQLite para histórico de tarefas e detecções do MAG Engine.
4. **Arbitragem Global de Inteligência:** Utiliza o motor MAG Engine para monitorar benchmarks globais e selecionar o melhor provedor.
5. **Alquimia Processing:** Distilação e síntese de conhecimento coletado.
6. **Zenith Automation:** Automação de tarefas recorrentes com profundidade recursiva.
7. **Shadow Oracle:** Coleta furtiva de inteligência de mercado e tecnologia.
8. **Carrasco Guard:** Proteção e monitoramento de segurança em tempo real.
9. **Telemetry:** Coleta de métricas e telemetria operacional.

---

## 🛠️ Guia de Uso Passo a Passo

### 1. Setup Local
```bash
# Instale as dependências
pip install -r requirements.txt

# Configure o .env
echo "GEMINI_API_KEY=sua_chave" >> .env
echo "TELEGRAM_TOKEN=seu_token_do_bot" >> .env
echo "TELEGRAM_CHAT_ID=seu_chat_id" >> .env
echo "ALLOWED_LIST=seu_user_id" >> .env
```

### 2. Iniciando o Sistema
Para operação total, inicie o NEXUS CORE e o ORÁCULO:

```bash
# Terminal 1: Cérebro Central
python nexus_core.py

# Terminal 2: Interface Telegram (C2)
python oracle_bot.py

# Terminal 3: Coletor Furtivo (Opcional)
python shadow_crawler.py

# Terminal 4: Automação Zenith (Opcional)
python zenith_automation.py

# Terminal 5: Alquimia Processing (Opcional)
python alquimia_processing.py
```

### 3. Comandos do Oráculo (Telegram)
Interaja diretamente com o cluster através do seu bot:
- `/start`: Inicia a interface e lista comandos.
- `/apogeu`: Ativa modo de alta performance e retorna status.
- `/carrasco`: Executa o ciclo de purga de processos.
- `/status`: Exibe a saúde dos nós e as últimas 5 tarefas do banco de dados.
- `/health`: Telemetria rápida do sistema.

---

## 🛰️ Módulo ORÁCULO (Telegram C2)
O Oráculo permite que você controle o Império Mutante de qualquer lugar. Ele é protegido por uma `ALLOWED_LIST`, garantindo que apenas operadores autorizados enviem comandos.

### Notificações Automáticas
O sistema enviará alertas para o Telegram sempre que:
- Uma tarefa de alta prioridade for concluída.
- Uma falha crítica ocorrer em qualquer nó.
- O MAG Engine detectar "Néctar" de alta relevância (benchmarks novos).

---

## 🕵️ Shadow Crawler & Proxy Rotation
O `shadow_crawler.py` agora suporta rotação de proxies configuráveis no `supra_codex.json`. Isso aumenta a furtividade e evita bloqueios durante a coleta de inteligência competitiva.

---

## ⚗️ Alquimia Processing
O módulo de Alquimia processa o "Néctar" coletado, realizando:
- **Distilação**: Extração de conhecimento puro de fontes brutas.
- **Síntese**: Consolidação de informações em blocos coerentes.
- **Armazenamento**: Persistência em loja de conhecimento local.

---

## 🤖 Zenith Automation
Automação de tarefas recorrentes com:
- Profundidade recursiva configurável (padrão: 3)
- Máximo de URLs por execução (padrão: 50)
- Priorização por palavras-chave de alta relevância (SOTA, benchmark, ranking)
- Sistema de pesos por fonte para relevância.

---

## 🛡️ Carrasco Guard
Sistema de proteção e monitoramento:
- Detecção de anomalias em tempo real
- Purga de processos zumbis
- Ciclo Darwinista de manutenção
- Alertas de segurança instantâneos

---

## 📊 Telemetry
Coleta de métricas operacionais:
- Uso de CPU e memória
- Latência de rede
- Status de nós
- Métricas de performance

---

## 🚀 Próxima Expansão: Darwinian Modules
O futuro do Império-Mutante está na automação total da inteligência e auto-reparo de módulos em runtime.

---

*Documentação Gerada pelo Protocolo ORÁCULO - v3.2.0*
*Consolidado em: 2024-05-12*