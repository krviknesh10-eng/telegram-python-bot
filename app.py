import os
from flask import Flask, request
import telebot

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello 👋 Welcome to my bot!")


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(message, "Send me any message!")


@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.reply_to(message, "You said: " + message.text)


@app.route("/")
def home():
    return "Telegram Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")

    update = telebot.types.Update.de_json(json_string)

    bot.process_new_updates([update])

    return "OK", 200
