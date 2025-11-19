# Complex Telegram Bot

Bot avançado do Telegram com múltiplos provedores de IA (OpenRouter, HuggingFace, Gemini), sistema de fallback, cache de respostas, rate limiting, histórico de conversas com SQLite, e suporte a plugins.

## Funcionalidades

- ✅ **Múltiplos provedores de IA** com fallback automático
- ✅ **Cache de respostas** para otimizar requisições
- ✅ **Rate limiting** por chat
- ✅ **Histórico de conversas** persistente com SQLite
- ✅ **Sistema de plugins** extensível
- ✅ **Webhook** para deploy em produção
- ✅ **Docker** para containerização
- ✅ **Comandos admin** para monitoramento

## Estrutura do Projeto

```
complex_telegram_bot/
├── main.py                    # Arquivo principal com bot e webhook
├── ai_providers.py            # Provedores de IA (OpenRouter, HF, Gemini)
├── agents.py                  # Gerenciador de agentes com fallback
├── db.py                      # Funções do banco de dados SQLite
├── utils.py                   # Utilitários (cache, rate limiting)
├── plugins/                   # Pasta de plugins
│   └── example_plugin.py      # Plugin de exemplo
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Containerização
├── Procfile                   # Deploy em plataformas como Railway
├── .env.example               # Exemplo de variáveis de ambiente
├── README.md                  # Este arquivo
└── UPLOADED_SOURCE_PATH.txt   # Referência ao arquivo original
```

## Configuração

1. **Clone ou extraia o projeto**

2. **Configure as variáveis de ambiente** copiando `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Preencha as variáveis necessárias** no arquivo `.env`:
   - `TELEGRAM_TOKEN`: Token do bot do Telegram (obtenha com @BotFather)
   - `AI_PROVIDER`: Provedor primário (`openrouter`, `huggingface`, ou `gemini`)
   - `OPENROUTER_KEY`: Chave da API OpenRouter
   - `HF_TOKEN` e `HF_MODEL`: Token e modelo do HuggingFace
   - `GEMINI_KEY`: Chave da API Gemini
   - `BASE_URL`: URL pública do seu deploy (para webhook)
   - `ADMINS`: IDs dos administradores separados por vírgula

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o bot**:
   ```bash
   python main.py
   ```

## Deploy

### Railway / Render / Heroku

1. Faça push do projeto para um repositório Git
2. Conecte o repositório na plataforma
3. Configure as variáveis de ambiente
4. A plataforma detectará o `Procfile` e `requirements.txt` automaticamente

### Docker

```bash
docker build -t telegram-bot .
docker run -p 8080:8080 --env-file .env telegram-bot
```

## Comandos do Bot

- `/start` - Inicia o bot
- `/help` - Lista os comandos disponíveis
- `/history` - Mostra as últimas 20 mensagens do chat
- `/admin_stats` - Estatísticas (apenas para admins)

## Plugins

Para criar um plugin personalizado, adicione um arquivo `.py` na pasta `plugins/` com a seguinte estrutura:

```python
async def on_message(app, update, context):
    text = update.message.text or ''
    if text.strip().lower() == 'seu_comando':
        await update.message.reply_text('Sua resposta')
        return True  # Plugin tratou a mensagem
    return False  # Continuar processamento normal
```

## Licença

MIT License - Use livremente!
