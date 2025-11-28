/**
 * RecipeService
 *
 * Centralized service responsible for interacting with the backend
 * recipe-related API endpoints, both global recipes and user-specific
 * custom recipes.
 *
 * This service:
 *   - Searches global recipes
 *   - Searches user-owned custom recipes
 *   - Retrieves full recipe details (global + custom)
 *   - Provides helper functions to generate URLs for CSV downloads
 *     (ingredients + instructions)
 *
 * All requests use HttpClient and automatically respect Angular's
 * dependency injection system.
 *
 * @author BCIT May 2025
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RecipeService {

  /**
   * Base URL for global recipe routes.
   *
   * Example:
   *   http://localhost:5000/api/recipes
   */
  private baseUrl = `${environment.baseUrl}/api/recipes`;

  constructor(private http: HttpClient) { }

  /**
   * Search global recipes (non-user-owned) by query.
   *
   * @param query - The user's search input
   * @param exact - Whether the backend should run exact-match mode
   *
   * Endpoint:
   *   GET /api/recipes/search?q=<query>&exact=<boolean>
   *
   * @returns Observable<any[]> - list of recipe summaries
   */
  searchRecipes(query: string, exact: boolean = false): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/search?q=${query}&exact=${exact}`
    );
  }

  /**
   * Retrieve detailed information for a global recipe.
   *
   * @param id - The numeric recipe ID from the global database
   *
   * Endpoint:
   *   GET /api/recipes/:id
   *
   * @returns Observable<any> - full recipe data (title, ingredients, instructions, metadata, etc.)
   */
  getRecipeDetails(id: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/${id}`);
  }

  /**
   * Search user-specific custom recipes.
   *
   * @param uid   - The authenticated user's ID
   * @param q     - The search term
   * @param exact - Exact match or partial match mode
   *
   * Endpoint:
   *   GET /api/custom-recipes/<uid>/search?q=<query>&exact=<boolean>
   *
   * @returns Observable<any[]> - list of custom recipe summaries
   */
  searchUserRecipes(uid: string, q: string, exact = false) {
    return this.http.get<any[]>(
      `${environment.baseUrl}/api/custom-recipes/${encodeURIComponent(uid)}/search?q=${encodeURIComponent(q)}&exact=${exact}`
    );
  }

  /**
   * Retrieve a single custom recipe belonging to the authenticated user.
   *
   * @param uid - User ID
   * @param id  - Custom recipe number / ID
   *
   * Endpoint:
   *   GET /api/custom-recipes/<uid>/<id>
   *
   * @returns Observable<any> - full custom recipe data
   */
  getCustomRecipeDetails(uid: string, id: number) {
    return this.http.get<any>(
      `${environment.baseUrl}/api/custom-recipes/${encodeURIComponent(uid)}/${id}`
    );
  }

  /**
   * Generate the backend-served CSV download URL for a custom recipe's ingredients.
   * The backend reads the CSV from storage and streams it to the client.
   *
   * @param uid - User ID
   * @param id  - Custom recipe ID
   *
   * Endpoint:
   *   GET /api/custom-recipes/<uid>/<id>/ingredients.csv
   *
   * @returns string - full URL to ingredients CSV
   */
  getCustomIngredientsCsvUrl(uid: string, id: number): string {
    return `${environment.baseUrl}/api/custom-recipes/${encodeURIComponent(uid)}/${id}/ingredients.csv`;
  }

  /**
   * Generate the backend-served CSV download URL for a custom recipe's instructions.
   *
   * @param uid - User ID
   * @param id  - Custom recipe ID
   *
   * Endpoint:
   *   GET /api/custom-recipes/<uid>/<id>/instructions.csv
   *
   * @returns string - full URL to instructions CSV
   */
  getCustomInstructionsCsvUrl(uid: string, id: number): string {
    return `${environment.baseUrl}/api/custom-recipes/${encodeURIComponent(uid)}/${id}/instructions.csv`;
  }
}
