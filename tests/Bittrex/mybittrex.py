import sys
import json
import os
import logging
import base64

sys.path.append(os.path.abspath(os.path.join('../..')))
from pymongo import MongoClient
from modules.bittrex.bittrex import Bittrex, API_V2_0, API_V1_1, encrypt
from modules.mongodb.mongodb import Database

#logging.basicConfig(filename='mybittrex.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# global variable
DEBUG=True
FIRST_RUN=False
if DEBUG:
    passw='bbbbbbbbbbbbbbbb'

class BittrexV20PublicAPI(object):
    """
    Integration tests for the Bittrex public API.
    These will fail in the absence of an internet connection or if bittrex API goes down
    """

    def __init__(self):
        self.bittrex = Bittrex(None, None, api_version=API_V2_0)

    def get_markets(self):
        actual = self.bittrex.get_markets()
        return actual
        #logging.debug("Market Info: %s" % actual)

    def get_currencies(self):
        actual = self.bittrex.get_currencies()
        return actual

    def get_market_summaries(self):
        actual = self.bittrex.get_market_summaries()
        return actual

    def get_market_summary(self, market):
        actual = self.bittrex.get_marketsummary(market=market)
        return actual

    def get_orderbook(self, market):
        actual = self.bittrex.get_orderbook(market)
        return actual

    def get_market_history(self, market):
        actual = self.bittrex.get_market_history(market)
        return actual

    def list_markets_by_currency(self, currency):
        actual = self.bittrex.list_markets_by_currency(currency)
        return actual

    def get_wallet_health(self):
        actual = self.bittrex.get_wallet_health()
        return actual

    def get_balance_distribution(self):
        actual = self.bittrex.get_balance_distribution()
        return actual

    def get_candles(self, market, interval):
        actual = self.bittrex.get_candles(market, tick_interval=interval)
        return actual

    def get_latest_candle(self, market, interval):
        actual = self.bittrex.get_latest_candle(market, tick_interval=interval)
        return actual

class BittrexV11AccountAPI(object):
    def __init__(self):
        # connect db
        db = Database('telebit')
        # get secret key for API
        self.bt_api = db.find_one('bt_api_auth', None)
        db.close()
        # init Bittrex APi
        self.bittrex = Bittrex(base64.b64decode(self.bt_api['key']), base64.b64decode(self.bt_api['secret']), api_version=API_V1_1)
        self.bittrex.decrypt(passw)

    def get_openorders(self, market):
        actual = self.bittrex.get_open_orders(market)
        return actual

    def get_balances(self):
        actual = self.bittrex.get_balances()
        return actual

    def get_balance(self, currency):
        actual = self.bittrex.get_balance(currency)
        return actual

    def get_order_history_one_market(self, market):
        actual = self.bittrex.get_order_history(market=market)

class BittrexV20AccountAPI(object):
    def __init__(self):
        # connect db
        db = Database('telebit')
        # get secret key for API
        self.bt_api = db.find_one('bt_api_auth', None)
        db.close()
        # init Bittrex APi
        self.bittrex = Bittrex(base64.b64decode(self.bt_api['key']), base64.b64decode(self.bt_api['secret']), api_version=API_V2_0)
        self.bittrex.decrypt(passw)

    def get_openorders(self, market):
        actual = self.bittrex.get_open_orders(market)
        return actual

    def get_balances(self):
        actual = self.bittrex.get_balances()
        return actual

    def get_balance(self, currency):
        actual = self.bittrex.get_balance(currency)
        return actual

    def get_order_history_one_market(self, market):
        actual = self.bittrex.get_order_history(market=market)

if __name__ == '__main__':
    if FIRST_RUN:
        ### Encrypt API Key - execute for only 1 time ###
        # connect db
        db = Database('telebit')
        # get secret key for API
        bt_api = db.find_one('bt_api_auth', None)
        # Encrypt with an input password
        encrypted_key = encrypt(base64.b64decode(bt_api['key']), base64.b64decode(bt_api['secret']), None, None)
        logging.debug(encrypted_key)
        # Overwrite to the key
        saved_key = db.update('bt_api_auth', { "_id" : bt_api["_id"] }, { 'key': base64.b64encode(encrypted_key['key']), 'secret': base64.b64encode(encrypted_key['secret'])} )
        logging.debug(saved_key)
        db.close()

    ### Test Public API ###
    public_api = BittrexV20PublicAPI()
    #public_api.get_markets()
    del public_api

    ### Test Account API ###
    account_api = BittrexV20AccountAPI()
    logging.info(json.dumps(account_api.get_openorders("BTC-TRIG")))
    del account_api

