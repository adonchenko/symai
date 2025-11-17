import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable } from 'rxjs';

export class CtlSyncWS {
    private ws : WebSocket | null = null;
    private responseQueue: Array<(msg: MessageEvent) => void> = []; //string[] = [];
    public isConnected : boolean = false;

  constructor() {}

  public attach(other_ws : WebSocket) : void {
    this.ws = other_ws;
  }
  
  public init( some_ws : WebSocket) {
    this.ws = some_ws;
    this.postInit();
  }

  postInit() : void {
    this.ws!.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    this.ws!.onmessage = (event) => {
      //try {
      //  this.responseQueue.push(event.data.toString());
      //  console.log('*** WebSocket onmessage: ' + event.data.toString() );
      //} catch (error) {
      //  console.error('Error while receiving WebSocket message:', error);
      //}
      const resolve = this.responseQueue.shift();
      if (resolve) {
        resolve(event);
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

  waitForMessage(): Promise<MessageEvent> {
    return new Promise((resolve) => {
      this.responseQueue.push(resolve);
    });
  }

  waitRecvBuf( condition : (data : string) => boolean) : Promise<string> {
    return new Promise((resolve, reject) => {
      // This Promise resolves to a string
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return reject(new Error('WebSocket is not open.'));
      }
      const handler = (event : MessageEvent) => {
        const data = event.data.toString();
        if( condition(data) ) {
          this.responseQueue.push(data);
          this.ws!.removeEventListener('message', handler);
          resolve(data);
        }
      }
      this.ws!.addEventListener('message', handler);
      /*
      if( this.responseQueue.length > 0 ) {
        const str = this.responseQueue.shift();
        if( typeof(str) === 'string') {
          resolve(str);
        }
        else
          reject("Invalid data");
      }
      else
        reject("No data yet");
      */
    });
  }

  public getData() : string | null {
    if( this.responseQueue.length > 0) {  
      const str = this.responseQueue.shift();
      if( typeof(str) === 'string') {
        console.log(' *** WS queue: ' + str);
        return str;
      }
    }
    return null; 
  }

  public async waitData() {
      const response = await this.waitRecvBuf((data) => typeof(data) === 'string');
  }

  public async sendrecv(payload : string, condition : (data : string) => boolean) : Promise<string> {
    return new Promise( async (resolve, reject) => {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return reject(new Error('WebSocket is not open.'));
      }

      console.log(' *** WebSocket sendrecv: ' + payload);
      this.ws!.send( payload );
      
      const msg = await this.waitForMessage();
      const data = msg.data.toString();
      if( condition(data) ) {
        resolve(data);
      }
      /*
      const handler = (event : MessageEvent) => {
        const data = event.data.toString();
        if( condition(data) ) {
          this.responseQueue.push(data);
          this.ws!.removeEventListener('message', handler);
          resolve(data);
        }
      }
      this.ws!.addEventListener('message', handler);
      */
    });
  }

  public send(message : string) : boolean {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return false;
      }

      this.ws!.send( message );
      return true;
  }

  public async recv(condition : (data : string) => boolean) : Promise<string> {
    return new Promise( async (resolve, reject) => {
      if (this.ws!.readyState !== WebSocket.OPEN) {
        return reject(new Error('WebSocket is not open.'));
      }
      
      const msg = await this.waitForMessage();
      const data = msg.data.toString();
      if( condition(data) ) {
        resolve(data);
      }
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
