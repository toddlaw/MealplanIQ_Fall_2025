import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';

/**
 * Interface representing a single ingredient row from a recipe.
 */
interface Ingredient {
    name: string;
    quantity: string;
    unit: string;
    state?: string;   // Optional: chopped, diced, softened, etc.
}

/**
 * Represents a "Part" section of ingredients (e.g., "Sauce", "Filling").
 * If no parts exist in the CSV, all ingredients fall under a blank header.
 */
interface Part {
    header: string;
    ingredients: Ingredient[];
}

/**
 * Represents a single instruction step.
 * If step === null, this is treated as a section header instead of a numbered step.
 */
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

    /** Parsed ingredient groups from the recipe or CSV file */
    public parts: Part[] = [];

    /** Parsed step-by-step instructions or section headers */
    public instructions: Instruction[] = [];

    /** Whether to show action buttons (Replace / Cancel) in the dialog */
    public showActions: boolean = false;

    constructor(
        /** Reference to the dialog so actions can close it */
        public dialogRef: MatDialogRef<RecipeDialogComponent>,

        /** Incoming data injected into this dialog */
        @Inject(MAT_DIALOG_DATA) public data: any,

        /** HTTP client used to fetch CSV files (ingredients + instructions) */
        private http: HttpClient
    ) { }

    /**
     * Lifecycle hook: Initializes the dialog by determining how to load and parse
     * recipe details.
     *
     * Behavior:
     *  1. If ingredientsUrl + instructionsUrl are provided:
     *        → Fetch CSV files from the server and parse them.
     *
     *  2. If not:
     *        → Fall back to parsing embedded recipe data:
     *              - custom recipes → ingredients_with_quantities + instructions[]
     *              - legacy recipes → newline-delimited instructions/ingredients
     *
     * This flexibility allows the dialog to support global recipes,
     * custom user recipes, as well as older formats returned by the search results.
     *
     * @author BCIT May 2025
     */
    ngOnInit(): void {
        console.log('=== [RecipeDialog] ngOnInit ===');
        console.log('[RecipeDialog] Raw data:', this.data);
        console.log('[RecipeDialog] ingredientsUrl:', this.data.ingredientsUrl);
        console.log('[RecipeDialog] instructionsUrl:', this.data.instructionsUrl);

        this.showActions = this.data.showActions || false;

        // Prefer CSV-based data if URLs are provided
        if (this.data.ingredientsUrl && this.data.instructionsUrl) {
            console.log('[RecipeDialog] Using CSV URLs to fetch data');
            this.fetchIngredients();
            this.fetchInstructions();
        } else {
            console.log('[RecipeDialog] No CSV URLs, falling back to embedded data');

            // Embedded ingredient structure (custom recipes)
            if (this.data.recipe.ingredients_with_quantities) {
                this.parseDataIntoParts(this.data.recipe.ingredients_with_quantities);
            }

            // Embedded instructions may be string[] or newline-delimited text
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
     * Parses custom ingredient data already structured as array-of-arrays.
     *
     * Custom recipes store ingredients_with_quantities as:
     *   [
     *     ["name","quantity","unit","state"],
     *     ...
     *   ]
     *
     * @param raw Raw ingredient rows
     */
    private parseCustomIngredientsFromArray(raw: any): void {
        if (!Array.isArray(raw) || raw.length === 0) {
            console.warn('[RecipeDialog] No custom ingredients_with_quantities found.');
            return;
        }
        this.parseDataIntoParts(raw);
    }

    /**
     * Wraps custom instructions[] into a CSV-like structure so the existing
     * parseDataIntoInstructions() logic can process it uniformly.
     *
     * @param raw string[] of instructions
     */
    private parseCustomInstructionsFromArray(raw: any): void {
        if (!Array.isArray(raw) || raw.length === 0) {
            console.warn('[RecipeDialog] No custom instructions array found.');
            return;
        }

        const csvData: any[] = [];
        csvData.push(['step', 'instruction']); // header row

        raw.forEach((text: any, index: number) => {
            const cleanText = (text ?? '').toString().trim();
            if (!cleanText) return;
            csvData.push([String(index + 1), cleanText]);
        });

        this.parseDataIntoInstructions(csvData);
    }

    /**
     * Converts a CSV table into an array of Parts.
     *
     * CSV Format (example):
     *   name,qty,unit,state
     *   Part, Dough
     *   Flour,2,cups,
     *   Water,1,cup
     *   Part, Filling
     *   Beef,300,g,ground
     *
     * Behavior:
     *   - The first row is ignored (headers).
     *   - Rows beginning with "Part" start new ingredient sections.
     *   - Other rows become Ingredient entries belonging to the active Part.
     *   - If no "Part" rows exist, ingredients are grouped into a single unnamed section.
     *
     * @param csvData Parsed CSV lines: string[][]
     */
    parseDataIntoParts(csvData: any[]): void {
        let currentPart: Part | null = null;
        const dataRows = csvData.slice(1); // skip header row

        dataRows.forEach(row => {
            const first = (row[0] || '').toString();

            // New section header
            if (first.startsWith('Part')) {
                if (currentPart) {
                    this.parts.push(currentPart);
                }
                currentPart = { header: row[1], ingredients: [] };

                // Ingredient row inside a section
            } else if (currentPart && first !== '') {
                currentPart.ingredients.push({
                    name: first,
                    quantity: row[1],
                    unit: row[2],
                    state: row[3],
                });

                // No section declared yet → put ingredients in default part
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

        // Push last part if any
        if (currentPart) {
            this.parts.push(currentPart);
        }
    }

    /**
     * Converts a CSV table into an array of Instruction objects.
     *
     * CSV Format example:
     *   step,instruction
     *   Part, Making Sauce
     *   1,Heat the oil
     *   2,Add onions
     *   Part, Cooking Pasta
     *   1,Boil water
     *
     * Behavior:
     *   - "Part" rows become section headers (step = null)
     *   - regular numeric rows become instruction steps
     *
     * @param csvData Parsed CSV lines: string[][]
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
                const rawText = (row[1] || '').toString();
                const cleanText = this.normalizeInstructionText(rawText);

                this.instructions.push({
                    step: Number(first),
                    text: cleanText,
                });
            }
        });
    }

    /**
     * Parses Instructions to remove triple quotes used in instructions csv files
     */
    private normalizeInstructionText(raw: string): string {
        if (!raw) return '';

        let t = raw.trim();

        // If wrapped in double-double quotes, strip one layer:
        // ""cut up eggplant"" -> cut up eggplant
        if (t.startsWith('""') && t.endsWith('""')) {
            t = t.slice(2, -2);
        }

        // Collapse any remaining doubled quotes inside to single quotes
        // (CSV escaping of inner quotes)
        t = t.replace(/""/g, '"');

        return t;
    }


    /** Closes the dialog without returning a value */
    close(): void {
        this.dialogRef.close();
    }

    /** Equivalent to "Cancel" – returns false to the caller */
    onCancel(): void {
        this.dialogRef.close(false);
    }

    /** Equivalent to "Replace" – returns true to the caller */
    onReplace(): void {
        this.dialogRef.close(true);
    }

    /**
     * Fetches the ingredient CSV file from the provided URL and parses it.
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
     * Fetches the instruction CSV file from the provided URL and parses it.
     *
     * Includes CSV parsing logic for lines in the format:
     *   1,"Heat the oven"
     * to correctly capture the content inside quotes.
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