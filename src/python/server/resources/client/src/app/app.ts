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
import { MessageService } from 'primeng/api';
//import { FileSelectEvent } from 'primeng/fileupload';
import { Subscription, of } from 'rxjs';
import { delay } from 'rxjs/operators';

import { Prefs } from './prefs/prefs';
import { CtlPrefs } from './ctl-prefs';
import { CtlWS } from './ctl-ws'; 
import { CtlSyncWS } from './ctl-sync-ws';
import { ChkMenuItem } from './chk-menu-item';
import { TraversalbehCfg } from './traversalbeh-cfg';


// ============================================ JS exports
declare function setSizes(): any;
declare function adjustSizes(): any;
declare function setTextareaSizes(id:string): any;
declare function wsWidth(e:HTMLElement): any;
declare function wsHeight(e:HTMLElement): any;
declare function refreshItem(id: string): any;
declare function diag(msg: string): any;
declare function output(msg: string): any;
declare function getItemText(id : string) : any;


export const SymAI_coreURL : string = "ws://{CORE_HOST}:{CORE_PORT}";

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
  providers:  [ CtlWS, CtlPrefs, MessageService ],

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
                private svcMsg: MessageService,
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
      else
        this.Diag("It seems WebSocket connected");
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
              { label:'Run', icon:'pi pi-fw', command : () => this.doRun() },
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
              { label:'Run', icon:'pi pi-fw', command : () => this.doRun() },
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
      console.log("ngOnDestroy");
    }

    @ViewChild(Prefs) prefsComponent?: Prefs;

    public ngAfterViewInit(): void {
        console.log("ngOnAfterInit");
        if (typeof window !== 'undefined') {
          (window as any)['myApp'] = this;
          (window as any).theProp = "that";
        }

        // Subscribe to messages from the WebSocket
        this.SyncWS();

        if( this.prefsComponent === undefined )
          this.msgBox('error', 'Error', 'prefsComponent undefined')
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
      console.log('***** New panel sizes:', this.splitterTop,this.splitterBottom);

      const ws = document.getElementById("workspace");
      if(ws) {
        switch(this.tabVal) {
          case 0: setTextareaSizes("txtEnv"); break;
          case 1: setTextareaSizes("txtBeh"); break;
          case 2: setTextareaSizes("txtAct"); break;
          case 3: setTextareaSizes("txtTgt"); break;
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
              refreshItem("txtEnv");
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
              refreshItem("txtAct");
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
              refreshItem("txtTgt");
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File...");             
            this.cntTgt = "Reading file...";
            reader.readAsText(this.fileTgtToUpload);
            console.log("cntTgt: " + this.cntTgt); 
            refreshItem("txtTgt"); // Do something with the file content
            
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
              refreshItem("txtBeh");
            };
            reader.onerror = (e : any) => {
              console.error("Error reading file:", e.target.error);
              console.log("Error reading file.");
            };
            
            console.log("read File..." + this.fileBehToUpload);             
            this.cntBeh = "Reading file...";
            reader.readAsText(this.fileBehToUpload);
            console.log("cntBeh: " + this.cntBeh); 
            refreshItem("txtBeh");// Do something with the file content
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
        this.msgBox('error', 'Error', 'Could not connect to '+ SymAI_coreURL);
      else
        this.msgBox('info', 'Information', 'Connected');
    }
    
    doShutdown() : void {
      if( this.SyncWS().send("shutdown") )
        this.msgBox('info', 'Information', 'Command sent');
      else 
        this.msgBox('error', 'Error', 'Could not send command');
    }
    
    doStop() : void {
      if( this.SyncWS().send("stop") )
        this.msgBox('info', 'Information', 'Command sent');
      else 
        this.msgBox('error', 'Error', 'Could not send command');

      this.disableMenu(this.items, "Start", false);
      this.disableMenu(this.itemsRun, "Start", false);

      this.checkMenu(this.items, "Debug", false);
      this.checkMenu(this.itemsRun, "Debug", false);
      
      this.isDebug = false;
      this.isRunning = false;
    }

    async doLoadData( msg: string, dataname: string) {
      try {
        const resp = await this.SyncWS().sendrecv(msg);
        if( resp === 'ok' ) {
          this.Diag( dataname + "  loaded");
        }
        else {
          this.Diag("Error loading " + dataname);
        }
      } catch (error) {
          this.Diag('Error during synchronous message exchange:' + error);
      }

    }

    doLoadEnv() : void {
      if( this.cntEnv === "" ) {
        this.msgBox('error', 'Error', 'Environment is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'environment { "content":"' + this.cntEnv + '", "solver": "';
      if( this.prefsComponent === undefined )
        msg.concat('SymPy');
      else { 
        this.Diag("Solver: "+ this.prefsComponent.selectedSolver);
        if(this.prefsComponent.selectedSolver === "" )
          msg += 'SymPy';
        else
          msg += this.prefsComponent.selectedSolver;
      }
      msg += '" }';

      this.doLoadData(msg, "Environment");      
    }

    doLoadBeh() : void {
      if( this.cntBeh === "" ) {
        this.msgBox('error', 'Error', 'Behavior is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'behaviors { "content": "' + this.cntBeh + '" }';

      this.doLoadData(msg, "Behaviors");
    }

    doLoadAct() : void {
      if( this.cntAct === "" ) {
        this.msgBox('error', 'Error', 'Actions  empty -- nothing to load');
        return;
      }
      
      var msg : string = 'actions { "content": "' + this.cntAct + '" }';

      this.doLoadData(msg, "Actions");
    }

    async doLoadTgt() {
      if( this.cntTgt === "" ) {
        this.msgBox('error', 'Error', 'Property is empty -- nothing to load');
        return;
      }
      
      var msg : string = 'property { "content": "' + this.cntTgt + '", "solver": "';
      if( this.prefsComponent === undefined )
        msg.concat('SymPy');
      else if(this.prefsComponent.selectedSolver === "" )
        msg.concat('SymPy');
      else
        msg.concat(this.prefsComponent.selectedSolver);
      msg.concat('" }');

      this.doLoadData(msg, "Property");
    }

    doLoad() : void {
      this.doLoadEnv();
      this.doLoadBeh();
      this.doLoadAct();
      this.doLoadTgt();
    }

    dlgStartBeh : boolean = false;
    private startBeh : string = "";

    startBehConfirm() : void {
        this.dlgStartBeh = false;
        this.startBeh = getItemText("start_beh");

        var msg : string = "traversalbeh ";
        var parm : TraversalbehCfg = { 
          solver : this.prefsComponent!.selectedSolver,
          behavior : this.startBeh,
          reenter_count : this.prefsComponent!.reenterCount,
          debug : this.isDebug
        };
        msg += JSON.stringify(parm);
        this.SyncWS().send(msg);
        this.isRunning = true;

        this.recvOutput();
    }

    startBehCancel() : void {
        this.dlgStartBeh = false;
    }

    doRun() : void {
      if( this.isDebug ) { // if Already debugging, just send "run" subcommand
        this.isDebug = false;
        
        this.checkMenu(this.items, "Debug", false);
        this.checkMenu(this.itemsRun, "Debug", false);

        var msg : string = "traversalbeh run";
        this.SyncWS().send(msg);
        this.isRunning = true;

        this.recvOutput();
      }
      else {
        this.dlgStartBeh = true;
        // ... and continue from startBehConfirm()
      }
    }

    async doDebug(nxt : boolean) {
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
      try {
          const resp = await this.SyncWS().recv();

          this.onReceiveMsg(resp);
      } catch (error) {
          this.Diag('Error during synchronous message exchange:' + error);
      }
    }

    onReceiveMsg(msg : string) : void {
      var sp1 : number = msg.indexOf(' ', 0);
      if( sp1 > 0 ) {
        var rsp : string = msg.substring(0,sp1-1);
        if( rsp === 'nok' || rsp === 'ok' ) {
          this.Diag(msg);
          return;
        }
      }
      // Suppose this is an output from Core
      output(msg);
    }

}
