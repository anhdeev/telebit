#!/usr/bin/env python3
# A simple script to print all updates received

from getpass import getpass
from os import environ
# environ is used to get API information from environment variables
# You could also use a config file, pass them as arguments,
# or even hardcode them (not recommended)
from Telethon.telethon import TelegramClient
from Telethon.telethon.errors import SessionPasswordNeededError

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = '194812'
api_hash = '7702fea03a54be4b9f575540421ed1f3'
user_phone = '+841683531320'
session_name = 'WhiteShark'

def main():
    client = TelegramClient(session_name,
                            api_id,
                            api_hash,
                            proxy=None,
                            update_workers=4)

    print('INFO: Connecting to Telegram Servers...' )
    client.connect()
    print('Done!')

    if not client.is_user_authorized():
        print('INFO: Unauthorized user')
        client.send_code_request(user_phone)
        code_ok = False
        while not code_ok:
            code = input('Enter the auth code: ')
            try:
                code_ok = client.sign_in(user_phone, code)
            except SessionPasswordNeededError:
                password = getpass('Two step verification enabled. Please enter your password: ')
                code_ok = client.sign_in(password=password)
    print('INFO: Client initialized succesfully!')

    client.add_update_handler(update_handler)
    input('Press Enter to stop this!\n')

def update_handler(update):
    print(update)
    print('Press Enter to stop this!')

if __name__ == '__main__':
    main()

