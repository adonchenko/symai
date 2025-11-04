import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable } from 'rxjs';

export class CtlSyncWS {
    private ws : WebSocket | null = null;
    private responseQueue: string[] = [];
    public isConnected : boolean = false;

  constructor() {}

  public init( some_ws : WebSocket) {
    this.ws = some_ws;
    this.postInit();
  }

  postInit() : void {
    this.ws!.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    this.ws!.onmessage = (event) => {
      try {
        this.responseQueue.push(event.data.toString());
        console.log('*** WebSocket onmessage: ' + event.data.toString() );
        //const str = this.responseQueue.shift();
        //resolve(str);
      } catch (error) {
        console.error('Error while receiving WebSocket message:', error);
      }
    };

    this.ws!.onclose = () => {
      console.log('WebSocket connection closed.');
      this.ws = null;
    };

    this.ws!.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

  }

  public async sendrecv(payload : string): Promise<string> {
    return new Promise((resolve, reject) => {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return reject(new Error('WebSocket is not open.'));
      }

      console.log(' *** WebSocket sendrecv: ' + payload);
      this.ws!.send( payload );

      // Optional: Add a timeout to reject the promise if no response is received
      setTimeout(() => {
        if (this.responseQueue.length === 0 ) {
          reject(new Error(`Timeout waiting for response to message:`));
        }
      }, 5000); // 5-second timeout

      const str = this.responseQueue.shift();
      if( typeof(str) === 'string') {
        console.log(' *** WS recv: ' + str);
        resolve(str);
      }
      //else 
      //  return reject(new Error('Error receiving data, response type = ' + typeof(str) ));
    });
  }

  public send(message : string) : boolean {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return false;
      }

      this.ws!.send( message );
      return true;
  }

  public async recv() : Promise<string> {
    return new Promise((resolve, reject) => {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return reject(new Error('WebSocket is not open.'));
      }

      const str = this.responseQueue.shift();
      if( typeof(str) === 'string') {
        console.log(' *** WS recv: ' + str);
        resolve(str);
      }
      else 
        return reject(new Error('Error receiving data, response type = ' + typeof(str)));
    });
  }

  public close(): void {
    if( this.ws !== null ) {
      this.ws.close();
      this.isConnected = false;
    }
  }

  public async connect(url : string) {
    console.log(" *** WebSocket connect: " + url);
    this.ws = new WebSocket(url);
    this.postInit();
    await new Promise(resolve => {
      this.ws!.onopen = () => {
        this.isConnected = true;
        console.log(" *** WebSocket connected");
        resolve(true);
      };
    });
  }

  public disconnect() : void {
    if( this.ws !== null )
      this.ws.close();
    this.ws = null;
    this.isConnected = false;
  }
}
