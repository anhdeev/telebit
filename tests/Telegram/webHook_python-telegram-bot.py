#!/usr/bin/env python
import os
import telegram
from flask import Flask, request, render_template
import json

app = Flask(__name__)

MY_TELEGRAM_KEY="477813611:AAEgbjU4Bz2EUJvftW4RZuRPdoGoSzDTK4M"
global bot
bot = telegram.Bot(token=MY_TELEGRAM_KEY)


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    print("Incomming Request Type: %s" % request.method)
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        #chat_id = update.message.chat.id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        if update.channel_post:
            if update.channel_post.text:
                text = update.channel_post.text.encode('utf-8')
                print('channel post=%s' % text)

        if update.message:
            if update.message.text:
                text = update.message.text.encode('utf-8')
                print('message=%s' % text)
        # repeat the same message back (echo)
        #bot.sendMessage(chat_id=chat_id, text="Done.")

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://35.197.140.7:443/webhook')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return render_template('upload_cert.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='443', ssl_context=('public.pem', 'private.key'))

