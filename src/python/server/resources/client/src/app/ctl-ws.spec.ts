import { TestBed } from '@angular/core/testing';

import { CtlWS } from './ctl-ws';

describe('CtlWS', () => {
  let service: CtlWS;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CtlWS);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
