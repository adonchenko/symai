export class parmVal {
    name:string = "";
    val:number = 0.;

    constructor(n? : string, v?: number) {
        this.name = n || this.name;
        this.val = v || this.val;
    }
}
