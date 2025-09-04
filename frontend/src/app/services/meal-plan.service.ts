// meal-plan.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MealPlanService {
  static getMealPlan(path: string): any {
    throw new Error('Method not implemented.');
  }
  private baseUrl = `${environment.baseUrl}/api/mealplan`;
  // private baseUrl = 'http://localhost:5000/api/mealplan'; 
  constructor(private http: HttpClient) {}

  getMealPlan(path: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/${path}`);
  }
}
