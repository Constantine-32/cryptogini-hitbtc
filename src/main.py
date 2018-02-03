import uuid
import time
from datetime import datetime
from datetime import timedelta

import requests
from decimal import *

from HitBtc import Client
import config
import api
from pump import *
from record_prices import *
from update_prices import *
from Price_Recorder import *

def get_clients():
    clients = []
    for client_info in api.clients:
        if not client_info['active']:
            continue
        try:
            client = {}
            client['user'] = client_info['user']
            client['client'] = Client("https://api.hitbtc.com", client_info['api_key'], client_info['api_secret'])
            client['pump'] = pump_info(get_asset_balance(config.market, client['client']))
            # client['pump'] = pump_info(0.1)
            clients.append(client)
            print('Client : {}, Balance : {:.8f}'.format(client_info['user'], client['pump'].btc_available))
        except:
            print('Client : {}, Detected an error and can not use API'.format(client_info['user']))
    return clients

def buy_pumped_coin(symb, pump_data, client, user):
    amount_to_buy = pump_data.amount_to_buy
    sell_limit = pump_data.price_to_sell
    
    try:
        client.market_buy(symbol=symb, quantity=amount_to_buy)
    except Exception as e:
        print ('Problem encountered buying {} with the {} account. Error is {}'.format(symb, user, e))

    try:
        client.order_limit_sell(symbol=symb, quantity=amount_to_buy, price=sell_limit)
    except Exception as e:
        print ('Problem encountered placing sell limit with the {} account. Error is {}'.format(user, e))

def check_spikes(coins, clients, pump_running):
    
    for key, coin in coins.items():
        
        spike = (coin['price'] - coin['mean'])/coin['mean']

        if pump_running == True and clients[0]['pump'].coin_bought == False:
            if spike >= config.pump_percentage and spike < config.pump_change_abort:
                for client in clients:
                    client['pump'].calculate_order_parameters(str(key), coin['price'], coin['mean'], coin['minQty'], coin['tickSize'])
                    if config.make_order:
                        buy_pumped_coin(str(key), client['pump'], client['client'], client['user'])
                    client['pump'].print_parameters()                      

        for spike_alarm in config.spikes_alarms:

            if str(spike_alarm) not in coin['previous_spikes'].keys():
                if spike_alarm < 0:
                    if spike < spike_alarm:
                        print(key, " Has fallen a", ("{:.3f}%!").format(spike*-100))
                        coin['previous_spikes'][str(spike_alarm)] = datetime.now()
                if spike_alarm > 0:
                    if spike > spike_alarm:
                        print(key, " Has increased a", ("{:.3f}%!").format(spike*100))
                        coin['previous_spikes'][str(spike_alarm)] = datetime.now()

if __name__ == "__main__":

    clients = get_clients()
    
    if len(clients) == 0:
        print "any client introduced"

    main_client = clients[0]['client']

           
    coins_to_track = []
    track_all_coins(main_client.get_symbols(), main_client.get_tickers(), coins_to_track)

    # price_recorder = Price_Recorder(config.t_betw_rec, 10)
    price_recorder = Price_Recorder(10)

    price_recorder.initialize_coins(main_client.get_tickers(), coins_to_track, main_client.get_symbols())

    #Time variables
    t_fetch = time.time()
    t_dips = time.time()
    t_reset_alarms = time.time()
    t_pump_start = time.time()

    #--LIST OF RETAINED PRICES DURING PUMP--#
    retained_prices = init_retained_prices(coins_to_track)

    #--RESET SPIKE ALARM--#
    t_betw_res_alarm_delta =timedelta(seconds = config.t_betw_res_alarm)

    #--PUMP INFO--#
    pump_running = False

    #Price updates
    pricing_with_threads = False

    while True:
        if time.time() - t_fetch > config.t_betw_fetch:
            t_fetch = time.time()

            if pricing_with_threads == False:
                update_prices(main_client.get_tickers(), price_recorder.coins)

            #---RECORD COINS---#
            if config.record_coins_txt:
                if pump_running == True: 
                    for symb, coin in price_recorder.coins.items():
                        retain_coin_price(coin['price'], retained_prices[symb], symb)
                else: 
                    for symb, coin in price_recorder.coins.items():
                        record_coin_price(coin['price'], symb)
            
            #---START PUMP MODE---#
            if config.next_pump['ended'] == False and pump_running == False:
                if is_pump_near(config.next_pump, 0, config.pump_time_margin + 2) and pricing_with_threads == False:
                    start_updating_prices(main_client, price_recorder.coins)
                    pricing_with_threads = True
                elif is_pump_near(config.next_pump, 0, config.pump_time_margin): # 5 seconds before
                    pump_running = True
                    config.t_betw_fetch = 0.15
                    t_pump_start = time.time()
                    print ("...Starting Pump Prodecure...")

            #---CHECK FOR FAST % CHANGES---#
            check_spikes(price_recorder.coins, clients, pump_running)

        #---UPDATE RECORDS---#
        if time.time() - t_dips > config.t_betw_rec:
            t_dips = time.time()
            price_recorder.update_previous_prices()

        #---PUMP MODE ENDED---#
        if time.time() - t_pump_start > config.t_pump_duration and pump_running:
            pump_running = False
            pricing_with_threads = False
            config.next_pump['ended'] = True
            config.t_betw_fetch = 0.5
            terminate_threads()
            for client in clients:
                client['pump'].reset_parameters()
            print ("Dumping data, Pump finalized!")

            if config.record_coins_txt:
                for key, coin_retained_prices in retained_prices.items():
                    dump_retained_prices(coin_retained_prices, key)

        #---RESET SPIKE ALARMS---# polla en vinagre que funciona i no sa de tocar
        if time.time() - t_reset_alarms > config.t_betw_res_alarm and pump_running == False:
            t_reset_alarms = time.time()
            for symb, coin in price_recorder.coins.items():
                for spike_alarm in config.spikes_alarms:
                    if str(spike_alarm) in coin['previous_spikes'].keys():
                        if datetime.now() - coin['previous_spikes'][str(spike_alarm)] > t_betw_res_alarm_delta:
                            # print "Deleted spike alarm for a ", spike_alarm, '%, Coin: ', str(symb)
                            coin['previous_spikes'].pop(str(spike_alarm), None)

    # for key, coin in price_recorder.coins.items():
    #     print key, '->', '{:.8f}'.format(coin['tickSize'])
    # a = client.get_tickers()
    # for b in a:
    #     if b['last'] != None and '.' not in b['last']:
    #         print b

    # print coins_to_track
    # time1 = time.time()
    # for i in range(20):
    #     a = client.get_tickers()

    # print (time.time() - time1)/20