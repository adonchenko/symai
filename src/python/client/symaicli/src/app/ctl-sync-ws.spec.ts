import { TestBed } from '@angular/core/testing';

import { CtlSyncWS } from './ctl-sync-ws';

describe('CtlSyncWS', () => {
  let service: CtlSyncWS;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CtlSyncWS);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
