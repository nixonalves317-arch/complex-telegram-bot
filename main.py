import os
import logging
import asyncio
import importlib
import glob

from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from agents import AgentManager
from db import init_db, save_message, get_history
from utils import cache, TokenBucket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error('TELEGRAM_TOKEN não definido. Pare o processo e defina a variável.')

PORT = int(os.getenv('PORT', 8080))
BASE_URL = os.getenv('BASE_URL') or os.getenv('RAILWAY_URL') or os.getenv('RAILWAY_STATIC_URL') or ''
SQLITE_DB = os.getenv('SQLITE_DB', 'bot_data.sqlite3')

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

agent = AgentManager()

# carregar plugins
PLUGINS = []
for f in glob.glob('plugins/*.py'):
    name = f.replace('/', '.').rstrip('.py')
    module = importlib.import_module(name)
    PLUGINS.append(module)
    logger.info('Plugin carregado: %s', name)

token_buckets = {}  # chat_id -> TokenBucket

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá! Bot avançado ativo. Use /help para comandos.')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/help - lista comandos\n/admin_stats - estatísticas (se for admin)\n/history - mostra últimas mensagens')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admins = os.getenv('ADMINS','').split(',')
    if str(user.id) not in admins:
        await update.message.reply_text('Acesso negado.')
        return
    await update.message.reply_text('OK, estou vivo. Consulte logs para detalhes.')

async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = await get_history(chat_id, limit=20)
    if not rows:
        await update.message.reply_text('Sem histórico.')
        return
    text = "\n".join([f"{r[0]}: {r[1]}" for r in rows])
    await update.message.reply_text(f'Últimas mensagens:\n{text}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (update.message.text or '').strip()
    if not text:
        return

    # Pre-plugin hooks
    for p in PLUGINS:
        try:
            ok = await p.on_message(application, update, context)
            if ok:
                return
        except Exception:
            logger.exception('plugin error')

    # rate limit por chat
    tb = token_buckets.get(chat_id)
    if not tb:
        tb = TokenBucket()
        token_buckets[chat_id] = tb
    if not tb.consume():
        await update.message.reply_text('🚫 Limite de requisições atingido, tenta de novo mais tarde.')
        return

    # salvar input
    await save_message(chat_id, 'user', text)

    # montar contexto (histórico curto)
    history = await get_history(chat_id, limit=6)
    context_prompt = '\n'.join([f"{r[0]}: {r[1]}" for r in history])
    prompt = f"Context: {context_prompt}\nUser: {text}\nAssistant:"

    # cache
    cached = cache.get(prompt)
    if cached:
        await update.message.reply_text(cached + '\n\n(Resposta em cache)')
        await save_message(chat_id, 'assistant', cached)
        return

    # chamada AI (executor para não bloquear loop principal)
    loop = asyncio.get_event_loop()
    try:
        resp = await loop.run_in_executor(None, agent.ask, prompt)
    except Exception:
        logger.exception('Falha ao chamar provedor de IA')
        await update.message.reply_text('Erro ao processar sua mensagem. Tente novamente mais tarde.')
        return

    # salvar e responder
    await save_message(chat_id, 'assistant', resp)
    cache.set(prompt, resp, ttl=60*5)
    await update.message.reply_text(resp)

# webhook endpoint
@app.route(f'/webhook/<token>', methods=['POST'])
def webhook(token):
    if token != TELEGRAM_TOKEN:
        return jsonify({'ok': False, 'error': 'invalid token'}), 403
    update = Update.de_json(request.json, bot)
    application.process_update(update)
    return jsonify({'ok': True})

async def set_webhook():
    if not BASE_URL:
        logger.warning('BASE_URL não definido — pulei set_webhook automático.')
        return
    url = f"{BASE_URL.rstrip('/')}/webhook/{TELEGRAM_TOKEN}"
    logger.info('Setting webhook to %s', url)
    await bot.set_webhook(url=url)

def run_app():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    import asyncio
    asyncio.run(init_db())
    # handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_cmd))
    application.add_handler(CommandHandler('admin_stats', admin_stats))
    application.add_handler(CommandHandler('history', history_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # set webhook if possible
    if BASE_URL:
        asyncio.get_event_loop().run_until_complete(set_webhook())
    run_app()
