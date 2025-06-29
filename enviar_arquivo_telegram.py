import os
import telebot

# Token e ID
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TOKEN)

def enviar_planilha_telegram(caminho_arquivo: str):
    try:
        with open(caminho_arquivo, 'rb') as f:
            bot.send_document(CHAT_ID, f, caption="📊 Planilha de Preços Atualizada!")
        print("✅ Arquivo enviado com sucesso pelo Telegram.")
    except Exception as e:
        print(f"❌ Falha ao enviar planilha: {e}")
