import os
import asyncio
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Configuração de Logging
logging.basicConfig(
    format='%(asctime)s - ORÁCULO - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("ORÁCULO")

TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USERS = [int(uid) for uid in os.getenv("ALLOWED_LIST", "").split(",") if uid]
NEXUS_CORE_URL = os.getenv("NEXUS_CORE_URL", "http://localhost:8000")

async def is_authorized(update: Update) -> bool:
    if not ALLOWED_USERS:
        return True
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Acesso negado. Você não é um operador autorizado.")
        logger.warning(f"Tentativa de acesso não autorizado: {user_id}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text(
        "👁️ Oráculo Ativo. Sistema de Comando & Controle Império Mutante.\n"
        "Comandos disponíveis:\n"
        "/apogeu - Status do Cluster e Performance\n"
        "/carrasco - Executar Purga de Processos\n"
        "/status - Últimas tarefas e detecções\n"
        "/health - Verificação de saúde dos nós"
    )

async def apogeu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{NEXUS_CORE_URL}/command", json={"command": "/APOGEU"})
            data = resp.json()
            await update.message.reply_text(f"🚀 {data.get('message', 'Comando executado')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao contatar NEXUS CORE: {e}")

async def carrasco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{NEXUS_CORE_URL}/command", json={"command": "/CARRASCO"})
            data = resp.json()
            await update.message.reply_text(f"💀 {data.get('message', 'Purga executada')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao contatar NEXUS CORE: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    try:
        async with httpx.AsyncClient() as client:
            # Pegar status do Nexus Core (será expandido com SQLite)
            resp = await client.get(f"{NEXUS_CORE_URL}/health")
            data = resp.json()
            
            status_text = "📊 STATUS ATUAL DO CLUSTER\n\n"
            for node, info in data.get("nodes", {}).items():
                status_text += f"🔹 {node}: {info.get('status')} ({info.get('latency_ms', 0):.2f}ms)\n"
            
            # Adicionar histórico de tarefas (via novo endpoint no nexus_core)
            resp_tasks = await client.get(f"{NEXUS_CORE_URL}/history?limit=5")
            if resp_tasks.status_code == 200:
                history = resp_tasks.json()
                status_text += "\n📜 ÚLTIMAS TAREFAS:\n"
                for t in history:
                    status_text += f"▪️ {t['task_id'][:8]}: {t['status']} ({t['node']})\n"
            
            await update.message.reply_text(status_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao obter status: {e}")

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{NEXUS_CORE_URL}/health")
            data = resp.json()
            await update.message.reply_text(f"🍏 SAÚDE: {data.get('status')}\nUptime: {data.get('telemetry', {}).get('uptime', 0):.0f}s")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")

if __name__ == '__main__':
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN não configurado no .env")
        exit(1)
        
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('apogeu', apogeu))
    application.add_handler(CommandHandler('carrasco', carrasco))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('health', health))
    
    logger.info("Bot Oráculo iniciado...")
    application.run_polling()
