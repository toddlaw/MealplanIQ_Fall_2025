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
  
    // deleteRecipe(recipeId: string, mealPlan: any): Observable<any> {
  //   const params = new HttpParams()
  //     .set('recipe_id', recipeId)
  //     .set('meal_plan', JSON.stringify(mealPlan)); // Serialize mealPlan to a string
  
  //   return this.http.post<any>(this.apiUrl_delete, { params });
  // }  

}
