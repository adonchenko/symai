import { Component, ViewChild, ElementRef, signal, OnInit, OnDestroy, AfterViewInit, Injectable  } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

import { PrimeNG } from 'primeng/config';
import { FormsModule } from '@angular/forms'
import { TabsModule } from 'primeng/tabs';
import { SplitterModule } from 'primeng/splitter';
import { MenubarModule } from 'primeng/menubar';
import {MenuItem} from 'primeng/api';
import { MessageService } from 'primeng/api';
//import { FileSelectEvent } from 'primeng/fileupload';
import { Subscription, of } from 'rxjs';
import { delay } from 'rxjs/operators';

import { Prefs } from './prefs/prefs';
import { CtlPrefs } from './ctl-prefs';
import { CtlWS } from './ctl-ws'; 


// ============================================ JS exports
declare function setSizes(): any;
declare function adjustSizes(): any;
declare function setTextareaSizes(id:string): any;
declare function wsWidth(e:HTMLElement): any;
declare function wsHeight(e:HTMLElement): any;
declare function refreshItem(id: string): any;
declare function diag(msg: string): any;


export const SymAI_coreURL : string = "";

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
  providers:  [ CtlWS, CtlPrefs, MessageService ],

  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App implements OnInit, OnDestroy, AfterViewInit {

    protected readonly title = signal('SymAI Client');
    messages: string[] = [];
    private messageSubscription: Subscription | undefined;

    constructor(private svcWS: CtlWS,
                private svcCtlPrefs: CtlPrefs, 
                private svcMsg: MessageService,
                private primeng: PrimeNG) {
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
              { label:'Reconnect', icon:'pi pi-fw', command: () => this.doReconnect() },
              { separator:true },
              { label:'Stop', icon:'pi pi-fw', disabled: this.isRunning, command: () => this.doStop() },
              { label:'Shutdown', icon:'pi pi-fw', command: () => this.doShutdown() },
            ]
        },
        {
          label:'Data', icon:'pi pi-fw pi-file',
          items:[
              { label:'Load Environment', icon:'pi pi-fw', command: () => this.doLoadEnv() },
              { label:'Load Behavior', icon:'pi pi-fw', command: () => this.doLoadBeh() },
              { label:'Load Actions', icon:'pi pi-fw', command: () => this.doLoadAct() },
              { label:'Load Property', icon:'pi pi-fw', command: () => this.doLoadTgt() },
              { separator:true },
              { label:'Load All', icon:'pi pi-fw', command: () => this.doLoad() },
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
       
        // Subscribe to messages from the WebSocket
        this.svcWS.connect(SymAI_coreURL); // Connect when the component initializes

        this.messageSubscription = this.svcWS.getMessages()!.subscribe(
          (message) => {
            //this.messages.push(message);
            // Process message in some way

            console.log('Received message:', message);
            this.onReceiveMsg(message);
          },
          (error) => console.error('WebSocket error:', error),
          () => { 
            console.log('WebSocket completed.');

            this.svcWS.disconnect();
            this.sleep(1000);
            this.svcWS.connect(SymAI_coreURL); // Connect when the component initializes
          }
        );
    }

    private sleep(ms:number) : void {
        const source = of(1, 2, 3);
        source.pipe(
            delay(ms) // Delay each emission by 1 second
          ).subscribe(value => {}
        );
    }

    public ngOnDestroy(): void {
      this.svcWS.disconnect();
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
          this.msgBox('error', 'Error', 'prefsComponent undefined')
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
        switch(this.tabVal) {
          case 0: this.doSplitterResizeElem(ws, "txtEnv"); break;
          case 1: this.doSplitterResizeElem(ws, "txtBeh"); break;
          case 2: this.doSplitterResizeElem(ws, "txtAct"); break;
          case 3: this.doSplitterResizeElem(ws, "txtTgt"); break;
        }
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
            console.log("cntEnv: " + this.cntEnv);
            refreshItem("txtEnv"); // Do something with the file content
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
            refreshItem("txtAct"); // Do something with the file content
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
    switchEnv() { this.tabVal = 0; setTextareaSizes("txtEnv"); }
    switchBeh() { this.tabVal = 1; setTextareaSizes("txtBeh"); }
    switchAct() { this.tabVal = 2; setTextareaSizes("txtAct"); }
    switchTgt() { this.tabVal = 3; setTextareaSizes("txtTgt"); }

    dlgVisible : boolean = false;
    isRunning : boolean = false;
    cmdCtx : string[] = []; // = ['ldEnv', 'ldBeh', 'ldAct', 'ldTgt', 'stop'];



    showPrefsDialog() {
      console.log("Call showDialog");
      this.dlgVisible = true;
      if( this.prefsComponent !== undefined )
        this.prefsComponent.showDialog();
      else
        this.svcCtlPrefs.setShowDialog(this.dlgVisible);
    }

    msgBox(sev: string, hdr: string, msg: string) : void {
      console.log(hdr + ' : ' + msg);
      this.svcMsg.add({severity:sev, summary:hdr, detail:msg});
    } 

    // ============================================ communication: 
    onReceiveMsg(msg : string) : void {
      if( msg === 'ok' || msg === 'nok' ) {
        if( this.cmdCtx.length > 0 ) {
          const ctx = this.cmdCtx.shift(); 
          switch(ctx) {
            case 'ldEnv':
              if( msg === 'ok' ) {
                console.log("Environment loaded");
                diag("Environment loaded");
              }
              else {
                console.log("Error loading Environment");
                diag("Error loading Environment");
              }
              break;
            case 'ldBeh':
              if( msg === 'ok' ) {
                console.log("Behavior loaded");
                diag("Behavior loaded");
              }
              else {
                console.log("Error loading Behavior");
                diag("Error loading Behavior");
              }
              break;
            case 'ldAct':
              if( msg === 'ok' ) {
                console.log("Actions loaded");
                diag("Actions loaded");
              }
              else {
                console.log("Error loading Actions");
                diag("Error loading Actions");
              }
              break;
            case 'ldTgt':
              if( msg === 'ok' ) {
                console.log("Property loaded");
                diag("Property loaded");
              }
              else {
                console.log("Error loading Property");
                diag("Error loading Property");
              }
              break;
          }
        }
      }
      else
        diag(msg);
    }

    doReconnect() : void {
      this.svcWS.disconnect(); 
      this.sleep(2);
      this.svcWS.connect(SymAI_coreURL);
      this.sleep(4);  
      if( !this.svcWS.isConnected )
        this.msgBox('error', 'Error', 'Could not connect to '+ SymAI_coreURL);
      else
        this.msgBox('info', 'Information', 'Connected');
    }
    
    doShutdown() : void {
      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( this.svcWS.sendMessage("shutdown") )
        this.msgBox('info', 'Information', 'Command sent');
      else 
        this.msgBox('error', 'Error', 'Could not send command');
    }
    
    doStop() : void {
      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( this.svcWS.sendMessage("stop") )
        this.msgBox('info', 'Information', 'Command sent');
      else 
        this.msgBox('error', 'Error', 'Could not send command');
    }

    doLoadEnv() : void {
      if( this.cntEnv === "" ) {
        this.msgBox('error', 'Error', 'Environment is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'environment { "content":' + this.cntEnv + ', "solver":';
      if( this.prefsComponent === undefined )
        msg.concat('SymPy');
      else
        msg.concat(this.prefsComponent.selectedSolver);
      msg.concat('}');

      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( !this.svcWS.sendMessage(msg) )
        this.msgBox('error', 'Error', 'Could not send command');
      else
        this.cmdCtx.push('ldEnv');
    }

    doLoadBeh() : void {
      if( this.cntBeh === "" ) {
        this.msgBox('error', 'Error', 'Behavior is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'behaviors { "content":' + this.cntBeh + '}';
 
      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( !this.svcWS.sendMessage(msg) )
        this.msgBox('error', 'Error', 'Could not send command');
      else
        this.cmdCtx.push('ldBeh');
    }

    doLoadAct() : void {
      if( this.cntAct === "" ) {
        this.msgBox('error', 'Error', 'Actions  empty -- nothing to load');
        return;
      }
      
      var msg : string = 'actions { "content":' + this.cntAct + '}';

      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( !this.svcWS.sendMessage(msg) )
        this.msgBox('error', 'Error', 'Could not send command');
      else
        this.cmdCtx.push('ldAct');
    }

    doLoadTgt() : void {
      if( this.cntTgt === "" ) {
        this.msgBox('error', 'Error', 'Property is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'property { "content":' + this.cntTgt + ', "solver":';
      if( this.prefsComponent === undefined )
        msg.concat('SymPy');
      else
        msg.concat(this.prefsComponent.selectedSolver);
      msg.concat('}');

      if( !this.svcWS.isConnected )
        this.svcWS.connect(SymAI_coreURL);
      if( !this.svcWS.sendMessage(msg) )
        this.msgBox('error', 'Error', 'Could not send command');
      else 
        this.cmdCtx.push('ldTgt');
    }

    doLoad() : void {
      this.doLoadEnv();
      this.doLoadBeh();
      this.doLoadAct();
      this.doLoadTgt();
    }
}
