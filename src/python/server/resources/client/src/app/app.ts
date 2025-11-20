import { Component, ViewChild, ElementRef, signal, OnInit, OnDestroy, AfterViewInit, Injectable  } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

import { PrimeNG } from 'primeng/config';
import { FormsModule } from '@angular/forms'
import { TabsModule } from 'primeng/tabs';
import { SplitterModule } from 'primeng/splitter';
import { MenubarModule } from 'primeng/menubar';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import {MenuItem} from 'primeng/api';
//import { MessageService } from 'primeng/api';
//import { FileSelectEvent } from 'primeng/fileupload';
import { Subscription, of } from 'rxjs';
import { delay } from 'rxjs/operators';

import { Prefs } from './prefs/prefs';
import { CtlPrefs } from './ctl-prefs';
import { CtlWS } from './ctl-ws'; 
import { CtlSyncWS } from './ctl-sync-ws';
import { ChkMenuItem } from './chk-menu-item';

import { TraversalbehCfg } from './traversalbeh-cfg';
import { RequestQue } from './request-que';
import { Point } from './point';
import { GraphSet } from './graph-set';
import { GraphItem } from './graph-item';


// ============================================ JS exports
declare function setSizes(): any;
declare function adjustSizes(): any;
declare function setTextareaSizes(id:string): any;
declare function wsWidth(): any;
declare function wsHeight(): any;
declare function refreshItem(id: string): any;
declare function diag(msg: string): any;
declare function output(msg: string): any;
declare function getItemText(id : string) : any;
declare function clickHiddenRefresh(arg : string) : any;


export const SymAI_coreURL : string = "ws://{CORE_HOST}:{CORE_PORT}";
export const defSolver = "Z3";

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet, 
    CommonModule,

    FormsModule,
    TabsModule,
    SplitterModule,
    MenubarModule,
    ButtonModule,
    DialogModule,


    Prefs
  ],
  providers:  [ CtlWS, CtlPrefs ], //, MessageService ],

  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App implements OnInit, OnDestroy, AfterViewInit {

    protected readonly title = signal('SymAI Client');
    messages: string[] = [];
    private messageSubscription: Subscription | undefined;
    svcSyncWS : CtlSyncWS | null = null;

    constructor(//private svcWS: CtlWS,
                private svcCtlPrefs: CtlPrefs, 
                //private svcMsg: MessageService,
                private primeng: PrimeNG) {
        console.log("constructor");
    }

    SyncWS() : CtlSyncWS {
      if( this.svcSyncWS === null )
        this.svcSyncWS = new CtlSyncWS();
      if( !this.svcSyncWS.isConnected ) {
        this.Diag("Connecting to " + SymAI_coreURL);
        this.svcSyncWS.connect(SymAI_coreURL);
      }
      //else
      //  this.Diag("It seems WebSocket connected");
      return this.svcSyncWS;
    }

    items: ChkMenuItem[] = [];
    itemsRun : ChkMenuItem[] = [];
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
              { label:'Upload Environment', icon:'pi pi-fw', command: () => this.doLoadEnv(false) },
              { label:'Upload Behavior', icon:'pi pi-fw', command: () => this.doLoadBeh(false) },
              { label:'Upload Actions', icon:'pi pi-fw', command: () => this.doLoadAct(false) },
              { label:'Upload Property', icon:'pi pi-fw', command: () => this.doLoadTgt(false) },
              { separator:true },
              //{ label:'Load All', icon:'pi pi-fw', command: () => this.doLoad() },
              { label:'Add Graph...', icon:'pi pi-fw', command: () => this.addGraph() },
            ]
        },
        { label:'Run', icon:'pi pi-fw pi-file',
          items:[
              //{ label:'Run', icon:'pi pi-fw', command : () => this.doRun() },
              { label:'Run', icon:'pi pi-fw', items : [
                  { label : "Default", icon:'pi pi-fw', command: () => this.doRun(false) },
                  { label : "Set start behavior...", icon:'pi pi-fw', command: () => this.doRun(true) },
                ] 
              },
              { separator:true },
              { label:'Debug', icon:'pi pi-fw', checked : this.isDebug, 
                items : [
                  { label:'Start', icon:'pi pi-fw', checked : this.isDebug, command : () => this.doDebug(false) },
                  { label:'Next', icon:'pi pi-fw', checked : this.isDebug, command : () => this.doDebug(true) },
                ]
              },
              { separator:true },
              { label:'Stop', icon:'pi pi-fw', command : () => this.doStop() },
          ]  
        },
        { label: 'Preferences', icon:'pi pi-fw pi-file', command: () => this.showPrefsDialog() }
        //{ separator:true },
        //{ label: 'Server: ', icon:'pi pi-fw pi-file' }

        ];
        this.itemsRun = [
              //{ label:'Run', icon:'pi pi-fw', command : () => this.doRun() },
              { label:'Run', icon:'pi pi-fw', items : [
                  { label : "Default", icon:'pi pi-fw', command: () => this.doRun(false) },
                  { label : "Set start behavior...", icon:'pi pi-fw', command: () => this.doRun(true) },
                ] 
              },
              { separator:true },
              { label:'Debug', icon:'pi pi-fw', checked: this.isDebug, 
                items : [
                  { label:'Start', icon:'pi pi-fw', checked : this.isDebug, command : () => this.doDebug(false) },
                  { label:'Next', icon:'pi pi-fw', checked : this.isDebug, command : () => this.doDebug(true) },
                ]
              },
              { separator:true },
              { label:'Stop', icon:'pi pi-fw', disabled: this.isRunning, command : () => this.doStop() },
        ];

        if (typeof window !== 'undefined') {
          (window as any)['myApp'] = this;
          (window as any).theProp = "this";
        }
       
        /*
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
        */
    }

    public ngOnDestroy(): void {
      if(this.svcSyncWS !== null)
        this.svcSyncWS.disconnect();
      //console.log("ngOnDestroy");
    }

    @ViewChild(Prefs) prefsComponent?: Prefs;

    public ngAfterViewInit(): void {
        //console.log("ngOnAfterInit");
        if (typeof window !== 'undefined') {
          (window as any)['myApp'] = this;
          (window as any).theProp = "that";
        }

        // Subscribe to messages from the WebSocket
        this.SyncWS();

        if( this.prefsComponent === undefined )
          this.msgBox('Error', 'prefsComponent undefined');
    }

    // =================================== Interface menu
    private checkMenu(menu : ChkMenuItem[], lbl : string, chk : boolean ) {
        const itm = menu.find(item => item.label === lbl);
        if(itm)
          itm.checked = chk;
    }

    private disableMenu(menu : MenuItem[], lbl : string, dis : boolean ) {
        const itm = menu.find(item => item.label === lbl);
        if(itm)
          itm.disabled = dis;
    }

    // =================================== Interface Splitter
      private splitterTop : number = 75;
      private splitterBottom : number = 25;

    getSplitterTop() {
      return this.splitterTop;
    }  

    getSplitterBottom() {
      return this.splitterBottom;
    }  

    onSplitterResizeEnd(event: any) {
      //console.log('Splitter resized');
      this.splitterTop = event.sizes[0];
      this.splitterBottom = event.sizes[1];
      //console.log('***** New panel sizes:', this.splitterTop,this.splitterBottom);

      const ws = document.getElementById("workspace");
      if(ws) {
        switch(this.tabVal) {
          case 0: setTextareaSizes("txtEnv"); break;
          case 1: setTextareaSizes("txtBeh"); break;
          case 2: setTextareaSizes("txtAct"); break;
          case 3: setTextareaSizes("txtTgt"); break;
          case 4: setTextareaSizes("runOutput"); break;
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

    waitReadFile(file : any) : Promise<String> {
      return new Promise((resolve) => {
        const reader = new FileReader();
        //console.log("FileReader created");             
        
        reader.onload = (e) => {
          const fileContent = reader.result; //e.target.value; // The content of the file
          resolve(String(fileContent));
          //console.log("cntEnv: " + this.cntEnv);
          //clickHiddenRefresh("txtEnv");
        };
        reader.onerror = (e : any) => {
          console.error("Error reading file:", e.target.error);
          this.msgBox("Error", "Error reading file.");
        };
        
        //console.log("read File...");   
        reader.readAsText(file);
      });
    }
    
    async handleEnvFileInput(event: any) {
        //const inputElement = event.target as HTMLInputElement;
        //console.log("handleEnvFileInput:");
        this.fileEnvToUpload = event.target.files[0];
        if (this.fileEnvToUpload) {
          this.cntEnv = "Reading file....";
          
          const str = await this.waitReadFile(this.fileEnvToUpload); 
          
          this.cntEnv = String(str);
        }
        else
          console.log("fileEnvToUpload not found");
    }

    async handleActFileInput(event: any) {
        //const inputElement = event.target as HTMLInputElement;
        //console.log("handleActFileInput:");
        this.fileActToUpload = event.target.files[0];
        if (this.fileActToUpload) {
          this.cntAct = "Reading file...";

          const str = await this.waitReadFile(this.fileActToUpload); 
          
          this.cntAct = String(str);
        }
        else
          console.log("fileActToUpload not found");
    }

    async handleTgtFileInput(event: any) {
        //const inputElement = event.target as HTMLInputElement;
        //console.log("handleTgtFileInput:");
        this.fileTgtToUpload = event.target.files[0];
        if (this.fileTgtToUpload) {
          this.cntTgt = "Reading file...";

          const str = await this.waitReadFile(this.fileTgtToUpload); 
          
          this.cntTgt = String(str);
        }
        else
            console.log("fileTgtToUpload not found");
    }

    async handleBehFileInput(event: any) {
        //const inputElement = event.target as HTMLInputElement;
        //console.log("handleBehFileInput:");
        this.fileBehToUpload = event.target.files[0];
        if (this.fileBehToUpload) {
          this.cntBeh = "Reading file...";

          const str = await this.waitReadFile(this.fileBehToUpload); 
          
          this.cntBeh = String(str);
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
    switchCons() { this.tabVal = 4; setTextareaSizes("runOutput"); }

    dlgVisible : boolean = false;
    isRunning : boolean = false;
    isDebug : boolean = false;
    cmdCtx : string[] = []; // = ['ldEnv', 'ldBeh', 'ldAct', 'ldTgt', 'stop'];


    private sleep(ms:number) : void {
        const source = of(1, 2, 3);
        source.pipe(
            delay(ms) // Delay each emission by 1 second
          ).subscribe(value => {}
        );
    }

    showPrefsDialog() {
//      console.log("Call showDialog");
      this.dlgVisible = true;
      if( this.prefsComponent !== undefined )
        this.prefsComponent.showDialog();
      else
        this.svcCtlPrefs.setShowDialog(this.dlgVisible);
    }

    msgBox(hdr: string, msg: string) : void {
      console.log("MsgBox: " + hdr + ' : ' + msg);

      const div1 = document.getElementById("msg_hdr");
      if( div1 ) div1.innerText = hdr;
      const div2 = document.getElementById("msg_msg");
      if( div2 ) div2.innerText = msg;
      const box = document.getElementById("MsgBox");
      if(box) box.style.visibility="visible";
      else console.log("Failure with MsgBox");

      if( div2 ) div2.innerText = msg;
      //this.svcMsg.add({severity:sev, summary:hdr, detail:msg});
    }
    
    Diag(msg : string) : void {
      console.log(msg);
      diag(msg);
    }

    // ============================================ communication: 

    doReconnect() : void {
      if(this.svcSyncWS !== null)
        this.svcSyncWS.disconnect(); 
      this.sleep(2);
 
      if( !this.SyncWS().isConnected )
        this.msgBox('Error', 'Could not connect to '+ SymAI_coreURL);
      else
        this.msgBox('Information', 'Connected');
    }
    
    doShutdown() : void {
      if( this.SyncWS().send("shutdown") )
        this.msgBox('Information', 'Command sent');
      else 
        this.msgBox('Error', 'Could not send command');
      this.isDebug = false;
      this.isRunning = false;
      this.envLoaded = false;
      this.behLoaded = false;
      this.actLoaded = false;
      this.tgtLoaded = false;
    }
    
    doStop() : void {
      if( this.SyncWS().send("stop") )
        this.msgBox('Information', 'Command sent');
      else 
        this.msgBox('Error', 'Could not send command');

      this.disableMenu(this.items, "Start", false);
      this.disableMenu(this.itemsRun, "Start", false);

      this.checkMenu(this.items, "Debug", false);
      this.checkMenu(this.itemsRun, "Debug", false);
      
      this.isDebug = false;
      this.isRunning = false;
      this.envLoaded = false;
      this.behLoaded = false;
      this.actLoaded = false;
      this.tgtLoaded = false;
    }

    // ===================================================
    envLoaded : boolean = false;
    actLoaded : boolean = false;
    behLoaded : boolean = false;
    tgtLoaded : boolean = false;
    errLoad : boolean = false;
    private isLoading : number = 0;
    private rque : RequestQue = new RequestQue();

    processLoad() : void {
      if(this.rque.hasRequests() === false) 
        return;
      const msg = this.rque.getRequest();
      const name = this.rque.getDName();
      if( typeof(msg) === 'string' ) {
        if( typeof(name) === 'string')
          this.doLoadData( msg, name);
        else
          this.doLoadData( msg, "");
      }
    }

    async doLoadData( msg: string, dataname: string) {
      /*
      if(this.isLoading > 0) {
        this.rque.postRequest(msg, dataname);
        console.log("=== doLoadData " + dataname + "==> BUSY");      
        return;
      }
      */

      console.log("=============== doLoadData " + dataname + "================");      
      this.errLoad = true;
      try {
        msg.replace(/[\r\n]+/g, ' ');
        this.isLoading++;
        const resp = await this.SyncWS().sendrecv(msg, (data) => typeof(data) === 'string');
        this.isLoading--;
        
        console.log(resp);
        if( resp === 'ok' ) {
          this.errLoad = false;
          this.Diag( dataname + "  loaded");
        }
        else {
          this.Diag("Error loading " + dataname);
          return;
        }
      } catch (error) {
          this.Diag('Error during synchronous message exchange:' + error);
      }

      //this.processLoad(); 
    }

    doLoadEnv(loadNext : boolean) : void {
      if( this.cntEnv === "" ) {
        this.msgBox('Error', 'Environment is empty -- nothing to load');
        return;
      }
      this.Diag("Uploading Environment...");
      
      var msg : string = 'environment ';
      var solver : string = defSolver; 
      if( this.prefsComponent !== undefined ) { 
        this.Diag("Solver: "+ this.prefsComponent.selectedSolver.toString());
        if(this.prefsComponent.selectedSolver === "" )
          solver = defSolver;
        else
          solver = this.prefsComponent.selectedSolver.toString();
      }
      this.cntEnv.replace(/[\r\n]+/g, ' ');
      var cmd = { 
        content : this.cntEnv, 
        solver : solver 
        };
      msg += JSON.stringify(cmd);

      /*
      this.rque.postRequest(msg, "Environment");
      if(this.isLoading <= 0 ) {
        this.isLoading = 0;
        this.processLoad();
      }
      */
      this.doLoadData(msg, "Environment"); 
    }

    doLoadBeh( loadNext : boolean ) : void {
      if( this.cntBeh === "" ) {
        this.msgBox('Error', 'Behavior is empty -- nothing to load');
        return;
      }
      this.Diag("Uploading Behaviors...");
      
      this.cntBeh.replace(/[\r\n]+/g, ' ');
      var msg : string = 'behaviors { "content": "' + this.cntBeh + '" }';

      this.doLoadData(msg, "Behaviors");
      /*
      this.rque.postRequest(msg, "Behaviors");
      if(this.isLoading <= 0 ) {
        this.isLoading = 0;
        this.processLoad();
      }
      */
    }

    doLoadAct(loadNext : boolean) : void {
      if( this.cntAct === "" ) {
        this.msgBox('Error', 'Actions  empty -- nothing to load');
        return;
      }
      this.Diag("Uploading Actions...");
      
      this.cntAct.replace(/[\r\n]+/g, ' ');
      var msg : string = 'actions { "content": "' + this.cntAct + '" }';

      this.doLoadData(msg, "Actions");
    }

    doLoadTgt(loadNext : boolean) : void {
      if( this.cntTgt === "" ) {
        this.msgBox('Error', 'Property is empty -- nothing to load');
        return;
      }
      this.Diag("Uploading Property...");
      this.cntTgt.replace(/[\r\n]+/g, ' ');

      var msg : string = 'property ';
      var solver : string = defSolver; 
      if( this.prefsComponent !== undefined ) { 
        this.Diag("Solver: "+ this.prefsComponent.selectedSolver.toString());
        if(this.prefsComponent.selectedSolver === "" )
          solver = defSolver;
        else
          solver = this.prefsComponent.selectedSolver.toString();
      }
      var cmd = { 
        content : this.cntTgt, 
        solver : solver 
        };
      msg += JSON.stringify(cmd);

      this.doLoadData(msg, "Property");
      //if( !this.errLoad ) 
      //  this.tgtLoaded = true;
    }

    doLoad() : void {
      console.log("========== doLoad =========");
      this.doLoadEnv(false);
      this.doLoadBeh(false);
      this.doLoadAct(false);
      this.doLoadTgt(false);
    }

    dlgStartBeh : boolean = false;
    private startBeh : string = "";

    startBehConfirm() : void {
      console.log("StartBehConfirm...");
      this.startBeh = getItemText("start_beh");
      this.dlgStartBeh = false;

      this.Diag("Auto-upload data...");
      this.doRun2();
    }

    doRun2() : void {
      this.doLoad();

      this.Diag("Start beh=" + this.startBeh);

      var msg : string = "traversalbeh ";
      if( this.startBeh !== "") {
        var parm : TraversalbehCfg = { 
          solver : this.prefsComponent!.selectedSolver,
          behavior : this.startBeh,
          reenter_count : this.prefsComponent!.reenterCount,
          debug : this.isDebug
        };
        
        msg += JSON.stringify(parm);
      }
      else {
        var par = { 
          solver : this.prefsComponent!.selectedSolver,
          reenter_count : this.prefsComponent!.reenterCount,
          debug : this.isDebug
        };
        
        msg += JSON.stringify(par);
      } 

      //console.log("Sending: " + msg);
      this.Diag("Sending: " + msg);

      this.SyncWS().send(msg);
      this.isRunning = true;
      this.tabVal = 4;

      this.recvOutput();
    }

    startBehCancel() : void {
        this.dlgStartBeh = false;
    }

    doRun(selBeh : boolean) : void {
      const out :HTMLDivElement = document.getElementById('runOutput')! as HTMLDivElement;
      out.innerText = "";
      out.innerHTML = ""; 
      //this.doLoad();
      
      //if(!this.envLoaded) { console.log('Environment not loaded'); this.msgBox('Error', 'Environment not loaded'); return; }
      //if(!this.actLoaded) { console.log('Actions not loaded'); this.msgBox('Error', 'Actions not loaded'); return; }
      //if(!this.behLoaded) { console.log('Actions not loaded'); this.msgBox('Error', 'Behaviors not loaded'); return; }
      //if(!this.tgtLoaded) { console.log('Actions not loaded'); this.msgBox('Error', 'Property not loaded'); return; }

      if( this.isDebug ) { // if Already debugging, just send "run" subcommand
        console.log("In debug mode -- switch to batch");

        this.isDebug = false;
        
        this.checkMenu(this.items, "Debug", false);
        this.checkMenu(this.itemsRun, "Debug", false);

        var msg : string = "traversalbeh run";
        this.SyncWS().send(msg);
        this.isRunning = true;

        this.recvOutput();
      }
      else {
        if( selBeh ) {
          this.dlgStartBeh = true;
          // ... and continue from startBehConfirm()
          console.log("DlgStartBeh...");
        }
        else 
          this.doRun2();
      }
    }

    async doDebug(nxt : boolean) {
      //this.doLoad();
      
      //if(!this.envLoaded) { this.Diag('Environment not loaded'); this.msgBox('Error', 'Environment not loaded'); return; }
      //if(!this.actLoaded) { this.Diag('Actions not loaded'); this.msgBox('Error', 'Actions not loaded'); return; }
      //if(!this.behLoaded) { this.Diag('Actions not loaded'); this.msgBox('Error', 'Behaviors not loaded'); return; }
      //if(!this.tgtLoaded) { this.Diag('Actions not loaded'); this.msgBox('Error', 'Property not loaded'); return; }

      if( !nxt ) { // Very beginning
        this.isDebug = true;
        
        this.checkMenu(this.items, "Debug", true );
        this.checkMenu(this.itemsRun, "Debug", true );

        this.dlgStartBeh = true;
        // ... and continue from startBehConfirm()
      }
      else {
        if( !this.isDebug ) {
          this.doDebug( false );
          return;
        }

        this.disableMenu(this.items, "Start", true);
        this.disableMenu(this.itemsRun, "Start", true);
      }     
    }

    async recvOutput() {
      let next = true; 
      while( next ) {
        try {

            console.log("... ... wait for data... ...");
            const resp = await this.SyncWS().recv((data) => typeof(data) === 'string');

            next = this.onReceiveMsg(resp);
            
            /*
            var qstr : string | null;
            while( (qstr = this.SyncWS().getData()) !== null ) {
              console.log("queue: " + qstr);
            }
            */ 
        } catch (error) {
            this.Diag('Error during synchronous message exchange:' + error);
            //next = false;
        }
      }
    }

    onReceiveMsg(msg : string) : boolean {
      msg.replace(/[\r\n]+/g, ' ');
      this.Diag("Recv: " + msg);
      
      var sp1 : number = msg.indexOf(' ', 0);
      //console.log("SP1: " + String(sp1));
      var rsp : string = "";
      var out = msg;
      
      if( sp1 < 0)
        rsp = msg;
      if( sp1 > 0 )
        rsp = msg.substring(0,sp1);

      console.log("RSP: '" + rsp + "'");
      if( rsp === 'nok' ) {
        this.Diag(msg);
        return false;
      }
       
      if( rsp === 'ok' ) {
        var cmd : string = "";
        var sp2 : number = msg.indexOf(' ', sp1+1);
        //console.log("SP2: " + String(sp2));

        if( sp2 < 0 )
          cmd = msg.substring(sp1+1);
        if( sp2 > 0 ) 
          cmd = msg.substring(sp1+1,sp2);

        //console.log("CMD: " + cmd);
        switch( cmd ) {
          case 'start' : // ok start
            return true;
          case 'end' : // ok end
            return false;
          case 'trace': 
          case 'environment':
            out = msg.substring(sp2+1);
            break;
          case 'values':
            this.graphSet.addDataRow(msg.substring(sp2+1)); 
            if(this.graphSet.graphs.size > 0)
            {
              var svg : SVGSVGElement = document.getElementById('myGraph')! as unknown as SVGSVGElement;
              var zp : Point = this.graphSet.repaintGraphs(svg);

              this.graphSet.graphs.forEach((val, key) => {
                  this.graphSet.drawGraph( svg, val, zp, svg.clientWidth-2, svg.clientHeight-2 ); 
              });
              /* ======================== DEBUG
              const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
              line.setAttribute('stroke', '#f00');
              line.setAttribute('stroke-width', '2');
              
              line.setAttribute('x1', String(25));
              line.setAttribute('y1', String(25));
              line.setAttribute('x2', String(300));
              line.setAttribute('y2', String(200));
              svg.appendChild(line);
              */
              console.log("SVG: " + svg.innerHTML);
            }
            return true;
          default:
            return true;
        }
      }

      // Suppose this is an output from Core
      console.log("Output: " + out);
      output(out);
      return true;
    }

    // ============================================================================
    // Graphs

    dlgAddGraph : boolean = false;
    private graphName : string = "";
    graphSet : GraphSet = new GraphSet();
    
    addGraph() : void {
      this.dlgAddGraph = true;
    }

    addGraphCancel() : void {
      this.dlgAddGraph = false;
    }

    addGraphConfirm() : void {
      this.graphName = getItemText("gr_name");
      const clr : HTMLInputElement = document.getElementById("gr_color")! as HTMLInputElement;
      // clr.value;
      console.log("Create graph " + this.graphName + "(" + getItemText('gr_X') + "," + getItemText('gr_Y') + ")");
      this.graphSet.addGraph( this.graphName, getItemText('gr_X'), getItemText('gr_Y'));
      this.dlgAddGraph = false;

      let gi : GraphItem | undefined = this.graphSet.getGraph(this.graphName);
      if( gi !== undefined )
        gi.color = "'" + clr.value + "'";

      var cont : HTMLDivElement = document.getElementById("graph")! as HTMLDivElement;
      /*
      var svg = document.createElement("svg")!;
      svg.style.width='400px';
      svg.style.height='400px';
      svg.id=this.graphName;

      cont.appendChild(svg);
      */
      cont.style.left = String(wsWidth()-420) + 'px';
      cont.style.visibility='visible';
      cont.style.zIndex='9999';
    }

}
