/**
 * SearchDialogComponent
 *
 * Angular component responsible for handling recipe search functionality.
 * It:
 *  - Accepts a search keyword from the user
 *  - Queries both global (shared) recipes and custom user-specific recipes
 *  - Merges and de-duplicates the results
 *  - Lets the user view detailed recipe information in a dialog
 *  - Lets the user confirm a recipe, returning it to the caller to replace
 *    an existing recipe in a meal plan or other context.
 *
 * The component itself is displayed as a dialog and returns the selected
 * recipe via MatDialogRef.close().
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
  /** The user-entered search keyword bound to the search input field. */
  searchTerm: string = '';

  /**
   * List of recipes returned by the combined search.
   *
   * Each entry is a recipe object augmented with a marker:
   *   __source: 'global' | 'custom'
   * so the component knows if it is a global recipe or a custom user recipe.
   */
  suggestedResults: any[] = [];

  /**
   * Flag indicating whether the current search mode is an exact match search.
   * - false: partial / "contains" search
   * - true: exact match search
   *
   * This is used primarily for display or UX cues.
   */
  isExactSearch: boolean = false;

  constructor(
    /** Reference to the search dialog itself (so we can close it with a result). */
    public dialogRef: MatDialogRef<SearchDialogComponent>,

    /** Service for performing recipe search and retrieval (global and user-specific). */
    private recipeService: RecipeService,

    /** Material dialog service used to open the recipe detail dialog (RecipeDialogComponent). */
    private dialog: MatDialog
  ) { }

  /**
   * Helper to retrieve the current authenticated user's UID.
   *
   * This assumes the UID is stored in localStorage under the key 'uid'.
   * If your application uses a different storage / key, this can be adjusted.
   *
   * @returns The UID string or null if not found.
   */
  private getUid(): string | null {
    const id = localStorage.getItem('uid'); // adjust if different
    console.log('[SearchDialog] UID =', id);
    return id;
  }

  /**
   * Core search logic that merges results from both global and custom user recipes.
   *
   * Steps:
   *  1. Build an observable for global recipes via recipeService.searchRecipes().
   *     - Tag each result with __source = 'global'.
   *     - Gracefully handle errors by logging and returning an empty list.
   *
   *  2. If a user ID is available:
   *     - Build an observable for user-specific recipes via recipeService.searchUserRecipes().
   *     - Tag each result with __source = 'custom'.
   *     - Also handle errors by logging and returning an empty list.
   *     If no UID is available, custom$ is just an empty list observable.
   *
   *  3. Use forkJoin([global$, custom$]) to run both in parallel and
   *     combine their final results.
   *
   *  4. Merge custom results first (so they appear at the top), then global.
   *
   *  5. De-duplicate based on a composite key of "__source:id" so the final
   *     list does not contain duplicates from overlapping sources.
   *
   *  6. Assign the merged list to suggestedResults for rendering in the template.
   *
   * @param term  Search term entered by the user.
   * @param exact Flag indicating if this is an exact match search.
   */
  private runCombinedSearch(term: string, exact: boolean) {
    const uid = this.getUid();

    // Global / shared recipes
    const global$ = this.recipeService.searchRecipes(term, exact).pipe(
      // Tag results so we know their source later
      map(list => list.map(r => ({ ...r, __source: 'global' }))),
      catchError(err => {
        console.error('Global search error:', err);
        // Return empty list on error so forkJoin still completes.
        return of([]);
      })
    );

    // Custom user-specific recipes (only if we have a UID)
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
          // Merge custom recipes first, then global recipes
          const merged = [...customResults, ...globalResults];

          // Optional de-duplication logic:
          // We use a composite key "<source>:<id>" as the uniqueness key.
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
        // Final unified list of suggested recipes rendered in the UI.
        this.suggestedResults = merged;
      });
  }

  /**
   * Triggered when the search input changes (e.g., keyup).
   *
   * Behavior:
   *  - Switches into "non-exact" / partial search mode.
   *  - If the term length is >= 2, performs a combined partial search.
   *  - If fewer than 2 characters, clears the suggestions list.
   *
   * This avoids hitting the backend for very short queries.
   */
  onSearchChange(): void {
    this.isExactSearch = false;

    if (this.searchTerm.length >= 2) {
      this.runCombinedSearch(this.searchTerm, false);
    } else {
      // Clear suggestions when the query is too short.
      this.suggestedResults = [];
    }
  }

  /**
   * Performs an *exact* match search when requested by the user.
   *
   * This is typically triggered by a button or some explicit action.
   * It will only run if the search term is non-empty.
   */
  onExactSearch(): void {
    this.isExactSearch = true;
    if (!this.searchTerm) return;
    this.runCombinedSearch(this.searchTerm, true);
  }

  /**
   * Opens a recipe details dialog for the selected recipe and, if the user
   * confirms in that dialog, returns the recipe back to the parent of this
   * search dialog.
   *
   * Steps:
   *  1. Determine if the selected recipe is from the 'custom' or 'global'
   *     source using the __source field and whether a UID exists.
   *  2. Based on the source:
   *     - For custom recipes: use recipeService.getCustomRecipeDetails(uid, id)
   *     - For global recipes: use recipeService.getRecipeDetails(id)
   *  3. Once details are loaded, compute the correct CSV URLs and image URL:
   *     - Custom recipes use recipeService.getCustomIngredientsCsvUrl / getCustomInstructionsCsvUrl
   *       and a local placeholder image.
   *     - Global recipes use public GCS URLs through getImageUrl / getIngredientsCsvUrl / getInstructionsCsvUrl.
   *  4. Open RecipeDialogComponent with all of this data.
   *  5. When the details dialog closes:
   *     - If the user confirmed the selection, close this SearchDialogComponent
   *       and return the chosen recipe via dialogRef.close().
   *
   * @param recipe - The recipe object selected by the user from suggestedResults.
   */
  selectRecipe(recipe: any): void {
    const uid = this.getUid();

    // Choose the proper detail endpoint based on recipe source
    const details$ =
      recipe.__source === 'custom' && uid
        ? this.recipeService.getCustomRecipeDetails(uid, recipe.id)
        : this.recipeService.getRecipeDetails(recipe.id);

    details$.subscribe(
      (fullRecipe) => {
        const isCustom = recipe.__source === 'custom' && !!uid;

        // Ingredients CSV URL differs for custom vs global
        const ingredientsUrl = isCustom
          ? this.recipeService.getCustomIngredientsCsvUrl(uid as string, recipe.id)
          : this.getIngredientsCsvUrl(recipe.id);

        // Instructions CSV URL differs for custom vs global
        const instructionsUrl = isCustom
          ? this.recipeService.getCustomInstructionsCsvUrl(uid as string, recipe.id)
          : this.getInstructionsCsvUrl(recipe.id);

        // Open a second dialog showing the full recipe details
        const detailDialogRef = this.dialog.open(RecipeDialogComponent, {
          data: {
            // If API did not return a full recipe, fall back to the basic recipe object
            recipe: fullRecipe ?? recipe,
            imageUrl: isCustom
              ? 'assets/images/placeholders/placeholder_missing_recipe.png'
              : this.getImageUrl(recipe.id),
            ingredientsUrl,
            instructionsUrl,
            showActions: true    // Allow the user to confirm selection
          }
        });

        // After the detail dialog closes, check if user confirmed
        detailDialogRef.afterClosed().subscribe(confirmed => {
          if (confirmed) {
            // Close the search dialog and return the selected recipe object
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
   * Fallback image handler.
   *
   * When an image fails to load (e.g., broken URL), this method can be bound
   * to the (error) event of the <img>. It swaps the src attribute to a local
   * placeholder image instead.
   *
   * @param ev - The native error event originating from the <img> element.
   */
  usePlaceholder(ev: Event) {
    (ev.target as HTMLImageElement).src = 'assets/images/placeholders/placeholder_missing_recipe.png';
  }

  /**
   * Returns the public image URL for a recipe.
   *
   * NOTE: This uses a hard-coded Google Cloud Storage bucket name. If you
   * later want to make this environment-specific, you can reference
   * environment variables here instead of a literal URL.
   *
   * @param id - The recipe ID.
   * @returns A string containing the image URL.
   */
  getImageUrl(id: number): string {
    return `https://storage.googleapis.com/mealplaniq-may-2024-recipe-images/${id}.jpg`;
  }

  /**
   * Returns the public URL for a recipe's ingredients CSV file.
   *
   * The CSV for ingredients is assumed to live in a fixed bucket with
   * a naming convention "<id>.csv".
   *
   * @param id - The recipe ID.
   * @returns A string containing the ingredients CSV URL.
   */
  getIngredientsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
  }

  /**
   * Returns the public URL for a recipe's instructions CSV file.
   *
   * The CSV for instructions is assumed to live in a fixed bucket with
   * a naming convention "<id>_instructions.csv".
   *
   * @param id - The recipe ID.
   * @returns A string containing the instructions CSV URL.
   */
  getInstructionsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
  }
}
