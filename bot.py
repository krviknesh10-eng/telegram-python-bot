import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello! 👋 Welcome to my bot.")

@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(message, "Send me any message and I will reply!")

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.reply_to(message, "You said: " + message.text)

print("Bot is running...")

bot.infinity_polling()
