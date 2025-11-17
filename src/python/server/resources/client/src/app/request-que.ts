
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { CtlSyncWS } from './ctl-sync-ws'

export class RequestQue {
    public que : string [] = [];
    public names : string [] = [];

    constructor() {}

    public postRequest( req : string, dname : string ) : void {
        this.que.push( req );
        this.names.push( dname );
    }

    public hasRequests() : boolean {
        if( this.que.length > 0 )
            return true;
        return false;
    }

    public getRequest() : string | undefined {
        if( this.que.length > 0 )
            return this.que.shift();
        return undefined;
    }

    public getDName() : string | undefined {
        if( this.names.length > 0 )
            return this.names.shift();
        return undefined;
    }
}
