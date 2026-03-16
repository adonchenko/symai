#!/usr/bin/python3

"""A websockets client with SymAO UI protocol for python 3.
"""
import websockets
from websockets.sync.client import connect
import _thread

import sys
import signal
import argparse

def signal_handler(signal, frame):
    print(f"Signal INT caught")
    sys.exit(0)

def receive_messages(websocket):
    while True:        
        try:
            message = websocket.recv()
            print(">", message)
        except websockets.exceptions.ConnectionClosed:
            break

parser = argparse.ArgumentParser(description="HTTP Server")
parser.add_argument("-p", "--port", dest="port", default=12345, required=False, type=int,
                    help="Listening port for an SymAI Core Websockets Server")
parser.add_argument("-i", "--ip", dest="ip", default="localhost", required=False, help="SymAI Core Websockets Server IP")
args = parser.parse_args()

signal.signal(signal.SIGINT, signal_handler)

with connect('ws://' + args.ip + ':' + str(args.port)) as ws:
    _thread.start_new_thread(receive_messages,(ws,))
    while True:
        toSend = input()
        try:
            ws.send(toSend)
        except:
            break    

