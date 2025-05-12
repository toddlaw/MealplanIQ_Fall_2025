import { Component, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root',
})
@Component({
  selector: 'app-refresh',
  templateUrl: './refresh.component.html',
  styleUrls: ['./refresh.component.css'],
})
export class RefreshComponent {
  private apiUrl = 'http://localhost:5000/api/refresh-meal-plan';

  constructor(private http: HttpClient) {}

  refreshRecipe(recipeId: string, mealPlan: any): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { recipe_id: recipeId, meal_plan: mealPlan };
    return this.http.post<any>(this.apiUrl, body, {
      headers: headers,
    });
  }

  private apiUrl_delete = 'http://localhost:5000/api/delete-recipe';

  deleteRecipe(recipeId: string, mealPlan: any): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { recipe_id: recipeId, meal_plan: mealPlan };
    console.log('Request body:', body);
    return this.http.post<any>(this.apiUrl_delete, body, {
      headers: headers,
    });
  }

  private apiUrl_replace = 'http://localhost:5000/api/replace-meal-plan-recipe';

  replaceRecipe(recipeId: string, dayIndex: number, recipeIndex: number, mealPlan: any): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { recipe_id: recipeId, day_index: dayIndex, recipe_index: recipeIndex, meal_plan: mealPlan };
    return this.http.post<any>(this.apiUrl_replace, body, { headers });
  }

}
