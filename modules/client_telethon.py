#!/usr/bin/env python3
# A simple script to print all updates received

from getpass import getpass
from os import environ
import logging
import json
import re
from datetime import datetime
# environ is used to get API information from environment variables
# You could also use a config file, pass them as arguments,
# or even hardcode them (not recommended)
from packages.Telethon.telethon import TelegramClient
from packages.Telethon.telethon.errors import SessionPasswordNeededError
from packages.Telethon.telethon.tl.types import PeerUser, PeerChat, PeerChannel
from modules.flashpump import FlashPump
from modules.mongodb.mongodb import MongoDatabase
from modules.bittrex_api import *
from apscheduler.schedulers.background import BackgroundScheduler


logging.getLogger().setLevel(logging.INFO)
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = '194812'
api_hash = '7702fea03a54be4b9f575540421ed1f3'
user_phone = '+841683531320'
session_name = 'letegram_auth'

EVENTS={
    "UpdateReadHistoryInbox": False,
    "UpdateDeleteChannelMessages": False,
    "UpdateReadChannelInbox": False,
    "UpdateNewMessage": True,
    "UpdateReadHistoryOutbox": False,
    "UpdateChatUserTyping": False,
    "UpdateUserStatus": False,
    "UpdateNewChannelMessage": True
}

TRACKING_CHANNEL=[
    #"Cryptotguide", 
    "Tradingcryptocoach",
    "bottestchannel912"
]

NSIG_KEYS=[
    "ed ",
    "between",
    "hits",
    "achieve",
    "%"
]

SIG_KEYS=[
    "big",
    "news",
    "huge"
]

client = None
bot = None
MSG_BUFFER = []
MSG_COUNT = 0
CURRENCIES = []

class MyTelegramClient(object):
    def __init__(self, botwh):
        global client
        global bot
        global bittrex_v20_public_api
        global bittrex_v20_account_api

        bot = botwh
        client = TelegramClient(session_name,
                            api_id,
                            api_hash,
                            proxy=None,
                            update_workers=4)

        logging.info('INFO: Connecting to Telegram Servers...' )
        client.connect()
        logging.info('Done!')

        if not client.is_user_authorized():
            logging.info('INFO: Unauthorized user')
            client.send_code_request(user_phone)
            code_ok = False
            while not code_ok:
                code = input('Enter the auth code: ')
                try:
                    code_ok = client.sign_in(user_phone, code)
                except SessionPasswordNeededError:
                    password = getpass('Two step verification enabled. Please enter your password: ')
                    code_ok = client.sign_in(password=password)

        if not bittrex_v20_public_api:
            bittrex_v20_public_api = BittrexV20PublicAPI()
        if not bittrex_v20_account_api:
            bittrex_v20_account_api = BittrexV20AccountAPI()
        # Init coin list
        self.get_currencies()
        MongoDatabase.init()
        logging.info('INFO: Client initialized succesfully!')


    # Get all current supported currencies
    def get_currencies(self):
        logging.info("Getting bitttrex supported currencies...")
        result = bittrex_v20_public_api.get_currencies();
        if result.get("success"):
            for coin in result["result"]:
                if coin.get("Currency") not in ["TIME", "U", "BAY", "SOON"]:
                    CURRENCIES.append(' ' + coin.get("Currency").lower() + ' ')

        logging.info("Done.")

    def count_coin_1h():
        global MSG_BUFFER
        #print('Every 10 seconds')
        COIN_BUFFER = []
        now = datetime.now()

        if MSG_BUFFER == "":
            return

        print('[%s] Discovering most recent coins...' % str(now))

        for coin in CURRENCIES:
            count = 0
            for msg in MSG_BUFFER:
                if coin in msg.get('msg'):
                    count +=1
                    msg['save'] = True
                    msg['coins'].append(coin[1:-1])
            if count > 0:
                COIN_BUFFER.append({'coin': coin, 'count': count, 'time': now})

        # Save to db
        for msg in MSG_BUFFER:
            if msg.get('save'):
                MongoDatabase.insert_one('telegram_message', msg)

        for coin in COIN_BUFFER:
                print(str(coin))
                MongoDatabase.insert_one('coin_statistic', coin)

        COIN_BUFFER=[]
        MSG_BUFFER=[]

    def run(object):
        global client
        client.add_update_handler(update_handler)

        sched = BackgroundScheduler()
        # seconds can be replaced with minutes, hours, or days
        sched.add_job(MyTelegramClient.count_coin_1h, 'interval', seconds=300)
        sched.start()


        input('Press Enter to stop this!\n')

def update_handler(update):
    global bot
    global MSG_BUFFER

    if not EVENTS.get(update.__class__.__name__):
        return None
    else:
        if update.__class__.__name__ not in [ "UpdateNewChannelMessage" ]:
            return None

        # Get Message
        if hasattr(update.message, 'message'):
            message = update.message.message
        else:
            return None

        # Handle pumb signal
        pumb_msg, channel_name = is_pumb_message(update)
        if pumb_msg:
            # Extract signal
            signal = extract_signal(message)
            logging.info("Signal: " + str(signal))
            # Execute
            if signal != None:
                pump = FlashPump(bot, signal, "TEST")
                pump.jump_in()

        # Community attention level
        #logging.info("Channel message: %s" % message)
        if message != "":
            now = datetime.now()
            #now = '{:%B %d, %H:%M}'.format(now)
            MSG_BUFFER.append({ 'msg': ' ' + message.lower() + ' ', 'from': channel_name, 'time': now, 'coins': [] })

        return None

def is_pumb_message(update):
        global client
        if not hasattr(update.message, 'to_id'):
            return False
        try:
            # Get channel name
            channel_id = update.message.to_id.channel_id
            #logging.info("channel id = " + str(update.message))
            if str(channel_id) == "1147798110":
                channel_name = "Tradingcryptocoach"
            elif str(channel_id) == "1291260229":
                channel_name = "maynguoilinh2018"
            elif str(channel_id) == "1181052147":
                channel_name = "maygroup"
            else:
                channel = client.get_entity(PeerChannel(channel_id=channel_id))
                if not channel:
                    return False, None
                channel_name = channel.username
        except:
            logging.error("Cannot get channel:")
            logging.error(update)
            return False, None

        if channel_name not in TRACKING_CHANNEL:
            return False, channel_name

        # Ignore if it is a reply/forward message
        if hasattr(update.message, 'reply_to_msg_id'):
            if update.message.reply_to_msg_id != None:
                return False, channel_name

        if hasattr(update.message, 'fwd_from'):
            if update.message.fwd_from != None:
                return False, channel_name

        return True, channel_name

def extract_signal(message):
    if message == '':
        logging.warn("Message is empty.")
        return None
    else:
        message = message.lower()


    # Filter for special signal
    signal = re.search('Coin : (.+?) ', message + " ")
    if signal:
        return signal.group(1)


    # Filter message include number
    # Filter for non-signal
    for w in NSIG_KEYS:
        if w in message:
            #logging.warn("Non signal message: %s." % w)
            return None

    # Filter for signal
    for w in SIG_KEYS:
        if w in message:
            # Extract target
            if message.count('#') != 1:
                logging.warn("Many signal in a message")
                return None
            #logging.info(message)
            result = re.search('#(.+?) ', message + " ")
            if result:
                return result.group(1)

    #logging.info("No signal was found.")


if __name__ == '__main__':
    main()

