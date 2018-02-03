exclude_coins = True
check_volumes = False
record_coins_txt = False

#Price threads

time_between_thread = 0.15
time_to_sleep = 1


#Tracked coins
coins_to_track = []
market = 'ETH'
excluded_coins = []
# excluded_coins = ['GAS', 'TRX', 'ETH', 'LTC', 'XRP', 'NEO', 'BNB', 'ADA', 'VEN', 'ICX', 'XVG', 'WTC', 'BCPT', 'IOTA', 'EOS', 'VIBE', 'IOST', 'XLM', 'TNT']


#Spikes
spikes_alarms = [-0.7,-0.1, 0.7, 0.05, 0.02, 0.005]

#Time events
t_betw_fetch = 0.5
t_betw_rec = 6
t_betw_res_alarm = 20
t_pump_duration = 40

#Pump
next_pump = {'year': 2018, 'month': 1, 'day': 30, 'hour' : 23, 'min' : 00, 'sec' : 00, 'group': "Mega_Pump", 'ended' : False}
make_order = False
perc_to_pump = 0.9
pump_time_margin = 5 #-Seconds before the next_pump to start the pump procedure

pump_percentage = 0.0055
pump_change_sell = 1.25
pump_change_abort = 0.1

#Sell = [[0.3, 1.15],[0.4, 1.19],[0.3, 1.23]]
