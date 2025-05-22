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
  ) {}

  /**
   * Triggered when the search input changes.
   * Performs a partial match search if at least 2 characters are entered.
   * Updates the suggestedResults list based on backend results.
   */
  onSearchChange(): void {
    this.isExactSearch = false;
    if (this.searchTerm.length >= 2) {
      this.recipeService.searchRecipes(this.searchTerm).subscribe(
        (results) => {
          this.suggestedResults = results;
        },
        (error) => {
          console.error('Search error:', error);
          this.suggestedResults = [];
        }
      );
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
    if (this.searchTerm.length === 0) return;

    this.recipeService.searchRecipes(this.searchTerm, true).subscribe(
      (results) => {
        this.suggestedResults = results;
      },
      (error) => {
        console.error('Exact search error:', error);
        this.suggestedResults = [];
      }
    );
  }

  /**
   * Opens a recipe details dialog for the selected recipe.
   * If the user confirms selection in the dialog, closes the search dialog and returns the recipe.
   * 
   * @param recipe - The recipe object selected by the user.
   */
  selectRecipe(recipe: any): void {
    this.recipeService.getRecipeDetails(recipe.id).subscribe(
      (fullRecipe) => {
        const detailDialogRef = this.dialog.open(RecipeDialogComponent, {
          data: {
            recipe: recipe,
            imageUrl: this.getImageUrl(recipe.id),
            ingredientsUrl: this.getIngredientsCsvUrl(recipe.id),
            instructionsUrl: this.getInstructionsCsvUrl(recipe.id),
            showActions: true
          },
        });

        // After recipe details dialog closes — if confirmed, return the recipe
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
