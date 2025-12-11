import { Point } from './point';
import { GraphItem } from './graph-item';
import { parmVal } from './parm-val';

export class GraphSet {
    public graphs: Map<string,GraphItem> = new Map<string,GraphItem>();
    public max : Point = new Point(0.,0.);
    public min : Point = new Point(0.,0.);
    public range : Point = new Point(0.,0.);
    public scale : Point = new Point(1.,1.);
    public defRange : Point = new Point(0.,0.);
    public lastDataRow : string = "";

    public addGraph(name: string, xParm: string, yParm: string) : void {
        this.graphs.set(name, new GraphItem(name, xParm, yParm));
        if( this.lastDataRow !== "" ) {
            this.addDataRow( this.lastDataRow );
        }
    }

    public getGraph(id:string) : GraphItem | undefined {
        let res: GraphItem | undefined = this.graphs.get(id);
        return res;
    }

    public addDataRow(data:string) : void {
        if(this.graphs.size === 0) return;

        const json = JSON.parse(data); // should be array of arrays

        this.graphs.forEach((val, key) => {
            val.pts = [];
        });
        
        console.log("addDataRow: " + String(json.length) + " items");
        if( json.length > 0 && Array.isArray(json) ) {
            for( let key in json ) {
                if( json[key].length > 0 && Array.isArray(json[key]) ) {
                    let parms : parmVal[] = [];//   Map<string, number> = new Map<string, number>(); 

                    json[key].forEach( item => {
                        for (const k in item) {
                            if (item.hasOwnProperty(k)) {
                                parms.push(new parmVal(k, item[k])); //.set(k, item[k]);
                            }
                        }
                    });

                    this.addPoint(parms);
                }
            }
        }

        this.graphs.forEach((val, key) => {
            val.check();
        });

        this.graphs.forEach((val, key) => {
            if(val.max.x > this.max.x ) this.max.x = val.max.x;
            if(val.min.x < this.min.x) this.min.x = val.min.x;
            if(val.max.y > this.max.y) this.max.y = val.max.y;
            if(val.min.y < this.min.y) this.min.y = val.min.y;
        });
        this.range.x = this.max.x - this.min.x;
        this.range.y = this.max.y - this.min.y;
    }
    
    public addPoint(param:parmVal[]) : void {
        //console.log("Set: addPoint: " + String(param.length) + " values");
        
        param.forEach((item) => {

            for (const entry of this.graphs.entries()) {
                //console.log("Check parm value: parmX=" + entry[1].parmX + ", parmY=" + entry[1].parmY + " <-- " + item.name);
                if( entry[1].parmX === item.name ) {
                    entry[1].new_x(item.val);
                }
                if( entry[1].parmY === item.name ) {
                    entry[1].new_y(item.val);
                }
            }
        });
        for (const entry of this.graphs.entries())
            entry[1].check();
    }

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

        //console.log("NormalizePoint: w=" + String(width) + ",h=" + String(height) + ", range=(" + String(this.range.x) + "," + String(this.range.x) + ")");

        ret.x = this.normalizeX(pt.x,width);
        ret.y = this.normalizeY(pt.y, height);
        return ret;
    }
  
    repaintGraphs(svg : SVGElement) : Point {
        console.log("Repaint Graphs ");
        var w = svg.clientWidth;
        var h = svg.clientHeight;
        var zeroPt : Point = new Point(0, 0);

        this.defRange.x = w;
        this.defRange.y = h;
        if( this.range.x <= 0. ) this.range.x = this.defRange.x;
        if( this.range.y <= 0. ) this.range.y = this.defRange.y;

        let zp : Point = this.normalizePoint(zeroPt, w, h);
        
        svg.innerHTML = "";
        //console.log(" --- zero point: (" + zp.x.toFixed(2) + "," + zp.y.toFixed(2) + ")" );
        
        const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line1.setAttribute('stroke', 'rgba(6, 43, 6, 0.94)');
        line1.setAttribute('stroke-width', '2');
        line1.setAttribute('x1', String(zp.x));
        line1.setAttribute('y1', '1');
        line1.setAttribute('x2', String(zp.x));
        line1.setAttribute('y2', String(h-1));
        svg.appendChild(line1);
        //console.log("V-line: (" + String(zp.x) + ", 1, " + String(zp.x) + ", " + String(zp.y) + ")");

        const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line2.setAttribute('stroke', 'rgba(6, 43, 6, 0.94)');
        line2.setAttribute('stroke-width', '2');
        line2.setAttribute('x1', '1');
        line2.setAttribute('y1', String(zp.y));
        line2.setAttribute('x2', String(w-1));
        line2.setAttribute('y2', String(zp.y));
        svg.appendChild(line2);
        //console.log("H-line: (" + String(zp.x) + ", " + String(zp.y) + ", " + String(w-1) + ", " + String(zp.y) + ")");

        this.graphs.forEach((val, key) => {
            this.drawGraph( svg, val, zp, w-2, h-2 ); 
        });
        return zp;
    }
    
    
    drawGraph( svg : SVGElement, graph : GraphItem, zero : Point, width: number, height: number ) : void {
        console.log("Draw Graph " + graph.id + ", points: " + String(graph.pts.length));
        
        const clr = graph.color;
        var x0 : number = this.normalizeX(graph.pts[0].x, width);  
        var y0 : number = this.normalizeY(graph.pts[0].y, height);  
        for( var idx = 1; idx < graph.pts.length; idx++ ) {
            var x1 : number = this.normalizeX(graph.pts[idx].x, width);  
            var y1 : number = this.normalizeY(graph.pts[idx].y, height);  

            console.log("Color=" + clr + '=' + graph.color);
            //console.log("Line: x0=" + String(x0) + ", y0=" + String(y0) + ", x1=" + String(x1) + ",y1=" + String(y1) );
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('stroke', clr);
            //line.setAttribute('stroke', 'rgba(15, 5, 71, 1)'); //graph.color);
            line.setAttribute('stroke-width', '2');
            
            line.setAttribute('x1', String(x0));
            line.setAttribute('y1', String(y0));
            line.setAttribute('x2', String(x1));
            line.setAttribute('y2', String(y1));
            svg.appendChild(line);

            const circ = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circ.setAttribute('stroke', clr); //graph.color);
            circ.setAttribute('stroke-width', '2');
            
            circ.setAttribute('cx', String(x1));
            circ.setAttribute('cy', String(y1));
            circ.setAttribute('r', '2');
            svg.appendChild(circ);

            var t : string = '('+String(graph.pts[idx].x)+','+String(graph.pts[idx].y)+')';
            const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            txt.setAttribute('x', String(x1+2));
            txt.setAttribute('y', String(y1-2));
            txt.setAttribute('class', 'smallTxt');
            txt.innerHTML=t;
            svg.appendChild(txt);

            x0 = x1;
            y0 = y1;
        }
    }
}
