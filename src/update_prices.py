from datetime import datetime
from datetime import timedelta
import time, numpy, os


from record_prices import *
from Price_Recorder import *
from pump import *
import config
import threading
import math

stop_threads = False
#Multithreading update prices
def update_price_thread(thread_position, main_client, coins):
	
	time.sleep(config.time_between_thread*thread_position) #Max of 16,6 req per sec
	last = time.time()
	# print "Starting updating price with threads"
	while stop_threads == False:
		if time.time() - last >= config.time_to_sleep:
			last += config.time_to_sleep
			try:
				update_prices(main_client.get_tickers(), coins)
			except Exception as e:
				print(e)
			# print time.time()
	# print "Threads of price update terminated"

def start_updating_prices(main_client, coins):
	num_of_threads = int(math.ceil(config.time_to_sleep / config.time_between_thread)) 
	# price_threads = []
	for thread_number in range(num_of_threads):
		t = threading.Thread(target=update_price_thread, args=(thread_number, main_client, coins))
		t.daemon = True #kill thread if main ends
		# price_threads.append(t)
		t.start()

def terminate_threads():
	global stop_threads 
	stop_threads = True

#Inicialization functions
def update_prices(tickers, coins):
	for ticker in tickers:
		if ticker['symbol'].endswith(config.market):
			symb = ticker['symbol'].replace(config.market, '') #Symbol without the ETH
			if symb in coins.keys():
				coins[symb]['price'] = unicode_to_float(ticker['last']) 

def track_all_coins(symbols_data, tickers, coins_to_track):
    for symbol_data in symbols_data:
        if symbol_data['quoteCurrency'] == config.market:
            symb = symbol_data['id'][:-3] 
            coins_to_track.append(str(symb))
    for ticker in tickers:
        if ticker['symbol'].endswith(config.market):
            if ticker['last'] == None:
                coins_to_track.remove(str(ticker['symbol'])[:-3])
                
def get_asset_balance(coin, client):
    all_balances = client.get_account_balance()
    for balance in all_balances:
        if  balance['currency'] == coin:
            return unicode_to_float(balance['available'])
