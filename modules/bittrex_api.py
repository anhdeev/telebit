#!/usr/bin/env python
import sys
import json
import os
import logging
import base64

#sys.path.append(os.path.abspath(os.path.join('../..')))
from pymongo import MongoClient
from packages.bittrex.bittrex.bittrex import *
from modules.mongodb.mongodb import Database

#logging.basicConfig(filename='mybittrex.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# global variable
DEBUG=True
FIRST_RUN=False
if DEBUG:
    passw='bbbbbbbbbbbbbbbb'
bittrex_v20_public_api=None
bittrex_v20_account_api=None
bittrex_v11_account_api=None


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
        self.bittrex = Bittrex(self.bt_api['key'], self.bt_api['secret'], api_version=API_V1_1)
        self.bittrex.decrypt(passw)

    def get_openorders(self, market=None):
        actual = self.bittrex.get_open_orders(market)
        return actual

    def get_balances(self):
        actual = self.bittrex.get_balances()
        return actual


    def get_balance_dist(self):
        actual = self.bittrex.get_balance_distribution()
        return actual

    def get_balance(self, currency):
        actual = self.bittrex.get_balance(currency)
        return actual

    def get_order_history_one_market(self, market):
        actual = self.bittrex.get_order_history(market=market)

    def get_order(self, uuid):
        actual = self.bittrex.get_order(uuid)
        return actual

class BittrexV20AccountAPI(object):
    def __init__(self):
        # connect db
        db = Database('telebit')
        # get secret key for API
        self.bt_api = db.find_one('bt_api_auth', None)
        db.close()
        # init Bittrex APi
        self.bittrex = Bittrex(self.bt_api['key'], self.bt_api['secret'], api_version=API_V2_0)
        self.bittrex.decrypt(passw)

    def get_openorders(self, market = None):
        actual = self.bittrex.get_open_orders(market)
        return actual

    def cancel_openorders(self, uuid):
        actual = self.bittrex.cancel(uuid)
        return actual

    def get_balances(self):
        actual = self.bittrex.get_balances()
        return actuali

    def get_currencies(self):
        actual = self.bittrex.get_currencies()
        return actual

    def get_balance(self, currency):
        actual = self.bittrex.get_balance(currency)
        return actual

    def get_wallet_health(self):
        actual = self.bittrex.get_wallet_health()
        return actual

    def get_balance_dist(self):
        actual = self.bittrex.get_balance_distribution()
        return actual

    def get_order_history_one_market(self, market):
        actual = self.bittrex.get_order_history(market=market)

    def buy_market(self, market, volume):
        actual = self.bittrex.trade_buy(market, order_type=ORDERTYPE_MARKET , quantity=volume, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED )
        return actual

    def buy_limit(self, market, volume, limit):
        actual = self.bittrex.trade_buy(market, order_type=ORDERTYPE_LIMIT , quantity=volume, rate=limit, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED )
        return actual

    def sell_market(self, market, volume):
        actual = self.bittrex.trade_sell(market, order_type=ORDERTYPE_MARKET, quantity=volume, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED)
        return actual

    def sell_limit(self, market, volume, limit):
        actual = self.bittrex.trade_sell(market, order_type=ORDERTYPE_LIMIT, quantity=volume, rate=limit, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED)
        return actual

    def sell_stop_loss(self, market, volume, limit, trigger):
        actual = self.bittrex.trade_sell(market, order_type=ORDERTYPE_LIMIT, quantity=volume, rate=limit, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED, \
                                            condition_type=CONDITIONTYPE_LESS_THAN, target=trigger)
        return actual

    def buy_stop(self, market, volume, limit, trigger):
        print(market, volume, limit, trigger)
        actual = self.bittrex.trade_buy(market, order_type=ORDERTYPE_LIMIT, quantity=volume, rate=limit, time_in_effect=TIMEINEFFECT_GOOD_TIL_CANCELLED, \
                                            condition_type=CONDITIONTYPE_GREATER_THAN , target=trigger)
        return actual


def load_api_key_for_the_first_run():
    # Encrypt API Key - execute for only 1 time ###
    # connect db
    db = Database('telebit')
    # get secret key for API
    try:
        with open("key.json") as f:
            bt_api = json.load(f)
            f.close()
    except:
        logging.error("key.json file not found!")
        raise

    # Encrypt with an input password
    encrypted_key = encrypt(bt_api['key'], bt_api['secret'], None, None)
    logging.debug(encrypted_key)
    # Overwrite to the key
    saved_key = db.insert_one( "bt_api_auth", { 'key': encrypted_key['key'], 'secret': encrypted_key['secret']} )
    logging.debug(saved_key)
    db.close()

