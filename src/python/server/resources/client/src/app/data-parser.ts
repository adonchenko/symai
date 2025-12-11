import { DataEntity } from "./data-entity";

export class DataParser {
    dataStore : Map<string, DataEntity>;

    constructor() {
        this.dataStore = new Map<string, DataEntity>();
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

            this.dataStore.set(ky,new DataEntity(ky, "Behavior", val));

            d = d.substring(cm+1);
            ln++;
        }
        return 0;
    }

    public parseAct(data:string) : number {
        return 0;
    }

    public getValue(key : string) : DataEntity | null {
        return null;
    }
}
