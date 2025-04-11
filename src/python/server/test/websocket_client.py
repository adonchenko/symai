#!/usr/bin/python3

"""A websockets client with SymAO UI protocol for python 3.
"""
import asyncio
import websockets
import signal
import sys
import argparse

def signal_handler(signal, frame):
    print(f"Signal INT caught")
    sys.exit(0)

# Function to handle the SymAI client
async def main():
    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument("-p", "--port", dest="port", default=12345, required=False, type=int,
                        help="Listening port for an SymAI Core Websockets Server")
    parser.add_argument("-i", "--ip", dest="ip", default="localhost", required=False, help="SymAI Core Websockets Server IP")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        async with websockets.connect('ws://' + args.ip + ':' + str(args.port)) as websocket:
            while True:
                # Prompt the user for a message
                message = input("Enter command: ")
                # Send the message to the server
                await websocket.send(message)
                # Receive a message from the server
                response = await websocket.recv()
                print(f"Received: {response}")
    except Exception as e:
        print(f"Something wrong. {str(e)} Quitting.")
        sys.exit(0)

# Run the client
if __name__ == "__main__":
    asyncio.run(main())