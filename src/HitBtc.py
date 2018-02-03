import uuid
import time

import requests
from decimal import *

class Client(object):
    
    def __init__(self, url, public_key, secret):
        self.url = url + "/api/2"
        self.session = requests.session()
        self.session.auth = (public_key, secret)

    def get_symbol(self, symbol_code):
        """Get symbol."""
        return self.session.get("%s/public/symbol/%s" % (self.url, symbol_code)).json()

    def get_symbols(self):
        """Get all symbols."""
        return self.session.get("%s/public/symbol" % (self.url)).json()
    
    def get_ticker(self, symbol):
        """Get tickers of a specific symbol."""
        return self.session.get("%s/public/ticker/%s" % (self.url, symbol)).json()

    def get_tickers(self):
        """Get tickers of all symbols."""
        return self.session.get("%s/public/ticker" % (self.url)).json()

    def get_orderbook(self, symbol_code):
        """Get orderbook. """
        return self.session.get("%s/public/orderbook/%s" % (self.url, symbol_code)).json()

    def get_address(self, currency_code):
        """Get address for deposit."""
        return self.session.get("%s/account/crypto/address/%s" % (self.url, currency_code)).json()

    def get_account_balance(self):
        """Get main balance."""
        return self.session.get("%s/account/balance" % self.url).json()

    def get_trading_balance(self):
        """Get trading balance."""
        return self.session.get("%s/trading/balance" % self.url).json()

    def transfer(self, currency_code, amount, to_exchange):
        return self.session.post("%s/account/transfer" % self.url, data={
                'currency': currency_code, 'amount': amount,
                'type': 'bankToExchange' if to_exchange else 'exchangeToBank'
            }).json()

    def market_buy(self, symbol, quantity):
        """Buy from market(instant)"""
        data = {'symbol': symbol, 'type' : 'market', 'timeInForce': 'IOC', 'side': 'buy', 'quantity': quantity}
        return self.session.post("%s/order" % (self.url), data=data).json()

    def market_sell(self, symbol, quantity):
        """Sell from market(instant)"""
        data = {'symbol': symbol, 'type' : 'market', 'timeInForce': 'IOC', 'side': 'sell', 'quantity': quantity}
        return self.session.post("%s/order" % (self.url), data=data).json()
    
    def order_limit_sell(self, symbol, quantity, price):
        """Order a sell limit"""
        data = {'symbol': symbol, 'timeInForce': 'IOC', 'side': 'sell', 'quantity': quantity, 'price' : price}
        return self.session.post("%s/order" % (self.url), data=data).json()

    # def new_order(self, symbol_code, order_type, side, quantity, price=None):
    #     """Place a market order."""
    #     data = {'symbol': symbol_code, 'type' : order_type, 'timeInForce': 'IOC', 'side': side, 'quantity': quantity}

    #     if price is not None:
    #         data['price'] = price

    #     return self.session.post("%s/order/%s" % (self.url, transaction_id), data=data).json()

            

    # Time in force is a special instruction used when placing a trade to indicate how long an order will remain active before it is executed or expires 
    # GTC - Good till cancel. GTC order won't close until it is filled. 
    # IOC - An immediate or cancel order is an order to buy or sell that must be executed immediately, and any portion of the order that cannot be immediately filled is cancelled. 
    # FOK - Fill or kill is a type of time-in-force designation used in securities trading that instructs a brokerage to execute a transaction immediately and completely or not at all. 
    # Day - keeps the order active until the end of the trading day in UTC. 
    # GTD - Good till date specified in expireTime.

    def get_order(self, client_order_id, wait=None):
        """Get order info."""
        data = {'wait': wait} if wait is not None else {}

        return self.session.get("%s/order/%s" % (self.url, client_order_id), params=data).json()

    def cancel_order(self, client_order_id):
        """Cancel order."""
        return self.session.delete("%s/order/%s" % (self.url, client_order_id)).json()

    def withdraw(self, currency_code, amount, address, network_fee=None):
        """Withdraw."""
        data = {'currency': currency_code, 'amount': amount, 'address': address}

        if network_fee is not None:
            data['networkfee'] = network_fee

        return self.session.post("%s/account/crypto/withdraw" % self.url, data=data).json()

    def get_transaction(self, transaction_id):
        """Get transaction info."""
        return self.session.get("%s/account/transactions/%s" % (self.url, transaction_id)).json()