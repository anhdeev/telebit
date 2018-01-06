import os
from modules.bittrex_api import *


SIGNAL_WEIGHT={
    "HUGE": 0.3,
    "BIG": 0.2,
    "SMALL": 0.1,
    "TINY": 0.05,
    "TEST": 0.002
}


MY_USER_NAME="Duong Anh"
MY_USER_ID="378106375"
MY_CHAT_ID="378106375"

ALLOWED_HIGH=0.2 #5min
SIGNAL_LOCKED=False
SIGNAL_LIST=[]

class FlashPump(object):
    def __init__(self, bot, signal, weight):
        global bittrex_v20_public_api
        global bittrex_v20_account_api
        self.currency = signal
        self.weight = weight
        self.result = None
        self.market = "btc-" + signal
        self.bot = bot

        if not bittrex_v20_public_api:
            bittrex_v20_public_api = BittrexV20PublicAPI()
        if not bittrex_v20_account_api:
            bittrex_v20_account_api = BittrexV20AccountAPI()

    def get_current_price(self):
        global bittrex_v20_public_api

        latest_candle = bittrex_v20_public_api.get_latest_candle(self.market, TICKINTERVAL_FIVEMIN)
        if latest_candle['success']:
            current_price = latest_candle['result'][0].get('C')
            high = latest_candle['result'][0].get('H')
            low = latest_candle['result'][0].get('L')

            if ((float(high)/float(low)) - 1 > float(ALLOWED_HIGH)):
                self.result = "Too late to jump into the pump. It was over %s " % str(ALLOWED_HIGH)
                logging.warn(self.result)
                return False

            return (current_price * 1.05) # Adding 5% for limit price
        else:
            self.result = latest_candle['message']
            return False

    def jump_in(self):
        global SIGNAL_LOCKED
        global bittrex_v20_public_api
        global bittrex_v20_account_api

        if SIGNAL_LOCKED:
            return
        else:
            SIGNAL_LOCKED = True

        limit_price = self.get_current_price()

        if not limit_price:
            return False
        elif self.market not in SIGNAL_LIST:
            # Calculate the volume based on the default amount and the current price
            volume = round(float(SIGNAL_WEIGHT[self.weight]) / float(limit_price),2)

            open_buy = bittrex_v20_account_api.buy_limit(self.market, volume, limit_price)
            #open_buy = bittrex_v20_account_api.buy_market(self.market, volume)
            logging.info(open_buy)
            if open_buy['success']:
                result = "Placed a Buy Order: \n"
                for key in open_buy['result']:
                    if key not in ['OrderId', 'MarketCurrency']:
                        result += '\t' + key + ' : ' + str(open_buy['result'][key]) + '\n'

                SIGNAL_LIST.append(self.market)

                self.bot.send_message(MY_CHAT_ID, str(result))
            else:
                self.bot.send_message(MY_CHAT_ID, str(open_buy))

            if False:
                # Calculate sell price
                self.bot.sendMessage(chat_id=MY_CHAT_ID, text="Placed a buy order %s %s %s \nWait till it is fullied..\n" % (self.market, volume, limit_price))
                limit_sell_price = limit_price * 1.05

                timeout=0
                while(True):
                    order = bittrex_v20_account_api.get_order(open_buy['OrderId'])
                    if order['success']:
                        if not order['result']['IsOpen']:
                            break
                        self.bot.sendMessage(chat_id=MY_CHAT_ID, text=".")
                        sleep(3)
                        timeout += 1
                        if timeout == 10:
                            break
                    else:
                        continue

                if timeout == 10:
                    # Cancel remaining order
                    commander = Commander("/c %s" % self.market, True)
                    result = commander.execute()
                    self.bot.sendMessage(chat_id=MY_CHAT_ID, text="Timed out! Cannel remaining ammount.. and jump out")
                    self.bot.sendMessage(chat_id=MY_CHAT_ID, text=str(result))
                else:
                    self.bot.sendMessage(chat_id=MY_CHAT_ID, text="Fullied! Jump out..")

                # Get balance of the currency
                #commander = Commander("/ba %s" % self.market, True)
                # Sell half of balance at 5% profit
                # Place a stop loss at current price-2%
                # Notify to user

                #self.result = "Placed a Buy Order: \n"
                #for key in open_buy['result']:
                #    if key not in ['OrderId', 'MarketCurrency']:
                #        self.result += '\t' + key + ' : ' + str(open_buy['result'][key]) + '\n'
            else:
                pass
                #self.bot.sendMessage(chat_id=MY_CHAT_ID, text=open_buy['message'])

            SIGNAL_LOCKED=False


    def jump_out():
        pass

    def set_stop_loss():
        pass
