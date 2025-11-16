export class Point {
    public x : number = 0;
    public y : number = 0;

    constructor(x?:number,y?:number) {
        this.x=x||this.x;
        this.y=y||this.y;
    }
}
