import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
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
    styleUrls: ['./recipe.component.css'],
})
export class RecipeDialogComponent implements OnInit {
    public parts: Part[] = [];
    public instructions: Instruction[] = [];
    public showActions: boolean = false;

    constructor(
        public dialogRef: MatDialogRef<RecipeDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        private http: HttpClient
    ) { }

    /**
     * Initializes the component by parsing the recipe data into parts and instructions.
     * If URLs for ingredients and instructions are provided, fetches data from those URLs.
     * Otherwise, parses the data directly from the recipe object:
     *   - custom recipes: ingredients_with_quantities (array) + instructions (array)
     *   - legacy: ingredients / instructions as newline-separated strings
     *
     * @author BCIT May 2025
     */
    ngOnInit(): void {
        console.log('=== [RecipeDialog] ngOnInit ===');
        console.log('[RecipeDialog] Raw data:', this.data);
        console.log('[RecipeDialog] ingredientsUrl:', this.data.ingredientsUrl);
        console.log('[RecipeDialog] instructionsUrl:', this.data.instructionsUrl);

        this.showActions = this.data.showActions || false;

        if (this.data.ingredientsUrl && this.data.instructionsUrl) {
            console.log('[RecipeDialog] Using CSV URLs to fetch data');
            this.fetchIngredients();
            this.fetchInstructions();
        } else {
            console.log('[RecipeDialog] No CSV URLs, falling back to embedded data');
            // only used for legacy / search-results-with-inline-data cases
            if (this.data.recipe.ingredients_with_quantities) {
                this.parseDataIntoParts(this.data.recipe.ingredients_with_quantities);
            }
            if (this.data.recipe.instructions) {
                const instructionsArray = Array.isArray(this.data.recipe.instructions)
                    ? this.data.recipe.instructions
                    : String(this.data.recipe.instructions)
                        .split('\n')
                        .map((line: string, idx: number) => [String(idx + 1), line]);
                this.parseDataIntoInstructions(instructionsArray);
            }
        }
    }



    /**
     * Custom recipes: ingredients_with_quantities is already an array-of-arrays
     * with a header row at index 0. We can feed it directly to parseDataIntoParts.
     */
    private parseCustomIngredientsFromArray(raw: any): void {
        if (!Array.isArray(raw) || raw.length === 0) {
            console.warn('[RecipeDialog] No custom ingredients_with_quantities found.');
            return;
        }
        this.parseDataIntoParts(raw);
    }

    /**
     * Custom recipes: instructions is just an array of strings.
     * We wrap it into a CSV-like structure to reuse parseDataIntoInstructions.
     */
    private parseCustomInstructionsFromArray(raw: any): void {
        if (!Array.isArray(raw) || raw.length === 0) {
            console.warn('[RecipeDialog] No custom instructions array found.');
            return;
        }

        const csvData: any[] = [];
        // header row (ignored by parseDataIntoInstructions, but keeps structure consistent)
        csvData.push(['step', 'instruction']);

        raw.forEach((text: any, index: number) => {
            const cleanText = (text ?? '').toString().trim();
            if (!cleanText) return;
            csvData.push([String(index + 1), cleanText]);
        });

        this.parseDataIntoInstructions(csvData);
    }

    /**
     * Parses CSV data into an array of Parts, where each Part contains a header and an array of Ingredients.
     * The first row of the CSV data is assumed to be headers and is skipped.
     * Rows starting with "Part" indicate a new section, while subsequent rows within a section are parsed as ingredients.
     * If no "Part" row is encountered initially, ingredients are grouped under an empty header.
     *
     * @param csvData An array of arrays representing the CSV data, where each inner array is a row.
     *
     * @author BCIT May 2025
     */
    parseDataIntoParts(csvData: any[]): void {
        let currentPart: Part | null = null;
        const dataRows = csvData.slice(1);

        dataRows.forEach(row => {
            const first = (row[0] || '').toString();
            if (first.startsWith('Part')) {
                if (currentPart) {
                    this.parts.push(currentPart);
                }
                currentPart = { header: row[1], ingredients: [] };
            } else if (currentPart && first !== '') {
                currentPart.ingredients.push({
                    name: first,
                    quantity: row[1],
                    unit: row[2],
                    state: row[3],
                });
            } else if (!currentPart && first !== '') {
                if (!this.parts.length) {
                    this.parts.push({ header: '', ingredients: [] });
                }
                this.parts[0].ingredients.push({
                    name: first,
                    quantity: row[1],
                    unit: row[2],
                    state: row[3],
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
     * @author BCIT May 2025
     */
    parseDataIntoInstructions(csvData: any[]): void {
        const dataRows = csvData.slice(1);
        let currentInstructionPart: string | null = null;

        dataRows.forEach(row => {
            const first = (row[0] || '').toString();
            if (first.startsWith('Part')) {
                currentInstructionPart = (row[1] || '').replace(/"/g, '');
                if (currentInstructionPart) {
                    this.instructions.push({ step: null, text: currentInstructionPart });
                }
            } else if (first !== '') {
                this.instructions.push({
                    step: Number(first),
                    text: row[1] || '',
                });
            }
        });
    }


    close(): void {
        this.dialogRef.close();
    }

    onCancel(): void {
        this.dialogRef.close(false);
    }

    onReplace(): void {
        this.dialogRef.close(true);
    }

    /**
     * Fetches ingredient data from a CSV file using an HTTP GET request.
     * The fetched CSV data is then parsed into the parts array using the parseDataIntoParts method.
     *
     * @author BCIT May 2025
     */
    fetchIngredients(): void {
        this.http
            .get(this.data.ingredientsUrl, { responseType: 'text' })
            .subscribe((csv) => {
                const lines = csv
                    .trim()
                    .split('\n')
                    .map((line) => line.split(','));
                this.parseDataIntoParts(lines);
            });
    }

    /**
     * Fetches instruction data from a CSV file using an HTTP GET request.
     * The fetched CSV data is then parsed into the instructions array using the parseDataIntoInstructions method.
     *
     * @author BCIT May 2025
     */
    fetchInstructions(): void {
        this.http
            .get(this.data.instructionsUrl, { responseType: 'text' })
            .subscribe((csv) => {
                const lines = csv.trim().split('\n').map((line) => {
                    const match = line.match(/^(\d+),"(.*)"$/);
                    return match ? [match[1], match[2]] : line.split(',');
                });
                this.parseDataIntoInstructions(lines);
            });
    }
}
