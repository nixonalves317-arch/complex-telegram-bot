# Exemplo de plugin simples
async def on_message(app, update, context):
    # Chamado pelo bot para cada mensagem recebida (antes do processamento principal).
    text = update.message.text or ''
    if text.strip().lower() == 'ping':
        await update.message.reply_text('pong (plugin)')
        return True  # indica que plugin lidou com a mensagem
    return False
