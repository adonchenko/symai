import { Injectable } from '@angular/core';
import { Subscription, Observable, Subject, BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CtlPrefs {
  private showDialog$ : BehaviorSubject<boolean> = new BehaviorSubject(false);
  private showDialog2 = new Subject<boolean>();
  
  public showDialogObs2$ = this.showDialog2.asObservable();
  //private showDialog: boolean = false;
  
  public getShowDialog() : Observable<boolean> {
    return this.showDialog$.asObservable();
  }

  public getShowDialog2() : Observable<boolean> {
    return this.showDialogObs2$;
  }

  public setShowDialog(newData: boolean) {
    console.log("setShowDialog, service");
    this.showDialog$.next(newData);
    this.showDialog2.next(newData);
  }
 
}
