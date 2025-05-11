import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';

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
      @Inject(MAT_DIALOG_DATA) public data: any,
      private http: HttpClient
    ) {}
  
    ngOnInit(): void {
    //   this.parseDataIntoParts(this.data.recipe.ingredients_with_quantities);
        // this.parseDataIntoInstructions(this.data.recipe.instructions);
        this.fetchIngredients();
        this.fetchInstructions();
    }
  
    /**
     * Parses CSV data into an array of Parts, where each Part contains a header and an array of Ingredients.
     * The first row of the CSV data is assumed to be headers and is skipped.
     * Rows starting with "Part" indicate a new section, while subsequent rows within a section are parsed as ingredients.
     * If no "Part" row is encountered initially, ingredients are grouped under an empty header.
     *
     * @param csvData An array of arrays representing the CSV data, where each inner array is a row.
     *
     * @example
     * // Example CSV data structure:
     * // [
     * //   ["", "Header", "", ""],
     * //   ["Part", "Main Ingredients", "", ""],
     * //   ["Ingredient A", "1", "cup", "fresh"],
     * //   ["Ingredient B", "2", "tbsp", "dried"],
     * //   ["Part", "Instructions", "", ""],
     * //   ["Step 1", "Mix well", "", ""]
     * // ]
     */
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

    /**
     * Parses CSV data into an array of Instructions.
     * The first row of the CSV data is assumed to be headers and is skipped.
     * Rows starting with "Part" indicate a new instruction section header,
     * while subsequent rows within a section are parsed as individual instructions with a step number and text.
     *
     * @param csvData An array of arrays representing the CSV data, where each inner array is a row.
     *
     * @example
     * // Example CSV data structure:
     * // [
     * //   ["", "Header"],
     * //   ["Part", "Preparation"],
     * //   ["1", "Chop the onions"],
     * //   ["2", "Sauté with garlic"],
     * //   ["Part", "Cooking"],
     * //   ["1", "Boil the sauce"],
     * //   ["2", "Simmer for 20 minutes"]
     * // ]
     */
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

    /**
     * Fetches ingredient data from a CSV file using an HTTP GET request.
     * The fetched CSV data is then parsed into the parts array using the parseDataIntoParts method.
     *
     * @returns void
     *
     * @example
     * // Assumes this.data.ingredientsUrl is a valid URL pointing to a CSV file.
     * this.fetchIngredients();
     * // After successful fetch, this.parts will be populated with ingredient data.
     */
    fetchIngredients(): void {
        this.http.get(this.data.ingredientsUrl, { responseType: 'text' }).subscribe(csv => {
            const lines = csv.trim().split('\n').map(line => line.split(','));
            this.parseDataIntoParts(lines);
        });
    }

    /**
     * Fetches instruction data from a CSV file using an HTTP GET request.
     * The fetched CSV data is then parsed into the instructions array using the parseDataIntoInstructions method.
     *
     * @returns void
     *
     * @example
     * // Assumes this.data.instructionsUrl is a valid URL pointing to a CSV file.
     * this.fetchInstructions();
     * // After successful fetch, this.instructions will be populated with instruction data.
     */
    fetchInstructions(): void {
        this.http.get(this.data.instructionsUrl, { responseType: 'text' }).subscribe(csv => {
            const lines = csv.trim().split('\n').map(line => {
                const match = line.match(/^(\d+),"(.*)"$/);
                return match ? [match[1], match[2]] : line.split(',');
            });
            this.parseDataIntoInstructions(lines);
        });
    }
}