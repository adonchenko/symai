import { Component, Input, SimpleChanges, OnInit, OnDestroy, Injectable } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'
import { PrimeNG } from 'primeng/config';
import { TabsModule } from 'primeng/tabs';
import { SplitterModule } from 'primeng/splitter';
import { ButtonModule } from 'primeng/button';
import { MenubarModule } from 'primeng/menubar';
import {MenuItem} from 'primeng/api';
import { FileSelectEvent } from 'primeng/fileupload';
import { DialogModule } from 'primeng/dialog';
import { SelectModule } from 'primeng/select';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { InputNumberModule } from 'primeng/inputnumber';
import { CheckboxModule } from 'primeng/checkbox';

import { CtlPrefs } from '../ctl-prefs';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-prefs',
  imports: [
            CommonModule,
            TabsModule,
            SplitterModule,
            ButtonModule,
            MenubarModule,
            FormsModule,
            DialogModule, 
            SelectModule, 
            ToggleSwitchModule, 
            InputNumberModule, 
            CheckboxModule,
  ],
  providers:  [ CtlPrefs ],
  templateUrl: './prefs.html',
  styleUrl: './prefs.css'
})

export class Prefs implements OnInit, OnDestroy {
    constructor(private svcCtlPrefs: CtlPrefs, private primeng: PrimeNG) { 
      console.log(" Prefs constructor");
      //this.window = inject(DOCUMENT).defaultView as Window;
      //this.window.localStorage.setItem('myApp', this);
    }

    dlgVisible! : boolean;

    private subs: Subscription[] = [];
    solvers : any = [];

    ngOnInit(): void {
      console.log("ngOnInit Prefs -->");
      this.svcCtlPrefs.getShowDialog().subscribe((newData:boolean)  => {
        console.log("Prefs: getShowDialog = " + newData);
        this.dlgVisible = newData;
      });
      this.svcCtlPrefs.showDialogObs2$.subscribe((newData:boolean)  => {
        console.log("Prefs: getShowDialog2 = " + newData);
        this.dlgVisible = newData;
      });

      this.solvers = [ 
        { label : "SymPy", value : "SymPy" }, 
        { label : "Z3", value : "Z3" },
        { label : "CVC5", value : "CVC5" }
      ];
      console.log(" --> ngOnInit Prefs");
    }

    ngOnDestroy(): void {
      console.log(" --> ngOnDestroy Prefs");
    }
    //ngOnChanges(changes: SimpleChanges) {
    //    console.log(changes);
    //}

    flagUseAI : boolean = false;

    selectedSolver: string = "SymPy";
    maxModels : number = 1;
    reenterCount : number = 1;
    flushSelSolver : boolean = false;
    flushUseAI : boolean = false;
    flushMaxModels : boolean = false;
    flushReenterCount : boolean = false; 

    public showDialog() { this.dlgVisible = true; }

    public confirmPrefs(event: Event) {
        this.dlgVisible = false;
    }

}
