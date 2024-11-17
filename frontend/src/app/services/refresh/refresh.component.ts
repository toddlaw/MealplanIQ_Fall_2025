import { Component, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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
  deleteRecipe(id: string) {
    return this.http.delete(`/api/recipes/${id}`);
  }
}
