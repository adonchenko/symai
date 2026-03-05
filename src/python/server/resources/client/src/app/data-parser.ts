import { DataEntity } from "./data-entity";

export class DataParser {
    behStore : Map<string, DataEntity>;
    actStore : Map<string, DataEntity>;

    constructor() {
        this.behStore = new Map<string, DataEntity>();
        this.actStore = new Map<string, DataEntity>();
    }

    public parseBeh(data:string) : number {
        var d = data;
        var ln = 1;
        d.replace(/\r\n/g, '\n');
        while( d !== '') {
            d.trimStart();
            var eq = d.indexOf('=');
            if(eq < 0)
                return ln;
            
            var ky = d.substring(0,eq);
            ky.trim();

            d = d.substring(eq+1);
            d.trimStart();
            var cm = d.indexOf(',');
            if( cm < 0 )
                return ln;
            var val = d.substring(0,cm);
            val.trim();

            this.behStore.set(ky,new DataEntity(ky, "Beh", val));

            d = d.substring(cm+1);
            ln++;
        }
        return ln;
    }

    public parseAct(data:string) : number {
        var d = data;
        var ln = 1;
        d.replace(/\r\n/g, '\n');
        while( d !== '') {
            d.trimStart();
            var eq = d.indexOf(':');
            if(eq < 0)
                return ln;
            
            var ky = d.substring(0,eq);
            ky.trim();

            d = d.substring(eq+1);
            d.trimStart();
            var cm = d.indexOf(',');
            if( cm < 0 )
                return ln;
            var val = d.substring(0,cm);
            val.trim();

            this.actStore.set(ky,new DataEntity(ky, "Act", val));

            d = d.substring(cm+1);
            ln++;
        }
        return ln;
    }

    public getValue(key : string) : DataEntity | null {
        if( this.behStore.has( key ) )
            return this.behStore.get(key)!;
        if( this.actStore.has( key ) )
            return this.actStore.get(key)!;
        return null;
    }
}
