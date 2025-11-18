import { Point } from './point';
export class GraphItem {
    public id:string = '';
    public pts:Array<Point> = [];
    public color:string = '#000';
    public parmX : string = "";
    public parmY : string = "";
    public max : Point = new Point(0.,0.);
    public min : Point = new Point(0.,0.);
    
    private newPt : Point | null = null;

    constructor( id:string, px : string, py: string ) {
         this.id = id;
         this.parmX = px;
         this.parmY = py;
    }

    public addPoint(pt:Point) : void {
        this.pts.push(pt);

        console.log("Graph " + this.id + ", new point(" + String(pt.x) + "," + String(pt.y) + ")");
        //console.log("Min: (" + String(this.min.x) + "," + String(this.min.y) + "), Max(" + String(this.max.x) + "," + String(this.max.y) + ")");
        if(pt.x > this.max.x ) this.max.x = pt.x;
        if(pt.x < this.min.x) this.min.x = pt.x;
        if(pt.y > this.max.y) this.max.y = pt.y;
        if(pt.y < this.min.y) this.min.y = pt.y;
    }

    public new_x(v : number) : void {
        if( this.newPt === null ) 
            this.newPt = new Point();
        //console.log(this.id + ": new_x=" + String(v));
        this.newPt.x = v;
    }

    public new_y(v : number) : void {
        if( this.newPt === null ) 
            this.newPt = new Point();
        //console.log(this.id + ": new_y=" + String(v));
        this.newPt.y = v;
    }

    public check() : void {
        if( this.newPt ) {
            this.addPoint( new Point(this.newPt.x, this.newPt.y) );
            this.newPt = null;
        }
    }
    /*
    public setScale(width:number, height:number) : void {
        while( this.range.x * this.scale.x < width/2 ) this.scale.x *= 2.; 
        while( this.range.x * this.scale.x > width ) this.scale.x *= 0.5;

        while( this.range.y * this.scale.y < height/2 ) this.scale.y *= 2.; 
        while( this.range.y * this.scale.y > height ) this.scale.y *= 0.5;

        console.log("Range: (" + String(this.range.x) + "," + String(this.range.y) + "), Scale(" + String(this.scale.x) + "," + String(this.scale.y) + ")");
    }
    */
 
    /*
    public normalizeX(x:number, width:number) : number {
        if(this.min.x < 0.) x -= this.min.x;

        let ret : number = (x*width)/this.range.x;

        //console.log("normalizeX: " + x.toFixed(2) + " -> " + ret.toFixed(2));
        return Math.round(ret);
    }

    public normalizeY(y:number, height:number) : number {
        if(this.min.y < 0.) y -= this.min.y;

        let ret : number = (y*height)/this.range.y;

        //console.log("normalizeY: " + y.toFixed(2) + " -> " + ret.toFixed(2));
        return height-Math.round(ret);
    }

    public normalizePoint(pt: Point, width:number, height:number) : Point {
        let ret = new Point(0., 0.);
        ret.x = this.normalizeX(pt.x,width);
        ret.y = this.normalizeY(pt.y, height);
        return ret;
    }
    */
}
