import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { RecipeService } from 'src/app/services/recipe.service'; // path may vary

@Component({
  selector: 'app-search-dialog',
  templateUrl: './search-dialog.component.html'
})
export class SearchDialogComponent {
  searchTerm: string = '';
  suggestedResults: any[] = [];

  constructor(
    public dialogRef: MatDialogRef<SearchDialogComponent>,
    private recipeService: RecipeService
  ) {}

  onSearchChange(): void {
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

  selectRecipe(recipe: any): void {
    this.dialogRef.close(recipe);
  }

  getImageUrl(id: number): string {
    return `https://storage.googleapis.com/mealplaniq-may-2024-recipe-images/${id}.jpg`;
  }
}
