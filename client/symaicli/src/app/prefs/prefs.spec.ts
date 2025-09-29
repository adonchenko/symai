import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Prefs } from './prefs';

describe('Prefs', () => {
  let component: Prefs;
  let fixture: ComponentFixture<Prefs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Prefs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Prefs);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
