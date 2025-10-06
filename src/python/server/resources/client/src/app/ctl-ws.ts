import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class CtlWS {
  public socket$: WebSocketSubject<string> | undefined;
  public URL : string = "";
  public isConnected : boolean = false;

  constructor() {
    //this.socket$ = null; //webSocket('ws://localhost:8080/ws'); // Replace with your WebSocket URL
  }

  // Method to send messages
  sendMessage(message: string): boolean {
    if(this.socket$ !== undefined) {
      this.socket$.next(message);
      return true;
    }
    return false;
  }

  // Method to receive messages as an Observable
  getMessages(): Observable<string> | undefined {
    if(this.socket$ !== undefined) 
      return this.socket$.asObservable();
    return undefined;
  }

  // Optional: Handle connection lifecycle events (open, close, error)
  connect(url: string): void {
    this.socket$ = webSocket({
      url: url, // Replace with your WebSocket URL
      openObserver: {
        next: () => this.setConnected(true, null), 
      },
      closeObserver: {
        next: (event) => this.setConnected(false, event),
      },
      // errorObserver: {
      //   next: (error) => console.error('WebSocket error:', error),
      // },
    });
    this.URL = url;
  }

  disconnect(): void {
    if(this.socket$ !== undefined) 
      this.socket$.complete();
  }

  setConnected( conn: boolean, evt: Event | null ) : void {
    if( conn ) {
      console.log('WebSocket connection opened!');
      this.isConnected = true;
    }
    else {
      console.log('WebSocket connection closed:', evt);
      this.isConnected = false;
    }
  }
}
