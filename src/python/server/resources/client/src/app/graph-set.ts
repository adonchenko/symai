import { Point } from './point';
import { GraphItem } from './graph-item';
import { parmVal } from './parm-val';

export class GraphSet {
    public graphSize : Point = new Point(500., 500.);
    public graphLbls : Point = new Point(48, 24); // fields for data labels

    public graphs: Map<string,GraphItem> = new Map<string,GraphItem>();
    public max : Point = new Point(0.,0.);
    public min : Point = new Point(0.,0.);
    public range : Point = new Point(0.,0.);
    public scale : Point = new Point(1.,1.);
    public defRange : Point = new Point(0.,0.);
    public lastDataRow : string = "";

    maxPts : number = 0;

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
            //val.setPrevData();
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

            //val.checkPrevData();
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
        if(this.range.x === 0.) return x;
        if(this.min.x < 0.) x -= this.min.x;

        let ret : number = (x*width)/this.range.x;

        //console.log("normalizeX: " + x.toFixed(2) + " -> " + ret.toFixed(2));
        return Math.round(ret) + this.graphLbls.x;
    }

    public normalizeY(y:number, height:number) : number {
        if(this.range.y === 0.) return y;
        if(this.min.y < 0.) y -= this.min.y;

        let ret : number = (y*height)/this.range.y;

        //console.log("normalizeY: " + y.toFixed(2) + " -> " + ret.toFixed(2));
        return height-Math.round(ret) - this.graphLbls.y;
    }

    public normalizePoint(pt: Point, width:number, height:number) : Point {
        let ret = new Point(0., 0.);

        //console.log("NormalizePoint: w=" + String(width) + ",h=" + String(height) + ", range=(" + String(this.range.x) + "," + String(this.range.x) + ")");

        ret.x = this.normalizeX(pt.x, width);
        ret.y = this.normalizeY(pt.y, height);
        return ret;
    }

    repaintGrid(svg : SVGElement, zp : Point, w : number, h : number) : void {
        console.log("-> repaint grid");
        var x : number = 1;
        var y : number = 1;
        for( ; x < w; x += this.graphLbls.x ) {
            if( x === zp.x )
                continue;
            const vline = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            vline.setAttribute('stroke', 'rgba(98, 98, 99, 0.94)');
            vline.setAttribute('stroke-width', '1');
            vline.setAttribute('stroke-dasharray', '4 3');
            vline.setAttribute('x1', String(x+this.graphLbls.x));
            vline.setAttribute('y1', '1');
            vline.setAttribute('x2', String(x+this.graphLbls.x));
            vline.setAttribute('y2', String(h-1));
            svg.appendChild(vline);

            var vx = (x*this.range.x)/w + this.min.x;
            var t : string = vx.toFixed(2);
            const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            txt.setAttribute('stroke', 'rgba(7, 7, 7, 0.94)');
            txt.setAttribute('x', String(x-2+this.graphLbls.x));
            txt.setAttribute('y', String(h+8) ); //String(this.graphSize.y-this.graphLbls.y+4));
            txt.setAttribute('font-size', '10');
            txt.setAttribute('letter-spacing', '1');
            txt.innerHTML=t;
            svg.appendChild(txt);
        }
        
        for( ; y < h; y += this.graphLbls.y ) {
            if( y === zp.y )
                continue;
            const hline = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            hline.setAttribute('stroke', 'rgba(98, 98, 99, 0.94)');
            hline.setAttribute('stroke-width', '1');
            hline.setAttribute('stroke-dasharray', '4 3');
            hline.setAttribute('x1', String(1+this.graphLbls.x));
            hline.setAttribute('y1', String(h-this.graphLbls.y-y));
            hline.setAttribute('x2', String(w+this.graphLbls.x));
            hline.setAttribute('y2', String(h-this.graphLbls.y-y));
            svg.appendChild(hline);

            var vy = (y*this.range.y)/h + this.min.y;
            var t : string = vy.toFixed(2);
            const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            txt.setAttribute('stroke', 'rgba(7, 7, 7, 0.94)');
            txt.setAttribute('x', '1');
            txt.setAttribute('y', String(h-1-y));
            txt.setAttribute('font-size', '10');
            txt.setAttribute('letter-spacing', '1');
            txt.innerHTML=t;
            svg.appendChild(txt);
        }
    }
  
    repaintGraphs(svg : SVGElement) : Point {
        console.log("Repaint Graphs ");
        var w = svg.clientWidth - this.graphLbls.x;
        var h = svg.clientHeight - this.graphLbls.y;
        var zeroPt : Point = new Point(0, 0);

        this.defRange.x = w;
        this.defRange.y = h;
        if( this.range.x <= 0. ) this.range.x = this.defRange.x;
        if( this.range.y <= 0. ) this.range.y = this.defRange.y;

        let zp : Point = this.normalizePoint(zeroPt, w, h);
        //zp.x += this.graphLbls.x;
        //zp.y -= this.graphLbls.y;
        
        svg.innerHTML = "";
        //console.log(" --- zero point: (" + zp.x.toFixed(2) + "," + zp.y.toFixed(2) + ")" );
        var x1 = String(zp.x);
        var y1 = '1';
        var x2 = x1;
        var y2 = String(h-1);

        const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line1.setAttribute('stroke', 'rgba(6, 43, 6, 0.94)');
        line1.setAttribute('stroke-width', '2');
        line1.setAttribute('x1', x1);
        line1.setAttribute('y1', y1);
        line1.setAttribute('x2', x2);
        line1.setAttribute('y2', y2);
        svg.appendChild(line1);
        console.log("V-line: (" + x1 + "," + y1 + ", " + x2 + ", " + y2 + ")");

        x1= String(1+this.graphLbls.x);
        y1= String(zp.y+ this.graphLbls.y);
        x2= String(w+this.graphLbls.x-1);
        y2= y1;

        const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line2.setAttribute('stroke', 'rgba(6, 43, 6, 0.94)');
        line2.setAttribute('stroke-width', '2');
        line2.setAttribute('x1', x1);
        line2.setAttribute('y1', y1);
        line2.setAttribute('x2', x2);
        line2.setAttribute('y2', y2);
        svg.appendChild(line2);
        console.log("H-line: (" + x1 + "," + y1 + ", " + x2 + ", " + y2 + ")");

        this.repaintGrid(svg,zp,w,h);

        this.graphs.forEach((val, key) => {
            if(this.maxPts < val.pts.length)
                this.maxPts = val.pts.length;
            this.drawGraph( svg, val, zp, w-2, h-2 ); // w-2, h-2
        });
        return zp;
    }
    
    
    drawGraph( svg : SVGElement, graph : GraphItem, zero : Point, width: number, height: number ) : void {
        console.log("Draw Graph " + graph.id + ", points: " + String(graph.pts.length));
        
        const clr = graph.color;
        var x0 : number = this.normalizeX(graph.pts[0].x, width);  
        var y0 : number = this.normalizeY(graph.pts[0].y, height)+ this.graphLbls.y;  
        for( var idx = 1; idx < graph.pts.length; idx++ ) {
            var x1 : number = this.normalizeX(graph.pts[idx].x, width);  
            var y1 : number = this.normalizeY(graph.pts[idx].y, height)+ this.graphLbls.y;  

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

            /*
            if( graph.labels ) {
                var t : string = '('+String(graph.pts[idx].x)+','+String(graph.pts[idx].y)+')';
                const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                txt.setAttribute('x', String(x1+2));
                txt.setAttribute('y', String(y1-2));
                //txt.setAttribute('class', 'smallTxt');
                txt.setAttribute('font-size', '6');
                txt.setAttribute('letter-spacing', '1');
                txt.innerHTML=t;
                svg.appendChild(txt);
            }
            */

            x0 = x1;
            y0 = y1;
        }
    }
}
