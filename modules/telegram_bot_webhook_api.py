import telegram
import os, sys
from flask import Flask, request, render_template
import json
import logging
import subprocess

#sys.path.append(os.path.abspath(os.path.join('..')))

from modules.messager import Messager

#TODO Store key in database
# ezm
#MY_TELEGRAM_KEY="477813611:AAEgbjU4Bz2EUJvftW4RZuRPdoGoSzDTK4M" 
# telebit
MY_TELEGRAM_KEY="463733841:AAHURJK64srQaqVrnF9hf2iU5_BOG2SVbrc"
MY_TEST_CHANNEL_ID="1396402572"

class TelegramWebhookBot(object):
    def __init__(self):
        self.key = MY_TELEGRAM_KEY
        self.bot = telegram.Bot(token=self.key)
        self.https_app = Flask(__name__, template_folder='../templates')

        @self.https_app.route('/')
        def index(): #TODO fix issue of register by template
            try:
                cmd = [ 'bash', '-c', "scripts/register_telegram_bot_webhook.sh"]
                #proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
                #proc.wait()
                logging.debug('Registered webhok succesfully:\t%s' %cmd)
            except:
                logging.error('Can not run %s' % cmd)
                raise
            return render_template('upload_cert.html')

        @self.https_app.route('/webhook', methods=['POST'])
        def webhook_handler(self=self):
            if request.method == "POST":
                # retrieve the message in JSON and then transform it to Telegram object
                update = telegram.Update.de_json(request.get_json(force=True), self.bot)

                messager = Messager(update)
                chat_id, result = messager.execute_command()

            #if "Most recent" in result:
                #self.bot.sendMessage(chat_id=MY_TEST_CHANNEL_ID, text=str(result))
            if chat_id:
                self.bot.sendMessage(chat_id=chat_id, text=str(result))
            else:
                pass

            return 'ok'

    def parse_message(self):
        # extract and filter information 
        pass

    def send_message(self, chat_id, result):
        self.bot.sendMessage(chat_id=chat_id, text=result)

    def run(self):
        logging.info("Please access https:<domain>/ to register webhook portal for udpates!")
        self.https_app.run(host='0.0.0.0', port='443', ssl_context=('ssl/public.pem', 'ssl/private.key'))
        #self.https_app.run(port='80')

