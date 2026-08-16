import os
from flask import Flask, request
import telebot

app = Flask(__name__)

# Get Telegram Bot Token from Render Environment Variable
TOKEN = os.environ.get("BOT_TOKEN")

print("=================================")
print("Telegram Bot Starting...")
print("TOKEN LOADED:", bool(TOKEN))
print("=================================")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

bot = telebot.TeleBot(TOKEN)


# /start command
@bot.message_handler(commands=["start"])
def start(message):
    print("START command received")
    print("Chat ID:", message.chat.id)

    bot.send_message(
        message.chat.id,
        "Hello 👋\nWelcome to my Telegram bot!"
    )


# /help command
@bot.message_handler(commands=["help"])
def help_command(message):
    print("HELP command received")

    bot.send_message(
        message.chat.id,
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show help"
    )


# Handle normal messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print("Message received:", message.text)
    print("Chat ID:", message.chat.id)

    bot.send_message(
        message.chat.id,
        "You said: " + str(message.text)
    )


# Home page
@app.route("/", methods=["GET"])
def home():
    return "Telegram Bot is running!", 200


# Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():

    print("=================================")
    print("WEBHOOK RECEIVED")
    print("=================================")

    try:
        data = request.get_json()

        print("Telegram Data:")
        print(data)

        if not data:
            print("No JSON data received")
            return "No data", 400

        update = telebot.types.Update.de_json(data)

        bot.process_new_updates([update])

        print("Update processed successfully")

        return "OK", 200

    except Exception as e:
        print("ERROR:", str(e))
        return "Error", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    print("Starting Flask server...")
    print("Port:", port)

    app.run(
        host="0.0.0.0",
        port=port
    )
