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

import { Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { UsersService } from 'src/app/services/users.service';


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
    ],
    templateUrl: './my-recipes.component.html',
    styleUrls: ['./my-recipes.component.css']
})
export class MyRecipesComponent {
    private dialog = inject(MatDialog);
    private http = inject(HttpClient);
    private router = inject(Router);
    private toast = inject(HotToastService);
    private usersService = inject(UsersService);


    // Once we can upload files to these buckets, we can use these functions to get the URLs.
    // getIngredientsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
    // }

    // getInstructionsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
    // }


    // stream of recipes for the template
    recipes$ = new BehaviorSubject<Recipe[]>([]);
    // show/hide content to avoid flicker if user isn’t logged in
    authorized$ = new BehaviorSubject<boolean>(false);


    trackById = (_: number, r: Recipe) => r.id;

    ngOnInit() {
        this.usersService.loadCachedUserProfile();
        this.usersService.profile$.subscribe(() => { /* use if needed */ });

        const uid = localStorage.getItem('uid');
        if (!uid) {
            this.toast.warning('Please log in to continue.');
            this.authorized$.next(false);
            // In case we want to navigate elsewhere -- dashboard exhibits behaviour where you can still access the dashboard
            this.router.navigate(['/']);
            return;
        }

        this.authorized$.next(true);
        this.fetchRecipes();

        // const url = `${environment.baseUrl}/api/recipes?user_id=${encodeURIComponent(uid)}`;

        // this.http.get<any[]>(url).subscribe({
        //     next: (rows) => {
        //         // Map API rows to your Recipe interface
        //         const mapped: Recipe[] = rows.map(r => ({
        //             id: String(r.id ?? r.number ?? r.title),
        //             title: r.title,
        //             ingredients: r.ingredients ?? [],  
        //             instructions: r.instructions ?? []
        //         }));
        //         saveRecipes(mapped);       // cache locally
        //         this.recipes$.next(mapped);
        //     },
        //     error: (err) => {
        //         console.error('Failed to fetch recipes from API, using seed data', err);
        //         const existing = loadRecipes();
        //         if (existing.length) {
        //             this.recipes$.next(existing);
        //             return;
        //         }
        //         // seed for first-time run if API fails
        //         // leave in for now, just in case updated table does not work correctly
        //         const seed: Recipe[] = [
        //             {
        //                 id: this.newId(),
        //                 title: 'My Grilled Chicken Sandwich',
        //                 ingredients: [
        //                     { name: 'Chicken breasts', amount: 0.5, unit: 'lb' },
        //                     { name: 'Bread', amount: 2, unit: 'slices', note: 'toasted' },
        //                     { name: 'Butter', amount: 2, unit: 'tbsp' },
        //                     { name: 'Salt', note: 'to taste' }
        //                 ],
        //                 instructions: [
        //                     'Cook chicken and cut into slices',
        //                     'Toast bread then butter',
        //                     'Place chicken on bread and sprinkle salt'
        //                 ]
        //             }
        //         ];
        //         saveRecipes(seed);
        //         this.recipes$.next(seed);
        //     }
        // });
    }

    /**
 * GET recipes for the current user and map to UI model.
 * Reused on load and after server-side imports/creates.
 */
    fetchRecipes() {
        const uid = localStorage.getItem('uid');
        if (!uid) return;

        const url = `${environment.baseUrl}/api/recipes?user_id=${encodeURIComponent(uid)}`;

        this.http.get<any[]>(url).subscribe({
            next: (rows) => {
                const mapped: Recipe[] = rows.map(r => ({
                    id: String(r.id ?? r.number ?? r.title),
                    title: r.title,
                    // placeholders returned by API ensure these exist
                    ingredients: r.ingredients ?? [],
                    instructions: r.instructions ?? []
                }));
                saveRecipes(mapped);       // cache locally
                this.recipes$.next(mapped);
            },
            error: (err) => {
                console.error('Failed to fetch recipes from API, using seed data', err);
                const existing = loadRecipes();
                if (existing.length) {
                    this.recipes$.next(existing);
                    return;
                }
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
        // send to questionnaire instead
        // const ref = this.dialog.open(EditRecipeDialogComponent, {
        //     width: '720px',
        //     data: {
        //         mode: 'create',
        //         recipe: {
        //             id: this.newId(),
        //             title: 'Untitled Recipe',
        //             ingredients: [],
        //             instructions: []
        //         }
        //     } as EditRecipeData
        // });
        // ref.afterClosed().subscribe((result?: Recipe) => {
        //     if (!result) return;
        //     const next = [...this.recipes$.value, result];
        //     saveRecipes(next);
        //     this.recipes$.next(next);
        // });



        
        // window.location.href = environment.addRecipeQuestionnaire
        const uid = localStorage.getItem('uid');
        window.location.href = `http://localhost:4201?uid=${uid}`;
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
        // Update with query to db so as to delete custom recipe from db as well
        if (!confirm(`Delete "${recipe.title}"?`)) return;
        const next = this.recipes$.value.filter(r => r.id !== recipe.id);
        saveRecipes(next);
        this.recipes$.next(next);
    }

    /**
   * NEW: Ask the backend to import a CSV that already lives on the server,
   * then refresh the list. Defaults to 'example.csv' but you can pass another name.
   *
   * Requires Flask route: POST /api/recipes/import/:user_id  body: { filename }
   */
    importFromServerCsv(filename = 'example.csv') {
        const uid = localStorage.getItem('uid');
        if (!uid) { this.toast.warning('Please log in'); return; }

        if (this._busy) return;
        this._busy = true;

        const url = `${environment.baseUrl}/api/recipes/import/${encodeURIComponent(uid)}`;
        this.http.post<{ ok: boolean; mode?: 'update' | 'skip'; skipped?: boolean; user_id?: string; number?: number; error?: string }>(
            url,
            { filename, mode: 'update' },
            { headers: { 'Content-Type': 'application/json' } }
        ).subscribe({
            next: (res) => {
                if (res?.ok && res?.skipped) {
                    this.toast.info(`Skipped: recipe #${res.number} already exists for this user.`);
                } else if (res?.ok) {
                    this.toast.success(`Imported recipe #${res.number}.`);
                } else {
                    this.toast.warning(res?.error || 'Import completed with warnings');
                }
                this.fetchRecipes();
            },
            error: (err) => {
                const msg = err?.error?.error || err?.message || 'Import failed';
                this.toast.error(msg);
                console.error('import failed', err);
            },
            complete: () => { this._busy = false; }
        });
    }

    // add this field in your class:
    private _busy = false;



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
