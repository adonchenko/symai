import { TestBed } from '@angular/core/testing';

import { CtlPrefs } from './ctl-prefs';

describe('CtlPrefs', () => {
  let service: CtlPrefs;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CtlPrefs);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
