import { DataEntity } from "./data-entity";
import { DataParser } from "./data-parser";

export class TraceData {
    public items:Array<string>=[];

    constructor() {}

    public setTrace( data:string) : void {
        // Trace looks like  '[' Beh, (Beh|Act)*, [REACHED] ']'

        let nits : Array<string> = [];
        var d = data;
        d.replace(/\r\n/g, '');

        var eq = d.indexOf('[');
        if(eq < 0)
            return;
        d = d.substring(eq+1);
        
        eq = d.indexOf(']');
        if(eq > 0) {
            d = d.substring(0,eq);
            d.trimEnd();
        }

        while( d !== '') {
            d.trimStart();
            eq = d.indexOf(',');
            if( eq < 0 ) {
                nits.push( d );
                break;
            }
            nits.push( d.substring(0,eq).trim() );
            d = d.substring(eq+1);
        }

        if( nits.length > this.items.length ) {
            this.items = [];
            for( const item of nits ) {
                this.items.push( item );
            }
        }
    }

    public getTraceStr( dp: DataParser | null ) : string {
        let res : string = "";
        let sep = false;
        for( const item of this.items ) {
            if(sep) {
                if( dp === null )
                    res += '.';
                else {
                    let di : DataEntity | null = dp.getValue(item);
                    if( di !== null ) {
                        if( di.type === 'Beh' )
                            res += ';';
                        else 
                            res += '.';
                    }
                    else 
                        res += ' ';
                }
                res += ' ';
            }
            sep = true;
            res += item;
        }
        return res;
    }
}
