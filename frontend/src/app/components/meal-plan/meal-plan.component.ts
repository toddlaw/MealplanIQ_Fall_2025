import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-meal-plan',
  templateUrl: './meal-plan.component.html',
  styleUrls: ['./meal-plan.component.css']
})
export class MealPlanComponent implements OnInit {
  date: string | null = null;
  response: string | null = null;

  constructor(private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.date = params['date'] || null;
      this.response = params['response'] || null;
      console.log('Date from query:', this.date);
      console.log('response', this.response);
  });
}
}
