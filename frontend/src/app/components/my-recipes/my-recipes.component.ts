import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { BehaviorSubject } from 'rxjs';
import { EditRecipeDialogComponent, EditRecipeData } from './edit-recipe-dialog.component';

export interface Ingredient {
    name: string;
    amount?: number;
    unit?: string;
    note?: string;
}

export interface Recipe {
    id: string;
    title: string;
    ingredients: Ingredient[];
    instructions: string[];
}

const STORAGE_KEY = 'demo_recipes';

function loadRecipes(): Recipe[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch { return []; }
}
function saveRecipes(recipes: Recipe[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(recipes));
}
function deepClone<T>(x: T): T { return JSON.parse(JSON.stringify(x)); }

@Component({
    selector: 'app-my-recipes',
    standalone: true,
    imports: [
        CommonModule,
        HttpClientModule,
        MatButtonModule,
        MatIconModule,
        MatCardModule,
        MatListModule,
        MatDialogModule,
        EditRecipeDialogComponent
    ],
    templateUrl: './my-recipes.component.html',
    styleUrls: ['./my-recipes.component.css']
})
export class MyRecipesComponent {
    private dialog = inject(MatDialog);
    private http = inject(HttpClient);


    // Once we can upload files to these buckets, we can use these functions to get the URLs.
    // getIngredientsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
    // }

    // getInstructionsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
    // }


    // stream of recipes for the template
    recipes$ = new BehaviorSubject<Recipe[]>([]);

    ngOnInit() {
        // if you want "all users" recipes:
        const url = `${environment.baseUrl}/api/recipes`;

        // if/when you want a single user's recipes:
        // const uid = localStorage.getItem('uid') ?? 'gubzy_01';
        // const url = `${environment.baseUrl}/api/recipes?user_id=${encodeURIComponent(uid)}`;

        this.http.get<any[]>(url).subscribe({
            next: (rows) => {
                // Map API rows to your Recipe interface
                const mapped: Recipe[] = rows.map(r => ({
                    id: String(r.id ?? r.number ?? r.title),
                    title: r.title,
                    ingredients: r.ingredients ?? [],   // API sends [], but this keeps it safe
                    instructions: r.instructions ?? []
                }));
                saveRecipes(mapped);       // optional: cache locally
                this.recipes$.next(mapped);
            },
            error: (err) => {
                console.error('Failed to fetch recipes from API, using seed data', err);
                const existing = loadRecipes();
                if (existing.length) {
                    this.recipes$.next(existing);
                    return;
                }
                // seed for first-time run if API fails
                const seed: Recipe[] = [
                    {
                        id: this.newId(),
                        title: 'My Grilled Chicken Sandwich',
                        ingredients: [
                            { name: 'Chicken breasts', amount: 0.5, unit: 'lb' },
                            { name: 'Bread', amount: 2, unit: 'slices', note: 'toasted' },
                            { name: 'Butter', amount: 2, unit: 'tbsp' },
                            { name: 'Salt', note: 'to taste' }
                        ],
                        instructions: [
                            'Cook chicken and cut into slices',
                            'Toast bread then butter',
                            'Place chicken on bread and sprinkle salt'
                        ]
                    }
                ];
                saveRecipes(seed);
                this.recipes$.next(seed);
            }
        });
    }

    addNew() {
        const ref = this.dialog.open(EditRecipeDialogComponent, {
            width: '720px',
            data: {
                mode: 'create',
                recipe: {
                    id: this.newId(),
                    title: 'Untitled Recipe',
                    ingredients: [],
                    instructions: []
                }
            } as EditRecipeData
        });
        ref.afterClosed().subscribe((result?: Recipe) => {
            if (!result) return;
            const next = [...this.recipes$.value, result];
            saveRecipes(next);
            this.recipes$.next(next);
        });
    }

    edit(recipe: Recipe) {
        const ref = this.dialog.open(EditRecipeDialogComponent, {
            width: '720px',
            data: { mode: 'edit', recipe: deepClone(recipe) } as EditRecipeData
        });
        ref.afterClosed().subscribe((updated?: Recipe) => {
            if (!updated) return;
            const next = this.recipes$.value.map(r => r.id === updated.id ? updated : r);
            saveRecipes(next);
            this.recipes$.next(next);
        });
    }

    delete(recipe: Recipe) {
        if (!confirm(`Delete "${recipe.title}"?`)) return;
        const next = this.recipes$.value.filter(r => r.id !== recipe.id);
        saveRecipes(next);
        this.recipes$.next(next);
    }

    private newId(): string {
        // safe fallback if crypto.randomUUID isn’t available
        // @ts-ignore
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            // @ts-ignore
            return crypto.randomUUID();
        }
        return 'id-' + Math.random().toString(36).slice(2);
    }
}
