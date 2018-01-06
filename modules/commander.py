#!/usr/bin/env python
import os
import json
import logging
from packages.bittrex.bittrex.bittrex import * # import marcro definition
from modules.bittrex_api import *

MAX_BUY_AMOUNT=0.3
MIN_BUY_AMOUNT=0.0005
DEFAULT_AMOUNT=0.05
BTC_SATOSHI=1e8
CANDLE_INTERVAL_LIST={
    '1': TICKINTERVAL_ONEMIN,
    '5': TICKINTERVAL_FIVEMIN,
    '30': TICKINTERVAL_THIRTYMIN,
    '1h': TICKINTERVAL_HOUR,
    '1d': TICKINTERVAL_DAY
}
DEFAULT_CANDLE_STICK = TICKINTERVAL_FIVEMIN

class Commander(object):
    def __init__(self, cmd_txt, isMe):
        global bittrex_v20_account_api
        global bittrex_v20_public_api
        global bittrex_v11_account_api

        attributes = cmd_txt.split()
        self.cmd = attributes.pop(0)
        self.args = attributes
        self.market = None
        self.currency = None
        self.result = None
        self.isMe = isMe

        if not bittrex_v20_account_api:
            bittrex_v20_account_api = BittrexV20AccountAPI()
        if not bittrex_v20_public_api:
            bittrex_v20_public_api = BittrexV20PublicAPI()
        if not bittrex_v11_account_api:
            bittrex_v11_account_api = BittrexV11AccountAPI()

    def show_help(self):
        h = '''
/b or /buy <market> [amount] [limit]
/s or /sell <market> [amount] [limit]
/bs or /buys <market> [amount] [limit] [stop]
/sl or /stoploss <market> [percentage] [limit] [stop]
/i <market> [interval]
/orders [market]
/b or /ba [market]
/c or /cancel
/h or /help
#TODO: Update help content.
        '''
        return h

    #TODO
    def verify_market(self):
        if self.market.lower() == "btc":
            self.market = 'USDT-BTC'
        if "btc-" not in self.market.lower() and 'usdt-' not in self.market.lower() and 'eth-' not in self.market.lower():
            self.market = ('BTC-' + self.market).upper()
        return True

    def verify_float(self, number):
        try:
            if number[:1] == 's':
                number=float(number[1:])/BTC_SATOSHI

            number = round(float(number),8)
            if number < 0:
                return False
        except:
            return False

        return number

    def check_exceed_amount(self, amount):
        if (self.cmd in ['/b', '/buy']) and (self.market[:4] == "BTC-"):
            if not amount:
                total_amount = float(self.args[1]) * float(self.args[2])
            else:
                total_amount = float(amount)

            if total_amount > MAX_BUY_AMOUNT or total_amount < MIN_BUY_AMOUNT:
                self.result = "Total amount %.8f btc must be in range[%.8f:%.8f] BTC " % (total_amount, MIN_BUY_AMOUNT, MAX_BUY_AMOUNT)
                logging.warning(self.result)
                return True

        return False

    def get_current_price(self):
        global bittrex_v20_public_api

        latest_candle = bittrex_v20_public_api.get_latest_candle(self.market, TICKINTERVAL_FIVEMIN)
        if latest_candle['success']:
            current_price = latest_candle['result'][0].get('C')
        else:
            self.result = latest_candle['message']
            return False

        # 3. Refine price depend one buy or sell
        if '/b' in self.cmd:
            limit_price = float(current_price) * 1.01
        else:
            limit_price = float(current_price) * 0.99

        return limit_price

    def verify_command(self):
        if self.cmd in [ '/b', '/buy', '/s', '/sell' ]:
            args_len = len(self.args)
            # I. Verify number of arguments
            if (args_len < 1) or (args_len > 3):
                self.result = "Wrong command, need 1, 2 or 3 arguments"
                logging.warning("Wrong command, need 1, 2 or 3 arguments")
                return False

            self.market = self.args[0]

            # II. Verify Market
            if not self.verify_market():
                self.result = "Market argument is not recognized!"
                logging.warning("Market argument is not recognized!")
                return False
            # III. Refine Volume, Price and Ammount
            if args_len == 3: # in case of sufficent arguments
                # 1. Verify Volume, Price
                self.args[1] = self.verify_float(self.args[1])
                self.args[2] = self.verify_float(self.args[2])
                if (not self.args[1]) or (not self.args[2]):
                    self.result = "Volume & Price must be in float type"
                    logging.warn(self.result)
                    return False

                # 2. Check if exceed the maximum buy ammount (apply for BTC market only)
                if self.check_exceed_amount(self.args[1]):
                    return False

                # 3. convert amount of btc to volume of altcoin
                self.args[1] = round(self.args[1] / self.args[2], 8) # volume = ammount of btc / price

            elif args_len == 2: # in case of missing price -> based on current price (refine upper for buying, lower for selling)
                # 1. Verify Volume
                self.args[1] = self.verify_float(self.args[1])
                if not self.args[1]:
                    self.result = "Volume must be in float type"
                    logging.warn(self.result)
                    return False
                # 2. Get current price
                limit_price = self.get_current_price()
                if not limit_price:
                    return False
                self.args.append(round(limit_price,8))

                # 3. Check if exceed the maximum amount
                if self.check_exceed_amount(self.args[1]):
                    return False

                # 4. convert amount of btc to volume of altcoin
                self.args[1] = round(self.args[1] / self.args[2], 8) # volume = ammount of btc / price

            elif args_len == 1: # in case of missing both volume and price, get the current price and calulate volume based on the default ammount
                # 1. Get current price
                limit_price = self.get_current_price()
                if not limit_price:
                    return False
                # 3. Calculate the volume based on the default amount and the current price
                calculate_volume = float(DEFAULT_AMOUNT) / float(limit_price)
                self.args.append(round(calculate_volume,8))
                self.args.append(round(limit_price,8))

                # 3. Check if exceed the maximum amount
                if self.check_exceed_amount(DEFAULT_AMOUNT):
                    return False
        elif self.cmd in ['/sl', '/stoploss']:
            args_len = len(self.args)
            # I. Verify number of arguments
            if args_len != 4:
                self.result = "Wrong command, need 4 arguments"
                logging.warning("Wrong command, need 4 arguments")
                return False

            self.market = self.args[0]

            # II. Verify Market
            if not self.verify_market():
                self.result = "Market argument is not recognized!"
                logging.warning("Market argument is not recognized!")
                return False

            # III. Refine Percentage, Price, Trigger
            # 1. Verify Volume, Price
            self.args[1] = self.verify_float(self.args[1])
            self.args[2] = self.verify_float(self.args[2])
            self.args[3] = self.verify_float(self.args[3])

            if (not self.args[1]) or (not self.args[2] or (not self.args[3])):
                self.result = "Percentage & Price must be in float type"
                logging.warn(self.result)
                return False

            if self.args[1] <=0 or self.args[1] > 100:
                self.result = "Percentage of amount must be from 0+ to 100"
                logging.warn(self.result)
                return False

            # 2. Get balance of current currency then calculate desired volume to sell
            self.currency = self.market.split('-')[1]
            balance = bittrex_v20_account_api.get_balance(self.currency)
            if balance['success']:
                try:
                    self.args[1] = float(balance['result']['Balance']) * self.args[1] / 100
                except:
                    self.result = "Can not calculate volume for placing a stop loss order"
                    return False
            else:
                self.result = balance['message']
                return False

        elif self.cmd in ['/bs', '/buystop']:
            args_len = len(self.args)
            # I. Verify number of arguments
            if args_len != 4:
                self.result = "Wrong command, need 4 arguments"
                logging.warning("Wrong command, need 4 arguments")
                return False

            self.market = self.args[0]

            # II. Verify Market
            if not self.verify_market():
                self.result = "Market argument is not recognized!"
                logging.warning("Market argument is not recognized!")
                return False

            # III. Verify volum, price, trigger
            # 1. Verify Volume, Price
            self.args[1] = self.verify_float(self.args[1])
            self.args[2] = self.verify_float(self.args[2])
            self.args[3] = self.verify_float(self.args[3])

            if (not self.args[1]) or (not self.args[2]) or (not self.args[3]):
                self.result = "Volume & Price % Trigger must be in float type"
                logging.warn(self.result)
                return False

            # 2. Check if exceed the maximum buy ammount (apply for BTC market only)
            if self.check_exceed_amount(self.args[1]):
                return False

            # 3. convert amount of btc to volume of altcoin
            self.args[1] = round(self.args[1] / self.args[2], 8) # volume = ammount of btc / price


        elif self.cmd in ['/ba', '/balances']:
            args_len = len(self.args)
            # I. Verify number of arguments
            if args_len != 0 and args_len != 1:
                self.result = "Wrong command, need 0 or 1 arguments"
                logging.warning("Wrong command, need 0 or 1 arguments")
                return False

            if args_len == 1:
                self.currency = self.args[0]

        elif self.cmd in ['/i', '/info']: # /info <market> <interval>
            args_len = len(self.args)
            # I. Verify number of arguments
            if (args_len < 1) or (args_len > 2):
                self.result = "Wrong command, need 1 or 2 arguments"
                logging.warning("Wrong command, need 1 or 2 arguments")
                return False

            self.market = self.args[0]

            # II. Verify Market
            if not self.verify_market():
                self.result = "Market argument is not recognized!"
                logging.warning("Market argument is not recognized!")
                return False

            # 3. Verify candle interval
            if args_len == 1:
                self.args.append(DEFAULT_CANDLE_STICK)
            else:
                if self.args[1] not in CANDLE_INTERVAL_LIST:
                    self.result = "Wrong interval. Support: 1 5 15 30 1h 4h 1d."
                    logging.warning(self.result)
                    return False
                else:
                    self.args[1] = CANDLE_INTERVAL_LIST[self.args[1]]

        elif self.cmd in ['/o', '/orders']:
            args_len = len(self.args)
            # I. Verify number of arguments
            if args_len != 1 and args_len != 0:
                self.result = "Wrong command, need 0 or 1 arguments. Given %s." % args_len
                logging.warning("Wrong command, need 0 or 1  arguments")
                return False
            if args_len == 1:
                self.market = self.args[0]
                if not self.verify_market():
                    self.result = "Market argument is not recognized!"
                    logging.warning("Market argument is not recognized!")
                    return False
            else:
                self.market = None

        elif self.cmd in ['/c', '/cancel']:
            args_len = len(self.args)
            # I. Verify number of arguments
            if args_len != 0:
                self.result = "Wrong command, no need arguments. Given %s." % args_len
                logging.warning("Wrong command, no need arguments")
                return False
        elif self.cmd in ["/h", "/help"]:
            self.result = self.show_help()
            return False
        elif self.cmd == "/test":
            pass
        else:
            self.result = "Command %s is not recognized!" % self.cmd
            logging.warning("Command %s is not recognized!" % self.cmd)
            return False
        return True

    def execute(self):
        if not self.verify_command():
            return self.result

        # Get Info
        if self.cmd in ['/i', '/info']:
            candle_list = bittrex_v20_public_api.get_latest_candle(self.market, self.args[1])
            if candle_list['success']:
                self.result = "Latest Candle Stick %s - %s:\n" % (self.market, self.args[1])
                for key in candle_list['result'][0]:
                    self.result += '\t' + key + ' : ' + str(candle_list['result'][0][key]) + '\n'
            else:
                self.result = candle_list['message']
        # Get Orders
        elif self.cmd in ['/o', '/orders']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result
            open_orders = bittrex_v11_account_api.get_openorders(self.market)

            if open_orders['success']:
                self.result = "Open Orders (%d):\n" % len(open_orders['result'])
                i = 0
                for order in open_orders['result']:
                    i += 1
                    self.result += str(i) + '. ' + order['OrderType'] + ' ' + order ['Exchange'] + '\n'
                    self.result +='\tAmount: ' + str(order['Quantity']) + '\n' + '\tRemaining: '  + str(order['QuantityRemaining']) + '\n'
                    self.result +='\tLimit: ' + str(order['Limit'])  + '\n' + '\tActual Price: ' + str(order['Price']) + '\n'
                    self.result +='\tStatus: ' + "*Closed*" if order['Closed'] else "*Open* \n\n"
            else:
                self.result = open_orders['message']
        # Get Balances
        elif self.cmd in ['/ba', '/balances']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result
            if self.currency:
                balance = bittrex_v20_account_api.get_balance(self.currency)
                if balance['success']:
                    self.result = "%s Balance:\n" % balance['result']['Currency']
                    for key in balance['result']:
                        if key in ['Balance', 'Available', 'Pending']:
                            self.result += '\t' + key + ' : ' + str(balance['result'][key]) + '\n'
                else:
                    self.result = balance['message']
            else:
                if False: # Too long message
                    balances = bittrex_v20_account_api.get_balances()
                    if balances['success']:
                        self.result = "Balances:\n"
                        i = 0
                        for balance in balances['result']:
                            i += 1
                            self.result += '\t' + str(i) + '. ' + str(balance['Currency']) + '\n'
                            for key in balance:
                                if key not in ['CryptoAddress', 'Currency']:
                                    self.result += '\t\t' + key + ' : ' + str(balance[key]) + '\n'
                self.result='Can not get all balances due to too long message.'
        # Buy Limit
        elif self.cmd in ['/b', '/buy']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result

            open_buy = bittrex_v20_account_api.buy_limit(self.market, self.args[1], self.args[2])
            if open_buy['success']:
                self.result = "Placed a Buy Order: \n"
                for key in open_buy['result']:
                    if key not in ['OrderId', 'MarketCurrency']:
                        self.result += '\t' + key + ' : ' + str(open_buy['result'][key]) + '\n'
            else:
                self.result = open_buy['message']
        # Sell Limit
        elif self.cmd in ['/s', '/sell']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result

            open_sell = bittrex_v20_account_api.sell_limit(self.market, self.args[1], self.args[2])
            if open_sell['success']:
                self.result = "Placed a Sell Order: \n"
                for key in open_sell['result']:
                    if key not in ['OrderId', 'MarketCurrency']:
                        self.result += '\t' + key + ' : ' + str(open_sell['result'][key]) + '\n'
            else:
                self.result = open_sell['message']
        # Sell Stop Loss
        elif self.cmd in ['/sl', '/stoploss']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result

            open_sell = bittrex_v20_account_api.sell_stop_loss(self.market, self.args[1], self.args[2], self.args[3])
            if open_sell['success']:
                self.result = "Placed a Sell Order: \n"
                for key in open_sell['result']:
                    if key not in ['OrderId', 'MarketCurrency']:
                        self.result += '\t' + key + ' : ' + str(open_sell['result'][key]) + '\n'
            else:
                self.result = open_sell['message']

        # Buy Stop
        elif self.cmd in ['/bs', '/buystop']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result

            open_sell = bittrex_v20_account_api.buy_stop(self.market, self.args[1], self.args[2], self.args[3])
            if open_sell['success']:
                self.result = "Placed a Buy Order: \n"
                for key in open_sell['result']:
                    if key not in ['OrderId', 'MarketCurrency']:
                        self.result += '\t' + key + ' : ' + str(open_sell['result'][key]) + '\n'
            else:
                self.result = open_sell['message']

        # Cancel all orders
        elif self.cmd in ['/c', '/cancel']:
            if not self.isMe:
                self.result == "WARNING!! You have no access right to anhdv bittrex account!"
                return self.result

            open_orders = bittrex_v11_account_api.get_openorders()
            if open_orders['success']:
                self.result = "Cancelling %d orders:\n" % len(open_orders['result'])
                for order in open_orders['result']:
                    cancel_order = bittrex_v20_account_api.cancel_openorders(order['OrderUuid'])
                    if cancel_order['success']:
                        self.result += '\t %s' % order['Exchange'] + '\t[y]\n'
                    else:
                        self.result += '\t %s' % order['Exchange'] + '\t[n]\n'
        elif self.cmd == "/test":
            #open_buy = bittrex_v20_account_api.buy_market( "BTC-RDD", 3450)
            #self.result = str(open_buy)
            pass
        else:
            self.result = "*TODO:* Execute %s %s %s" % (self.cmd, self.market, self.args)

        return self.result

