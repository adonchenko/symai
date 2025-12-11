export class DataEntity {
    public name:string = "";
    public type:string = "unknown"; // should be 'behavior' or 'action'
    public value:string = "";

    constructor(n?:string, t?:string, v?:string) {
        this.name = n || this.name;
        this.type = t || this.type;
        this.value = v || this.value;
    }
}
