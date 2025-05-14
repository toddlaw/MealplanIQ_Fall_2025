import { Component } from '@angular/core';
import { MatDialogRef, MatDialog } from '@angular/material/dialog';
import { RecipeService } from 'src/app/services/recipe.service'; // path may vary
import { RecipeDialogComponent } from '../dialogues/recipe/recipe.component';

@Component({
  selector: 'app-search-dialog',
  templateUrl: './search-dialog.component.html'
})
export class SearchDialogComponent {
  searchTerm: string = '';
  suggestedResults: any[] = [];
  isExactSearch: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<SearchDialogComponent>,
    private recipeService: RecipeService,
    private dialog: MatDialog // Add MatDialog injection
  ) {}

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

  selectRecipe(recipe: any): void {
    this.recipeService.getRecipeDetails(recipe.id).subscribe(
      (fullRecipe) => {
        const detailDialogRef = this.dialog.open(RecipeDialogComponent, { // Use injected dialog
        data: {
          recipe: recipe,
          imageUrl: this.getImageUrl(recipe.id),
          ingredientsUrl: this.getIngredientsCsvUrl(recipe.id),
          instructionsUrl: this.getInstructionsCsvUrl(recipe.id),
          showActions: true
        },
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

  getImageUrl(id: number): string {
    return `https://storage.googleapis.com/mealplaniq-may-2024-recipe-images/${id}.jpg`;
  }

    getIngredientsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
  }

  getInstructionsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
  }
  
}
