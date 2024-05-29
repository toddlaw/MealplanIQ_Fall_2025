import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-nutrition-chart',
  templateUrl: './nutrition-chart.component.html',
  styleUrls: ['./nutrition-chart.component.css']
})
export class NutritionChartComponent implements OnInit {
  mealPlanResponse = {
    tableData: [
      {
        nutrientName: 'calories',
        display_target: '2000 kcal',
        actual: '1800 kcal',
        status: 'warning'
      },
      {
        nutrientName: 'protein',
        display_target: '50 g',
        actual: '55 g',
        status: 'success'
      },
      {
        nutrientName: 'carbohydrates',
        display_target: '275 g',
        actual: '260 g',
        status: 'warning'
      },
      {
        nutrientName: 'fiber',
        display_target: '30 g',
        actual: '28 g',
        status: 'warning'
      },
      {
        nutrientName: 'sugar',
        display_target: '50 g',
        actual: '45 g',
        status: 'success'
      },
      {
        nutrientName: 'fat',
        display_target: '70 g',
        actual: '65 g',
        status: 'success'
      },
      {
        nutrientName: 'saturated fat',
        display_target: '20 g',
        actual: '18 g',
        status: 'success'
      },
      {
        nutrientName: 'cholesterol',
        display_target: '300 mg',
        actual: '280 mg',
        status: 'success'
      },
      {
        nutrientName: 'sodium',
        display_target: '2300 mg',
        actual: '2200 mg',
        status: 'success'
      },
      {
        nutrientName: 'potassium',
        display_target: '3500 mg',
        actual: '3400 mg',
        status: 'success'
      },
      {
        nutrientName: 'vitamin a',
        display_target: '900 mcg',
        actual: '850 mcg',
        status: 'warning'
      },
      {
        nutrientName: 'vitamin c',
        display_target: '75 mg',
        actual: '80 mg',
        status: 'success'
      },
      {
        nutrientName: 'calcium',
        display_target: '1000 mg',
        actual: '950 mg',
        status: 'warning'
      },
      {
        nutrientName: 'iron',
        display_target: '18 mg',
        actual: '16 mg',
        status: 'warning'
      }
    ]
  };

  displayedColumns: string[] = ['nutrientName', 'target', 'actual'];

  constructor() {}

  ngOnInit(): void {}

  displayVitamin(nutrientName: string): string {
    return nutrientName.charAt(0).toUpperCase() + nutrientName.slice(1).toLowerCase();
  }
}
