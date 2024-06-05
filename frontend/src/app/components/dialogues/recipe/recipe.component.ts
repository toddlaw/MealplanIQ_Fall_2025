import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';


 @Component({
    selector: 'app-recipe',
    templateUrl: './recipe.component.html',
    styleUrls: ['./recipe.component.css']
})

export class RecipeDialogComponent {

    constructor(
        public dialogRef: MatDialogRef<RecipeDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any) {}

    close(): void {
        this.dialogRef.close();
      }
}
