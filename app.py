import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

print("=================================")
print("Telegram Bot Starting...")
print("TOKEN LOADED:", bool(TOKEN))
print("=================================")


def send_message(chat_id, text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, json=data)

    print("Telegram API Status:", response.status_code)
    print("Telegram API Response:", response.text)

    return response


@app.route("/", methods=["GET"])
def home():
    return "Telegram Bot is running!", 200


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
            return "No data", 400

        message = data.get("message")

        if not message:
            print("No message found")
            return "OK", 200

        chat = message.get("chat")
        chat_id = chat.get("id")

        text = message.get("text", "")

        print("Chat ID:", chat_id)
        print("Message:", text)

        # /start
        if text == "/start":

            print("START command received")

            send_message(
                chat_id,
                "Hello 👋\nWelcome to my Telegram bot!"
            )

        # /help
        elif text == "/help":

            send_message(
                chat_id,
                "Available commands:\n\n"
                "/start - Start the bot\n"
                "/help - Show help"
            )

        # Normal message
        else:

            send_message(
                chat_id,
                "You said: " + text
            )

        return "OK", 200

    except Exception as e:

        print("ERROR:", str(e))

        return "Error", 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
