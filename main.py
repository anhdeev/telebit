#!/usr/bin/env python
import os
import json
import logging
import threading

from modules.telegram_bot_webhook_api import TelegramWebhookBot
from modules.client_telethon import MyTelegramClient
from modules.bittrex_api import load_api_key_for_the_first_run

logging.getLogger().setLevel(logging.INFO)

bot = TelegramWebhookBot()
client = MyTelegramClient(bot)

INIT_KEY=False

def run_bot():
    global bot
    bot.run()

def run_client():
    global client
    client.run()

if __name__ == "__main__":
    if INIT_KEY:
        load_api_key_for_the_first_run()
    else:
        b = threading.Thread(name='bot', target=run_bot)
        c = threading.Thread(name='client', target=run_client)

        b.start()
        c.start()
