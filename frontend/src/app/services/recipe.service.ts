import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RecipeService {
  private baseUrl = `${environment.baseUrl}/api/recipes`;

  constructor(private http: HttpClient) {}

  searchRecipes(query: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/search?q=${query}`);
  }
}
