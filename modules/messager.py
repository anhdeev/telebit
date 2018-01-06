#!/usr/bin/env python
import os
import json
import logging
from modules.commander import Commander

MY_USER_NAME="Duong Anh"
MY_USER_ID="378106375"
MY_CHAT_ID="378106375"

class Messager(object):
    def __init__(self, update):
        self.update = update
        self.text = None
        self.from_user = None
        self.msg_type = None
        self.msg_id = None
        self.chat_id = None
        self.from_id = None

        logging.debug(json.loads(update.to_json()))

        if update.channel_post:
            channel_post = json.loads(update.channel_post.to_json())
            self.msg_type = "channel_post"
            if channel_post.get('text'):
                self.text = channel_post['text']
            if channel_post.get('from'):
                self.from_user = channel_post['from']
        elif update.message:
            message = json.loads(update.message.to_json())
            self.msg_type = "message"
            if message.get('text'):
                self.text = message['text']
            if message.get('from'):
                self.from_user = message['from']
            if message.get('message_id'):
                self.msg_id = message['message_id']
            if message.get('chat'):
                self.chat_id = message['chat'].get('id')
        else:
            logging.warn("The message is not in type of 'message' neither 'channel_post'")

    def execute_command(self):
        if self.from_user:
            if str(self.from_user['id']) != MY_USER_ID:
                logging.debug("Execute message type message")
                commander = Commander(self.text, False)
                result = commander.execute()
                return (self.chat_id, result)
            elif self.msg_type == "message" and self.text:
                logging.debug("Execute message type message")
                commander = Commander(self.text, True)
                result = commander.execute()
                return (self.chat_id, result)
            elif self.msg_type == "channel_post":
                logging.debug("Execute channel_post type message")
            else:
                logging.debug("Execute unknown type message")
        else:
            return (MY_CHAT_ID, "Anonymous user is not allowed!")

        return (None, None)

    
