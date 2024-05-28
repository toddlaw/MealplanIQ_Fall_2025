import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';


 @Component({
    selector: 'app-recipe',
    templateUrl: './recipe.component.html',
    styleUrls: ['./recipe.component.css']
})

export class RecipeDialogComponent {
    popup: boolean = true;
    constructor(@Inject(MAT_DIALOG_DATA) public data: any) {}

    closeRecipeDialog() {
        this.popup = false;
    }

}
