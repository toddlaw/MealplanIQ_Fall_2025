import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NutritionChartComponent } from './nutrition-chart.component';

describe('NutritionChartComponent', () => {
  let component: NutritionChartComponent;
  let fixture: ComponentFixture<NutritionChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NutritionChartComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NutritionChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
