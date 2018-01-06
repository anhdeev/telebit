#!/usr/bin/env python3
# A simple script to print all updates received

from getpass import getpass
from os import environ
import logging
import json
import re
# environ is used to get API information from environment variables
# You could also use a config file, pass them as arguments,
# or even hardcode them (not recommended)
from packages.Telethon.telethon import TelegramClient
from packages.Telethon.telethon.errors import SessionPasswordNeededError
from packages.Telethon.telethon.tl.types import PeerUser, PeerChat, PeerChannel
from modules.flashpump import FlashPump
logging.getLogger().setLevel(logging.INFO)

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

class MyTelegramClient(object):
    def __init__(self, botwh):
        global client
        global bot

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
        logging.info('INFO: Client initialized succesfully!')

    def run(object):
        global client
        client.add_update_handler(update_handler)
        input('Press Enter to stop this!\n')

def update_handler(update):
    global bot

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
        if is_pumb_message(update):
            # Extract signal
            signal = extract_signal(message)
            logging.info("Signal: " + str(signal))
            # Execute
            if signal != None:
                pump = FlashPump(bot, signal, "TEST")
                pump.jump_in()

        # Community attention level
        #logging.info("Channel message: %s" % message)

        return None

def is_pumb_message(update):
        global client
        if not hasattr(update.message, 'to_id'):
            return False
        try:
            # Get channel name
            channel_id = update.message.to_id.channel_id
            #logging.info("channel id = " + str(channel_id))
            if str(channel_id) == "1147798110":
                channel_name = "Tradingcryptocoach"
            elif str(channel_id) == "1291260229":
                channel_name = "maynguoilinh2018"
            else:
                channel = client.get_entity(PeerChannel(channel_id=channel_id))
                if not channel:
                    return False
                channel_name = channel.username
        except:
            logging.error("Cannot get channel:")
            logging.error(update)
            return False

        if channel_name not in TRACKING_CHANNEL:
            return False

        # Ignore if it is a reply/forward message
        if hasattr(update.message, 'reply_to_msg_id'):
            if update.message.reply_to_msg_id != None:
                return False

        if hasattr(update.message, 'fwd_from'):
            if update.message.fwd_from != None:
                return False

        return True

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

