import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';

interface Ingredient {
    name: string;
    quantity: string;
    unit: string;
    state?: string;
  }
  
  interface Part {
    header: string;
    ingredients: Ingredient[];
  }  

  interface Instruction {
    step: number | null; 
    text: string;        
}

 @Component({
    selector: 'app-recipe',
    templateUrl: './recipe.component.html',
    styleUrls: ['./recipe.component.css']
})

export class RecipeDialogComponent implements OnInit {
    public parts: Part[] = [];
    public instructions: Instruction[] = [];
  
    constructor(
      public dialogRef: MatDialogRef<RecipeDialogComponent>,
      @Inject(MAT_DIALOG_DATA) public data: any
    ) {}
  
    ngOnInit(): void {
      this.parseDataIntoParts(this.data.recipe.ingredients_with_quantities);
      this.parseDataIntoInstructions(this.data.recipe.instructions);
    }
  
    parseDataIntoParts(csvData: any[]): void {
        let currentPart: Part | null = null;
    
        const dataRows = csvData.slice(1);
    
        dataRows.forEach(row => {
            if (row[0].startsWith("Part")) {
                if (currentPart) {
                    this.parts.push(currentPart);
                }
    
                currentPart = { header: row[1], ingredients: [] };
            } else if (currentPart && row[0] !== "") {
                currentPart.ingredients.push({
                    name: row[0],
                    quantity: row[1],
                    unit: row[2],
                    state: row[3]
                });
            } else if (!currentPart && row[0] !== "") {

                if (!this.parts.length) {
                    this.parts.push({
                        header: "", 
                        ingredients: []
                    });
                }
                this.parts[0].ingredients.push({
                    name: row[0],
                    quantity: row[1],
                    unit: row[2],
                    state: row[3]
                });
            }
        });
    
        if (currentPart) {
            this.parts.push(currentPart);
        }

    }
    parseDataIntoInstructions(csvData: any[]): void {
        const dataRows = csvData.slice(1); 
        let currentInstructionPart: string | null = null;
    
        dataRows.forEach((row) => {
            if (row[0].startsWith("Part")) {
                currentInstructionPart = row[1].replace(/"/g, '');
                if (currentInstructionPart) {
                    this.instructions.push({ step: null, text: currentInstructionPart });
                }
            } else if (row[0] !== "") {
                this.instructions.push({
                    step: Number(row[0]), 
                    text: row[1] || '' 
                });
            }
        });
    }
    
    
    
    close(): void {
      this.dialogRef.close();
    }
}