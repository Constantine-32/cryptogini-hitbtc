
from datetime import datetime
from datetime import timedelta

import config

class pump_info:
	def __init__(self, btc_available):
		self.coin = ''
		self.initial_price = 0
		self.price_bought = 0
		self.price_to_sell = 0

		self.btc_available = btc_available
		self.amount_to_buy = 0

		self.trade_info = {}
		self.pump_running = False
		self.coin_bought = False

	def calculate_order_parameters(self, coin, price_bought, initial_price, minQty, tickSize):
		self.coin = coin
		self.initial_price = initial_price
		self.price_bought = price_bought
		self.price_to_sell = self.sell_price_to_str(initial_price * config.pump_change_sell, tickSize)
		self.pump_running = True
		self.coin_bought = True
 
		self.amount_to_buy = self.truncate_to_minQty(self.btc_available / (self.price_bought / config.perc_to_pump),  minQty)
		
		config.t_betw_fetch = 0.5

	
	def sell_price_to_str(self, amount, tickSize):
		cut_value = self.truncate_to_minQty(amount, tickSize)
		return '{:.8f}'.format(cut_value)

	def truncate_to_minQty(self, amount, minQty):
		return int(amount / minQty) / (1 / minQty)

	def print_parameters(self):
		print ('Bought {} {} priced at {:.8f} with an initial price of {:.8f}. Sell limit at {}'.format(self.amount_to_buy, self.coin, self.price_bought, self.initial_price, self.price_to_sell))
	
	def reset_parameters(self):
		self.coin = ''
		self.initial_price = 0
		self.price_bought = 0
		self.price_to_sell = 0

		self.btc_available = 0
		self.amount_to_buy = 0

		self.trade_info.clear()
		self.pump_running = False
		self.coin_bought = False


def is_pump_near(next_pump, min_margin, sec_margin):
	
	year = next_pump['year']
	month = next_pump['month']
	day = next_pump['day']
	hour = next_pump['hour']
	minute = next_pump['min']
	second = next_pump['sec']

	date_pump = datetime(year, month, day, hour, minute, second)
	date_margin = timedelta(seconds = sec_margin + min_margin*60)
	if  date_pump - date_margin < datetime.now():
		return True
	return False