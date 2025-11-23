/**
 * SearchDialogComponent
 * 
 * Angular component responsible for handling recipe search functionality.
 * Allows users to search for recipes by keyword, view suggested results,
 * view detailed recipe information in a dialog, and select a recipe to replace an existing one.
 *
 * @author BCIT May 2025
 */

import { Component } from '@angular/core';
import { MatDialogRef, MatDialog } from '@angular/material/dialog';
import { RecipeService } from 'src/app/services/recipe.service';
import { RecipeDialogComponent } from '../dialogues/recipe/recipe.component';

import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-search-dialog',
  templateUrl: './search-dialog.component.html'
})
export class SearchDialogComponent {
  /** The user-entered search keyword */
  searchTerm: string = '';

  /** List of recipes returned by the search */
  suggestedResults: any[] = [];

  /** Flag indicating whether the current search is an exact match search */
  isExactSearch: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<SearchDialogComponent>,  // Reference to the search dialog itself
    private recipeService: RecipeService,                   // Service for recipe search and retrieval
    private dialog: MatDialog                                // Service to open additional dialogs (e.g. recipe details)
  ) { }

  /** Helper: get the current authenticated user’s UID from localStorage */
  private getUid(): string | null {
    const id = localStorage.getItem('uid'); // adjust if different
    console.log('[SearchDialog] UID =', id);
    return id;
  }


  /**
   * Combined search that merges both global and custom user recipes.
   */
  private runCombinedSearch(term: string, exact: boolean) {
    const uid = this.getUid();

    const global$ = this.recipeService.searchRecipes(term, exact).pipe(
      map(list => list.map(r => ({ ...r, __source: 'global' }))),
      catchError(err => {
        console.error('Global search error:', err);
        return of([]);
      })
    );

    const custom$ = uid
      ? this.recipeService.searchUserRecipes(uid, term, exact).pipe(
        map(list => list.map(r => ({ ...r, __source: 'custom' }))),
        catchError(err => {
          console.error('Custom search error:', err);
          return of([]);
        })
      )
      : of([]);

    forkJoin([global$, custom$])
      .pipe(
        map(([globalResults, customResults]) => {
          const merged = [...customResults, ...globalResults];
          // optional: de-dupe by id if needed
          const seen = new Set();
          return merged.filter(r => {
            const key = `${r.__source}:${r.id}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
          });
        })
      )
      .subscribe(merged => {
        this.suggestedResults = merged;
      });
  }

  /**
   * Triggered when the search input changes.
   * Performs a partial match search if at least 2 characters are entered.
   * Updates the suggestedResults list based on backend results.
   */
  onSearchChange(): void {
    this.isExactSearch = false;
    if (this.searchTerm.length >= 2) {
      this.runCombinedSearch(this.searchTerm, false);
    } else {
      this.suggestedResults = [];
    }
  }

  /**
   * Performs an exact match search when requested by the user.
   * Will only run if the search term is not empty.
   */
  onExactSearch(): void {
    this.isExactSearch = true;
    if (!this.searchTerm) return;
    this.runCombinedSearch(this.searchTerm, true);
  }

  /**
   * Opens a recipe details dialog for the selected recipe.
   * If the user confirms selection in the dialog, closes the search dialog and returns the recipe.
   * 
   * @param recipe - The recipe object selected by the user.
   */
  selectRecipe(recipe: any): void {
    const uid = this.getUid();

    const details$ =
      recipe.__source === 'custom' && uid
        ? this.recipeService.getCustomRecipeDetails(uid, recipe.id)
        : this.recipeService.getRecipeDetails(recipe.id);

    details$.subscribe(
      (fullRecipe) => {
        const isCustom = recipe.__source === 'custom' && !!uid;

        const ingredientsUrl = isCustom
          ? this.recipeService.getCustomIngredientsCsvUrl(uid as string, recipe.id)
          : this.getIngredientsCsvUrl(recipe.id);

        const instructionsUrl = isCustom
          ? this.recipeService.getCustomInstructionsCsvUrl(uid as string, recipe.id)
          : this.getInstructionsCsvUrl(recipe.id);

        const detailDialogRef = this.dialog.open(RecipeDialogComponent, {
          data: {
            recipe: fullRecipe ?? recipe,
            imageUrl: isCustom
              ? 'assets/images/placeholders/placeholder_missing_recipe.png'
              : this.getImageUrl(recipe.id),
            ingredientsUrl,
            instructionsUrl,
            showActions: true
          }
        });

        detailDialogRef.afterClosed().subscribe(confirmed => {
          if (confirmed) {
            this.dialogRef.close(recipe);
          }
        });
      },
      (error) => {
        console.error('Error loading recipe details:', error);
      }
    );
  }

  /**
   * Returns the placeholder image for missing recipes 
   */
  usePlaceholder(ev: Event) {
    (ev.target as HTMLImageElement).src = 'assets/images/placeholders/placeholder_missing_recipe.png';
  }

  /**
   * Returns the public image URL for a recipe.
   * 
   * @param id - The recipe ID
   * @returns A string containing the image URL
   */
  getImageUrl(id: number): string {
    return `https://storage.googleapis.com/mealplaniq-may-2024-recipe-images/${id}.jpg`;
  }

  /**
   * Returns the public URL for a recipe's ingredients CSV file.
   * 
   * @param id - The recipe ID
   * @returns A string containing the ingredients CSV URL
   */
  getIngredientsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
  }

  /**
   * Returns the public URL for a recipe's instructions CSV file.
   * 
   * @param id - The recipe ID
   * @returns A string containing the instructions CSV URL
   */
  getInstructionsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
  }
}
