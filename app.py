import os
import requests
from flask import Flask, request
from openai import OpenAI
from moviescrapping import search_movies


app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("OPEN_AI_API_KEY")

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
                "👋 Hello and welcome to the Black Pearl Bot! 🏴‍☠️\n\n⚫ Powered by Black Pearl\n💬 Type /help to see all available commands.\n\n© Black Pearl — All Rights Reserved."
            )

        # /help
        elif text == "/help":

            send_message(
                chat_id,
                "Available commands:\n\n"
                "/start - Start the bot\n"
                "/help - Show help\n"
                "/openai YOUR_MESSAGE - chat with AI eg : /openai hello , /openai hi \n "
                "/movie MOVIE_NAME - send you a movie link (only 2026 released movies eg : /movie karuppu) \n"
            )

        # AI chat
        elif text.startswith("/openai"):
            message = text[len("/openai"):].strip()
            client = OpenAI(
                api_key=API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )

            #MODEL = "llama-3.3-70b-versatile"
            MODEL = "openai/gpt-oss-20b"
            response = client.responses.create(
                model=MODEL,
                input=message
            )
    
            send_message(
                chat_id,
                response.output_text
            )

        elif text.startswith("/movie"):
            message = text[len("/movie"):].strip()
            send_message(
                chat_id,
                main(message)
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
