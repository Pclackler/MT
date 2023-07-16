import requests
import json
import base64
import hmac
import hashlib
import websockets
import asyncio
import asyncio
import json
import websockets
import ssl
import gzip
from upbit.websocket import UpbitWebSocket
import time
import datetime
import pandas as pd
import csv
import re
import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import datetime
import time
import tkinter as tk
import threading
import discord
import queue
import threading
import concurrent.futures
import urllib.parse
import hashlib
import hmac
import base64
import requests
import time
import pprint
import aiohttp
import asyncio
import datetime
import hmac
import hashlib
import time
import urllib.parse
import inspect

 # The path to use for log files
MT_Logger_log_path = 'C:/Users/Philip/Desktop/MasterTrade/Logs'


MT_active_base_assets = ['BTC']
MT_active_quote_assets = ['USD','USDT']
MT_tradeable_quote_assets = ['USD','USDT']


class MT_DataFrame(pd.DataFrame): # Extension of Dataframe class
    def __init__(self, name):
        self.name = name


# ________________________________
# GLOBAL LOGGER OBJECT 
# ________________________________

# Usage:
# Define the global logger class instance as MT_Logger.
# It will be accessed and referred to as MT_Logger from within just about every class method.
# Since it will be used extensively, it is efficient to have it in the global namespace.
# There's no need for additional security or complexity for this implementation.

class MT_Logger: 
    def __init__(self, log_dir):
        self.log_dir = log_dir

    async def log(self, code, message):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_directory = f"{self.log_dir}/{current_date}"
        log_file = f"{log_directory}/{current_date}.csv"
        
        try:
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            
            log_entry = {
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'code': code,
                'message': message
            }
            
            with open(log_file, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=log_entry.keys())
                if file.tell() == 0:  # Check if file is empty
                    writer.writeheader()
                writer.writerow(log_entry)
        
        except OSError as e:
            print(f"Error while logging: {e}")
        
        await asyncio.sleep(0)  # Allow other tasks to run


MT_Logger = MT_Logger(MT_Logger_log_path) # Explicit MT_Logger definition.
# ________________________________
# /GLOBAL LOGGER OBJECT 
# ________________________________




# ________________________________
# GLOBAL BASE EXCHANGE OBJECT
# ________________________________
class Exchange:
    
    trades = pd.DataFrame()

    def __init__(self, name):
        self.name = name

    async def update_trades(self, new_trades):
        
        self.trades = pd.concat([self.trades, new_trades])
        await asyncio.sleep(0)  # Allow other tasks to run
# ________________________________
# / GLOBAL BASE EXCHANGE OBJECT
# ________________________________






# ________________________________
# BINANCE DEFINITION -100
# ________________________________

class Binance(Exchange):

    # This object Id will be referenced every time we use the logger.
    # This is for easy sorting later
    object_id = '100' 

    # Maybe in each Exchange Class instance init, this is where we get our authentication tokens etc? 
    async def async_binance_init(self):
        await MT_Logger.log(f'{self.object_id}', f'{self.name} class init')
        await asyncio.sleep(0)  # Allow other tasks to run

    def __init__(self, name):
        self.name = name
        asyncio.run(self.async_binance_init())

Binance = Binance('Binance')

# ________________________________
# / BINANCE DEFINITION -100
# ________________________________


# ________________________________
# BINANCE US DEFINITION -101
# ________________________________

class BinanceUS(Exchange):

    active_streams = {'trades' : False, 'orderbook_updates' : False}

    API_KEY = ''

    API_SECRET_KEY = ''

    # This object Id will be referenced every time we use the logger.
    # This is for easy sorting later
    object_id = '101' 

    base_endpoint_rest = "https://api.binance.us"

    account_info = {}


    async def get_binanceus_signature(self, data):
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(self.API_SECRET_KEY, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac

    async def binanceus_request(self, uri_path, data,  type):
        headers = {}
        headers['X-MBX-APIKEY'] = self.API_KEY
        signature = await self.get_binanceus_signature(data)
        params = {
            **data,
            "signature": signature,
        }

        if type == 'GET':
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_endpoint_rest + uri_path, params=params, headers=headers) as response:
                    return await response.text()
        if type == 'POST':
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_endpoint_rest + uri_path, params=params, headers=headers) as response:
                    return await response.text()


    # This Method is where we retrieve account information / balances etc. Update this as needed
    async def get_account_info(self):

        uri_path = "/api/v3/account"

        data = {
            "timestamp": int(round(time.time() * 1000)),
        }

        get_account_result = await self.binanceus_request(uri_path, data, 'GET')
        
        self.account_info = get_account_result
        await asyncio.sleep(0)
        
        return get_account_result
        
    async def send_order(self,symbol,type,side,price,quantity,timeInForce):
        
        try:
            uri_path = "/api/v3/order"
            # Get the parameters of the method
            parameters = inspect.signature(self.send_order).parameters
            data = {}
            # Iterate over the parameter names
            for param_name in parameters:
                # Get the value of the parameter
                param_value = locals()[param_name]
                # Do something with the parameter name
                    # Check if the value is not null and not empty
                if param_value is not None and param_value != "":
                    # Append the parameter value to the data dictionary
                    data[param_name] = param_value
        

            data["timestamp"] = int(round(time.time() * 1000))
                
            await MT_Logger.log(f'{self.object_id}', f'{self.name} SENDING ORDER')
            result = await self.binanceus_request(uri_path=uri_path, data=data, type='POST')
            print("POST {}: {}".format(uri_path, result))
            await MT_Logger.log(f'{self.object_id}', f'{self.name} ORDER SENT')
            await MT_Logger.log(f'{self.object_id}', f'{self.name} ORDER RESULT : {result}')
        except Exception as e:
            print(e)
            await MT_Logger.log(f'{self.object_id}', f'{self.name} ERROR SENDING ORDER :')
            await MT_Logger.log(f'{self.object_id}', f'{self.name} EXCEPTION : {e}')
            await MT_Logger.log(f'{self.object_id}', f'{self.name} FAILED DATA PAYLOAD {data}')

        
    async def async_binanceus_init(self):
        await MT_Logger.log(f'{self.object_id}', f'{self.name} class init')
        await self.get_account_info()

    async def initialize(self):
        await self.async_binanceus_init()

    def __init__(self, name):
        self.name = name
        asyncio.run(self.initialize())

BinanceUS = BinanceUS('BinanceUS')

# ________________________________
# / BINANCE US DEFINITION -101
# ________________________________
endpoints_global = ['BTC-USDT']

# ________________________________
# COINBASE DEFINITION -102
# ________________________________

class Coinbase(Exchange):

    
    active_websocket_trade_streams = []
    object_id = '102' 

    async def async_coinbase_init(self):
        await MT_Logger.log(f'{self.object_id}', f'{self.name} class init')
        

    async def initialize(self):
        await self.async_coinbase_init()

    def __init__(self, name):
        self.name = name
        asyncio.run(self.initialize())

    async def connect_to_coinbase(self):
        global MT_active_base_assets
        global MT_active_quote_assets
        start_time = time.time()
        while True:
            try:
                async with websockets.connect('wss://ws-feed.exchange.coinbase.com', ssl=ssl.SSLContext()) as websocket:
                    temp_new_symbol_list = []
                    #Iterate and give a list of endpoints to connect to 'BTC-USDT' 'ETH-USDT'
                    for base_symbol in MT_active_base_assets:
                        for quote_symbol in MT_active_quote_assets:
                            symbol = base_symbol + '-' + quote_symbol
                            temp_new_symbol_list.append(symbol)

                    await MT_Logger.log('1','new list of appended base+quote Symbols :')   
                    await MT_Logger.log('1',str([temp_new_symbol_list]))
                    await MT_Logger.log('1','existing list of appended base+quote Symbols :')     
                    await MT_Logger.log('1',str([self.active_websocket_trade_streams])) 
                    
                    if self.active_websocket_trade_streams != []:
                        #Ok, connections are not empty, proceed.
                        entries =[]
                        for index,entry in enumerate(self.active_websocket_trade_streams):
                            if (entry not in temp_new_symbol_list):
                                    entries.append(entry)
                                    print('!!!!!!Entry Not found in new list')
                                    
                                    if index+1 == len(self.active_websocket_trade_streams): #we've reached the end of the symbol list, nopw we can unsub
                                        print("unsubbing from entries"+str(entries))
                                        unsubscribe_msg = {
                                            "type": "unsubscribe",
                                            "channels": [{"name": "matches", "product_ids": [entries]}]
                                        }
                                        
                                        await MT_Logger.log('1',f'sending unsubscribe message: {unsubscribe_msg}')
                                        await websocket.send(json.dumps(unsubscribe_msg))

                                        for entry in entries:
                                            self.active_websocket_trade_streams.remove(entry)      
                                    
                    
                                
                    
                    for symbol in temp_new_symbol_list:
                        if symbol not in self.active_websocket_trade_streams:
                                                

                            subscribe_msg = {
                                "type": "subscribe",
                                "channels": [{"name": "matches", "product_ids": [symbol]}]
                            }
                            
                            
                            await MT_Logger.log('1',f'sending ADDITIONAL subscribe message: {subscribe_msg}')
                            
                            await websocket.send(json.dumps(subscribe_msg))
                            self.active_websocket_trade_streams.append(symbol)
                            

                     
                                
                    async for message33 in websocket:
                        message = json.loads(message33)
                        # Is this a trade message?
                        print(message)
                        temp_new_symbol_list = []
                        
                        #Iterate and give a list of endpoints to connect to 'BTC-USDT' 'ETH-USDT'
                        for base_symbol in MT_active_base_assets:
                            for quote_symbol in MT_active_quote_assets:
                                symbol = base_symbol + '-' + quote_symbol
                                temp_new_symbol_list.append(symbol)
                                

                        await MT_Logger.log('1',str(temp_new_symbol_list))
                        await MT_Logger.log('2',str(self.active_websocket_trade_streams))

                        should_break = False

                        for entry in self.active_websocket_trade_streams:
                            print(entry)
                            if self.active_websocket_trade_streams != temp_new_symbol_list:
                                await MT_Logger.log('1','OH GOD IM GUNNA BREAK')
                                should_break = True
                                break

                        if should_break:
                            break

                                                
                        

                    #Erase any empty entries       
                    self.active_websocket_trade_streams = [item for item in self.active_websocket_trade_streams if item != '']

                    await MT_Logger.log('1','END iteration of message33')
                        
            except Exception as e:
                print(e)
                await asyncio.sleep(3)

Coinbase = Coinbase('Coinbase')
# ________________________________
# / COINBASE DEFINITION -102
# ________________________________


async def change_symbols():
    global MT_active_base_assets
    start_time = time.time()
    while True:
        
        
        if time.time() - start_time > 10:
            await MT_Logger.log('21','10 SECOND MARK')
            MT_active_base_assets = ['BTC','ETH']

        if time.time() - start_time > 20:
            await MT_Logger.log('21','20 SECOND MARK')
            MT_active_base_assets = ['XRP']

        if time.time() - start_time > 40:
            await MT_Logger.log('21','40 SECOND MARK')
            MT_active_base_assets = ['XRP','ETH','BTC','AVX'] 

        await asyncio.sleep(1)


async def main():
             


    await MT_Logger.log('99','Master Trader main INITIALIZING')

    print("Initialized, waiting 2 seconds before asking for account information")

    await BinanceUS.get_account_info()

    print("Waiting for account information")

    await asyncio.sleep(2)

    print(BinanceUS.account_info)

    print("waiting to send test trade request")
    await asyncio.sleep(2)

    await BinanceUS.send_order(symbol='BTCUSDT',side='BUY',type='LIMIT',quantity=.01,price=26800.5,timeInForce='GTC')
    while True:
        
        try:
            tasks = [Coinbase.connect_to_coinbase(),
                     change_symbols()]
            # Gather and execute all the tasks
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            print(f"Error: {e}")
            # wait and reconnect for the failed task
            await asyncio.sleep(1)
   

asyncio.run(main())

