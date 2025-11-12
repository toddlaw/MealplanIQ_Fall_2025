import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import type { Recipe, Ingredient } from './my-recipes.component';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export type Mode = 'create' | 'edit';
export interface EditRecipeData {
  mode: Mode;
  recipe: Recipe;
}

@Component({
  selector: 'app-edit-recipe-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule
  ],
  template: `
    <h2 mat-dialog-title>{{ data.mode === 'create' ? 'Add Recipe' : 'Edit Recipe' }}</h2>
    <div mat-dialog-content class="content">
      <mat-form-field appearance="fill" class="full">
        <mat-label>Title</mat-label>
        <input matInput [(ngModel)]="model.title" />
      </mat-form-field>

      <h3>Ingredients</h3>
      <div class="ing-row" *ngFor="let ing of model.ingredients; let i = index; trackBy: trackByIndex">
        <mat-form-field appearance="fill"><mat-label>Name</mat-label>
          <input matInput [(ngModel)]="ing.name" />
        </mat-form-field>
        <mat-form-field appearance="fill"><mat-label>Amount</mat-label>
          <input matInput type="number" [(ngModel)]="ing.amount" />
        </mat-form-field>
        <mat-form-field appearance="fill"><mat-label>Unit</mat-label>
          <input matInput [(ngModel)]="ing.unit" />
        </mat-form-field>
        <mat-form-field appearance="fill"><mat-label>Note</mat-label>
          <input matInput [(ngModel)]="ing.note" />
        </mat-form-field>
        <button mat-icon-button color="warn" (click)="removeIngredient(i)">
          <mat-icon>close</mat-icon>
        </button>
      </div>
      <button mat-stroked-button (click)="addIngredient()">
        <mat-icon>add</mat-icon> Add Ingredient
      </button>

      <h3>Instructions</h3>
      <div class="step-row" *ngFor="let step of model.instructions; let i = index; trackBy: trackByIndex">
        <span class="idx">{{ i + 1 }}</span>
        <mat-form-field appearance="fill" class="full">
          <mat-label>Step {{ i + 1 }}</mat-label>
          <input matInput [(ngModel)]="model.instructions[i]" />
        </mat-form-field>
        <button mat-icon-button color="warn" (click)="removeStep(i)">
          <mat-icon>close</mat-icon>
        </button>
      </div>
      <button mat-stroked-button (click)="addStep()">
        <mat-icon>add</mat-icon> Add Step
      </button>
    </div>

    <div mat-dialog-actions align="end">
      <button mat-button (click)="close()">Cancel</button>
      <button mat-raised-button color="primary" (click)="save()">Save</button>
    </div>
  `,
  styles: [`
    .content { display: grid; gap: 12px; }
    .full { width: 100%; }
    .ing-row, .step-row {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr auto;
      gap: 8px;
      align-items: center;
    }
    .step-row { grid-template-columns: auto 1fr auto; }
    .idx { width: 24px; text-align: right; margin-right: 8px; opacity: .7; }
    h3 { margin: 8px 0 0; }
  `]
})
export class EditRecipeDialogComponent implements OnInit {   // <-- implement OnInit
  model: Recipe;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: EditRecipeData,
    private ref: MatDialogRef<EditRecipeDialogComponent>,
    private http: HttpClient,
  ) {
    // start with what you already had (title from DB)
    this.model = {
      id: data.recipe.id,
      title: data.recipe.title,
      ingredients: (data.recipe.ingredients || []).map(x => ({ ...x })),
      instructions: [...(data.recipe.instructions || [])],
    };
  }

  ngOnInit(): void {
    const uid = localStorage.getItem('uid');
    const num = Number(this.model.id);
    if (!uid || !Number.isFinite(num)) return;

    const url = `${environment.baseUrl}/api/recipes/${encodeURIComponent(uid)}/${num}/files`;
    this.http.get<{ ingredients: Ingredient[]; instructions: string[] }>(url)
      .subscribe({
        next: (res) => {
          if (Array.isArray(res.ingredients)) this.model.ingredients = res.ingredients;
          if (Array.isArray(res.instructions)) this.model.instructions = res.instructions;
        },
        error: (err) => console.error('load CSV files failed', err)
      });
  }

  trackByIndex(index: number, _item: any) {
    return index;
  }


  addIngredient() { (this.model.ingredients as Ingredient[]).push({ name: '' }); }
  removeIngredient(i: number) { this.model.ingredients.splice(i, 1); }

  addStep() { this.model.instructions.push(''); }
  removeStep(i: number) { this.model.instructions.splice(i, 1); }

  close() { this.ref.close(); }

  save() {
    const uid = localStorage.getItem('uid');
    const num = Number(this.model.id);
    if (!uid || !Number.isFinite(num)) { this.ref.close(this.model); return; }

    const url = `${environment.baseUrl}/api/recipes/${encodeURIComponent(uid)}/${num}/files`;
    const body = { ingredients: this.model.ingredients, instructions: this.model.instructions };

    this.http.put(url, body).subscribe({
      next: () => this.ref.close(this.model),
      error: (err) => { console.error('save CSV files failed', err); this.ref.close(this.model); }
    });
  }
}