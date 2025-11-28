/**
 * MyRecipesComponent
 *
 * This standalone Angular component displays and manages the current user's
 * custom recipes. It:
 *  - Checks if the user is logged in (by presence of uid in localStorage)
 *  - Fetches recipes from the backend Flask API
 *  - Caches recipes in localStorage as a fallback
 *  - Allows editing and deleting recipes locally
 *  - Can trigger an import of recipes from a server-side CSV
 */

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

/**
 * Ingredient model for a recipe.
 * - name: Required display name of the ingredient.
 * - amount: Optional numeric quantity (e.g., 2).
 * - unit: Optional unit for quantity (e.g., "tbsp", "g").
 * - note: Optional free-form note (e.g., "to taste", "minced").
 */
export interface Ingredient {
    name: string;
    amount?: number;
    unit?: string;
    note?: string;
}

/**
 * Recipe model used by the component and template.
 * - id: String identifier used for tracking, editing, and deleting.
 * - title: Recipe name.
 * - ingredients: List of ingredient objects.
 * - instructions: Ordered list of instruction steps.
 */
export interface Recipe {
    id: string;
    title: string;
    ingredients: Ingredient[];
    instructions: string[];
}

/**
 * Key used to persist recipes in localStorage as a fallback.
 */
const STORAGE_KEY = 'demo_recipes';

/**
 * Load recipes from localStorage cache.
 *
 * Returns an empty array on:
 *  - missing key
 *  - JSON parse error
 */
function loadRecipes(): Recipe[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch { return []; }
}

/**
 * Save recipes to localStorage cache.
 *
 * @param recipes - Array of Recipe objects to serialize and store.
 */
function saveRecipes(recipes: Recipe[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(recipes));
}

/**
 * Simple deep clone using JSON serialization.
 *
 * NOTE: Only safe for plain data objects (no functions, Dates, etc.).
 *
 * @param x - Value to clone (typically Recipe or Ingredient objects).
 */
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
    /**
     * Angular Material dialog service for opening edit dialogs.
     */
    private dialog = inject(MatDialog);

    /**
     * HttpClient for calling backend APIs.
     */
    private http = inject(HttpClient);

    /**
     * Router for navigation (e.g., redirecting unauthenticated users).
     */
    private router = inject(Router);

    /**
     * Toast service for user feedback (success/error/info messages).
     */
    private toast = inject(HotToastService);

    /**
     * UsersService for loading and observing the current user's profile.
     */
    private usersService = inject(UsersService);

    /**
    * Flag to prevent concurrent import operations.
    * - true: an import is currently in progress.
    * - false: no import is active.
    */
    private _busy = false;


    // Once we can upload files to these buckets, we can use these functions to get the URLs.
    // getIngredientsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
    // }

    // getInstructionsCsvUrl(id: number): string {
    //     return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
    // }


    /**
     * Reactive stream of recipes for the template.
     *
     * The template can subscribe via | async to render the list of recipes.
     */
    recipes$ = new BehaviorSubject<Recipe[]>([]);

    /**
     * Controls whether the content should be shown or hidden.
     *
     * This helps avoid flicker while we determine if the user is logged in,
     * and can also be used to gate the page to authenticated users only.
     */
    authorized$ = new BehaviorSubject<boolean>(false);

    /**
     * trackBy function for *ngFor to improve performance and avoid DOM churn.
     * Uses the recipe's id as the unique key.
     */
    trackById = (_: number, r: Recipe) => r.id;

    /**
     * Lifecycle hook: runs once when the component is initialized.
     *
     * - Loads any cached user profile.
     * - Subscribes to profile$ in case you want future reactive behavior.
     * - Checks for uid in localStorage to determine if user is logged in.
     * - If not logged in: shows a warning and navigates to home.
     * - If logged in: marks authorized and fetches recipes from the backend.
     */
    ngOnInit() {
        // Load cached profile data (if any) so user info is available quickly.
        this.usersService.loadCachedUserProfile();

        // You can later use this subscription to react to profile changes.
        this.usersService.profile$.subscribe(() => { /* use if needed */ });

        // Minimal auth check: we consider presence of uid as "logged in".
        const uid = localStorage.getItem('uid');
        if (!uid) {
            this.toast.warning('Please log in to continue.');
            this.authorized$.next(false);
            // In case we want to navigate elsewhere -- dashboard exhibits behaviour where you can still access the dashboard
            this.router.navigate(['/']);
            return;
        }

        // User has a UID, so consider them authorized and fetch data.
        this.authorized$.next(true);
        this.fetchRecipes();
    }

    /**
     * GET recipes for the current user and map to UI model.
     * Reused on load and after server-side imports/creates.
     *
     * Behavior:
     *  - If uid is missing: silently return.
     *  - Call GET /api/recipes?user_id=...
     *  - Map backend rows -> Recipe objects.
     *  - Cache successful results in localStorage.
     *  - On error:
     *      - If cached recipes exist: use them.
     *      - Otherwise seed with a single example recipe, then cache.
     */
    fetchRecipes() {
        const uid = localStorage.getItem('uid');
        if (!uid) return;

        // Build API endpoint for fetching recipes for the current user.
        const url = `${environment.baseUrl}/api/recipes?user_id=${encodeURIComponent(uid)}`;

        this.http.get<any[]>(url).subscribe({
            next: (rows) => {
                // Map backend rows to our internal Recipe model.
                const mapped: Recipe[] = rows.map(r => ({
                    // Fallback ID logic: prefer r.id, then r.number, then r.title.
                    id: String(r.id ?? r.number ?? r.title),
                    title: r.title,
                    // placeholders returned by API ensure these exist
                    ingredients: r.ingredients ?? [],
                    instructions: r.instructions ?? []
                }));
                // Persist to localStorage as a cache.
                saveRecipes(mapped);
                // Emit to subscribers (template updates via async pipe).
                this.recipes$.next(mapped);
            },
            error: (err) => {
                console.error('Failed to fetch recipes from API, using seed data', err);

                // 1) Try to use any locally cached recipes.
                const existing = loadRecipes();
                if (existing.length) {
                    this.recipes$.next(existing);
                    return;
                }

                // 2) If nothing is cached, seed with a sample recipe.
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
                // Cache the seed recipe so future loads can use it.
                saveRecipes(seed);
                this.recipes$.next(seed);
            }
        });
    }

    /**
     * Navigate to the external custom recipe builder UI.
     *
     * This opens a new/other app (on port 4201) and passes the current uid
     * as a query parameter so the external app can associate new recipes
     * with the same user.
     */
    addNew() {
        const uid = localStorage.getItem('uid');
        // Direct full-page navigation rather than router navigation
        // because this is likely a separate Angular app.
        window.location.href = `http://localhost:4201?uid=${uid}`;
    }

    /**
     * Open the EditRecipeDialogComponent to edit a specific recipe.
     *
     * @param recipe - The recipe to edit; will be deep-cloned before passing
     *                 to the dialog so the original is not mutated directly.
     *
     * After the dialog closes with an updated recipe:
     *  - Replace the matching recipe in recipes$.
     *  - Persist the new list to localStorage.
     */
    edit(recipe: Recipe) {
        const ref = this.dialog.open(EditRecipeDialogComponent, {
            width: '720px',
            data: { mode: 'edit', recipe: deepClone(recipe) } as EditRecipeData
        });

        ref.afterClosed().subscribe((updated?: Recipe) => {
            // If user cancelled the dialog or closed without saving, do nothing.
            if (!updated) return;

            // Replace the original recipe with the updated one.
            const next = this.recipes$.value.map(r => r.id === updated.id ? updated : r);
            saveRecipes(next);
            this.recipes$.next(next);
        });
    }

    /**
     * Delete a recipe from the in-memory and cached list.
     *
     * NOTE: Currently this only updates the local BehaviorSubject and
     *       localStorage cache. The comment indicates that this should be
     *       updated to also delete from the database via an API call.
     *
     * @param recipe - The recipe to delete.
     */
    delete(recipe: Recipe) {
        // Update with query to db so as to delete custom recipe from db as well
        if (!confirm(`Delete "${recipe.title}"?`)) return;

        // Filter out the deleted recipe.
        const next = this.recipes$.value.filter(r => r.id !== recipe.id);
        saveRecipes(next);
        this.recipes$.next(next);
    }

    /**
     * Ask the backend to import a CSV that already lives on the server,
     * then refresh the list. Defaults to 'example.csv' but you can pass another name.
     *
     * Expected backend endpoint:
     *   POST /api/recipes/import/:user_id
     *   body: { filename, mode }
     *
     * The response is expected to be of the form:
     *   { ok: boolean; mode?: 'update' | 'skip'; skipped?: boolean;
     *     user_id?: string; number?: number; error?: string }
     *
     * Behavior:
     *  - Requires a logged-in user (uid in localStorage).
     *  - Uses this._busy to avoid overlapping imports.
     *  - Shows appropriate toast messages based on response.
     *  - Always calls fetchRecipes() on success to refresh the list.
     *
     * @param filename - Name of CSV file on the server to import (default: 'example.csv').
     */
    importFromServerCsv(filename = 'example.csv') {
        const uid = localStorage.getItem('uid');
        if (!uid) { this.toast.warning('Please log in'); return; }

        // Prevent concurrent imports from being triggered.
        if (this._busy) return;
        this._busy = true;

        const url = `${environment.baseUrl}/api/recipes/import/${encodeURIComponent(uid)}`;

        this.http.post<{ ok: boolean; mode?: 'update' | 'skip'; skipped?: boolean; user_id?: string; number?: number; error?: string }>(
            url,
            { filename, mode: 'update' },
            { headers: { 'Content-Type': 'application/json' } }
        ).subscribe({
            next: (res) => {
                // Interpret the response and show user feedback.
                if (res?.ok && res?.skipped) {
                    // Case: Existing recipe detected and skipped.
                    this.toast.info(`Skipped: recipe #${res.number} already exists for this user.`);
                } else if (res?.ok) {
                    // Case: Successful import.
                    this.toast.success(`Imported recipe #${res.number}.`);
                } else {
                    // Case: Non-ok response, but no transport-level error.
                    this.toast.warning(res?.error || 'Import completed with warnings');
                }
                // In all success-ish cases, refresh the recipe list.
                this.fetchRecipes();
            },
            error: (err) => {
                // Handle network or server errors.
                const msg = err?.error?.error || err?.message || 'Import failed';
                this.toast.error(msg);
                console.error('import failed', err);
            },
            complete: () => { this._busy = false; }
        });
    }

    /**
     * Utility to generate a new unique ID string for client-side recipes.
     *
     * Uses crypto.randomUUID when available, otherwise falls back to
     * a Math.random-based ID. This is primarily used for seed/fallback data
     * and may not match the server's primary key scheme.
     */
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
