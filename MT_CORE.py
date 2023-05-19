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




# Extension of Dataframe class
class MT_DataFrame(pd.DataFrame):
    def __init__(self, name):
        self.name = name


# My implementation of a global logger for all pertinent information 
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

MT_Logger = MT_Logger('C:/Users/Philip/Desktop/MasterTrade/Logs')




class Exchange:
    global_logger = []

    trades = pd.DataFrame()

    async def async_init(self):
        await self.global_logger.log('222', 'class init')

    def __init__(self, name, global_logger_object):
        self.name = name
        self.global_logger = global_logger_object
        asyncio.run(self.async_init())

    def update_trades(self, new_trades):
        print("updating exchange's trades")
        self.trades = pd.concat([self.trades, new_trades])
        print("finished updating exchange's trades")


Binance = Exchange('Binance', MT_Logger)




async def main():
    await MT_Logger.log('111','Test')


asyncio.run(main())

