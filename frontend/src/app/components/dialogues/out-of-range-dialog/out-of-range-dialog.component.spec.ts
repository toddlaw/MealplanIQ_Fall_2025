import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OutOfRangeDialogComponent } from './out-of-range-dialog.component';

describe('OutOfRangeDialogComponent', () => {
  let component: OutOfRangeDialogComponent;
  let fixture: ComponentFixture<OutOfRangeDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OutOfRangeDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OutOfRangeDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
