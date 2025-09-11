import { Component, ViewChild, ElementRef, signal, OnInit, OnDestroy, AfterViewInit, Injectable  } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

import { PrimeNG } from 'primeng/config';
import { FormsModule } from '@angular/forms'
import { TabsModule } from 'primeng/tabs';
import { SplitterModule } from 'primeng/splitter';
import { MenubarModule } from 'primeng/menubar';
import {MenuItem} from 'primeng/api';
import { FileSelectEvent } from 'primeng/fileupload';


import { Prefs } from './prefs/prefs';
import { CtlPrefs } from './ctl-prefs';


declare function setSizes(): any;
declare function adjustSizes(): any;
declare function setTextareaSizes(id:string): any;
declare function wsWidth(e:HTMLElement): any;
declare function wsHeight(e:HTMLElement): any;


@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet, 
    CommonModule,

    FormsModule,
    TabsModule,
    SplitterModule,
    MenubarModule,

    Prefs
  ],
  providers:  [ CtlPrefs ],

  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App implements OnInit, OnDestroy, AfterViewInit {

    protected readonly title = signal('SymAI Client');

    constructor(private svcCtlPrefs: CtlPrefs, private primeng: PrimeNG) {
        console.log("constructor");
    }

    items: MenuItem[] = [];
    public ngOnInit() {
        console.log("ngOnInit");
        this.items = [
        {
          label:'File', icon:'pi pi-fw pi-file',
          items:[
              { label:'Environment', icon:'pi pi-fw', command: () => this.switchEnv() },
              { label:'Behavior', icon:'pi pi-fw', command: () => this.switchBeh() },
              { label:'Actions', icon:'pi pi-fw', command: () => this.switchAct() },
              { label:'Property', icon:'pi pi-fw', command: () => this.switchTgt() },
              { separator:true },
              { label:'Load', icon:'pi pi-fw' },
              { separator:true },
              { label:'Shutdown', icon:'pi pi-fw' },
            ]
        },
        { label:'Run', icon:'pi pi-fw pi-file',
          items:[
              { label:'Run', icon:'pi pi-fw' },
              { separator:true },
              { label:'One Step', icon:'pi pi-fw' },
              { separator:true },
              { label:'Stop', icon:'pi pi-fw' },
          ]  
        },
        { label: 'Preferences', icon:'pi pi-fw pi-file', command: () => this.showPrefsDialog() }
        //{ separator:true },
        //{ label: 'Server: ', icon:'pi pi-fw pi-file' }

        ];

        if (typeof window !== 'undefined') {
          (window as any)['myApp'] = this;
          (window as any).theProp = "this";
        }
    }

    public ngOnDestroy(): void {
      console.log("ngOnDestroy");
    }

    @ViewChild(Prefs) prefsComponent?: Prefs;

    public ngAfterViewInit(): void {
        console.log("ngOnAfterInit");
        if (typeof window !== 'undefined') {
          (window as any)['myApp'] = this;
          (window as any).theProp = "that";
        }

        if( this.prefsComponent === undefined )
          console.log("prefsComponent undefined");
    }

    // =================================== Splitter
      private splitterTop : number = 75;
      private splitterBottom : number = 25;

    getSplitterTop() {
      return this.splitterTop;
    }  

    getSplitterBottom() {
      return this.splitterBottom;
    }  

    doSplitterResizeElem( ws : HTMLElement, idElem : string  ) {
      const inpElem = document.getElementById(idElem);
      let w : number = 0;
      if(inpElem) {
        setTextareaSizes(idElem);
    /*
        //console.log("ws.style.height="+ws.style.height);
        let h1 : number = wsHeight(ws); //Number(ws.height);
        w = wsWidth(ws);//Number(ws.width);
        if( h1===0) { 
          console.log("ws.clientHeight="+ws.clientHeight);
          h1=Number(ws.clientHeight);
        }
        if(w === 0) {
          console.log("ws.clientWidth="+ws.clientWidth);
          w=Number(ws.clientWidth);
        }
        console.log("Anchor sizes: "+ w + " x " + h1);

        let t1 : number  =  Math.trunc((h1 * Math.trunc(this.splitterTop)) / 100) - 36;
        //console.log("h1=" + h1 + ", h=" +t1)
        inpElem.style.height =  String(t1) + "px";
        inpElem.style.width = String(w-20) + "px";
        inpElem.style.left = "4px";
        //console.log('New Textarea height', inpElem.style.height);
    */
      }
    }

    onSplitterResizeEnd(event: any) {
      //console.log('Splitter resized');
      this.splitterTop = event.sizes[0];
      this.splitterBottom = event.sizes[1];
      console.log('***** New panel sizes:', this.splitterTop,this.splitterBottom);

      const ws = document.getElementById("workspace");
      if(ws) {
        this.doSplitterResizeElem(ws, "txtEnv");
        this.doSplitterResizeElem(ws, "txtBeh");
        this.doSplitterResizeElem(ws, "txtAct");
        this.doSplitterResizeElem(ws, "txtTgt");
      }
    }

    // ================================== Handle uploads
    fileEnvToUpload: File | null = null;
    fileBehToUpload: File | null = null;
    fileActToUpload: File | null = null;
    fileTgtToUpload: File | null = null;
    /* ------------- Content */
    cntEnv : string = '';
    cntBeh : string = '';
    cntAct : string = '';
    cntTgt : string = '';
    
    handleEnvFileInput(event: any): void {
        //const inputElement = event.target as HTMLInputElement;
        console.log("handleEnvFileInput:");
        this.fileEnvToUpload = event.target.files[0];
        if (this.fileEnvToUpload) {
            const reader = new FileReader();
            console.log("FileReader created");             
            
            reader.onload = (e) => {
              const fileContent = reader.result; //e.target.value; // The content of the file
              this.cntEnv = String(fileContent);
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File...");   
            this.cntEnv = "Reading file....";          
            reader.readAsText(this.fileEnvToUpload);
            console.log("cntEnv: " + this.cntEnv); // Do something with the file content
            const ws = document.getElementById("workspace");
            if(ws) {
              this.doSplitterResizeElem(ws, "txtEnv");
            }
        }
        else
          console.log("fileEnvToUpload not found");
    }

    handleActFileInput(event: any): void {
        //const inputElement = event.target as HTMLInputElement;
        console.log("handleActFileInput:");
        this.fileActToUpload = event.target.files[0];
        if (this.fileActToUpload) {
            const reader = new FileReader();
            console.log("FileReader created");             
            
            reader.onload = (e) => {
              const fileContent = reader.result; //e.target.value; // The content of the file
              this.cntAct = String(fileContent);
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File...");             
            this.cntAct = "Reading file...";
            reader.readAsText(this.fileActToUpload);
            console.log("cntAct: " + this.cntAct); // Do something with the file content
            const ws = document.getElementById("workspace");
            if(ws) {
              this.doSplitterResizeElem(ws, "txtAct");
            }
        }
        else
          console.log("fileActToUpload not found");
    }

    handleTgtFileInput(event: any): void {
        //const inputElement = event.target as HTMLInputElement;
        console.log("handleTgtFileInput:");
        this.fileTgtToUpload = event.target.files[0];
        if (this.fileTgtToUpload) {
            const reader = new FileReader();
            console.log("FileReader created");             
            
            reader.onload = (e) => {
              const fileContent = reader.result; //e.target.value; // The content of the file
              this.cntTgt = String(fileContent);
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File...");             
            this.cntTgt = "Reading file...";
            reader.readAsText(this.fileTgtToUpload);
            console.log("cntTgt: " + this.cntTgt); // Do something with the file content
        }
        else
            console.log("fileTgtToUpload not found");
    }

    handleBehFileInput(event: any): void {
        //const inputElement = event.target as HTMLInputElement;
        console.log("handleBehFileInput:");
        this.fileBehToUpload = event.target.files[0];
        if (this.fileBehToUpload) {
            const reader = new FileReader();
            console.log("FileReader created");             
            
            reader.onload = (e) => {
              const fileContent = reader.result; //e.target.value; // The content of the file
              this.cntBeh = String(fileContent);
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File..." + this.fileBehToUpload);             
            this.cntBeh = "Reading file...";
            reader.readAsText(this.fileBehToUpload);
            console.log("cntBeh: " + this.cntBeh); // Do something with the file content
        }
        else
          console.log("fileBehToUpload not found");
    }


    // ================================== utils
    public tabVal: number = 0;
    public getTabValue() : number { return this.tabVal; }
    switchEnv() { this.tabVal = 0; }
    switchBeh() { this.tabVal = 1; }
    switchAct() { this.tabVal = 2; }
    switchTgt() { this.tabVal = 3; }

    dlgVisible : boolean = false;
    isRunning : boolean = false;

    showPrefsDialog() {
      console.log("Call showDialog");
      this.dlgVisible = true;
      if( this.prefsComponent !== undefined )
        this.prefsComponent.showDialog();
      else
        this.svcCtlPrefs.setShowDialog(this.dlgVisible);
    }
}
