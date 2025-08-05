import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { ShoppingListLandingPageComponent } from '../dialogues/shopping-list-landing-page/shopping-list-landing-page.component';
import { startDate } from '../landing/form-values';
import { RecipeDialogComponent } from '../dialogues/recipe/recipe.component';
import { SearchDialogComponent } from '../search-dialog/search-dialog.component';
import {sampleMealPlanData } from '../../moc/sampleMealPlan';
import { ShoppingList } from '../dialogues/shopping-list-landing-page/shopping-list-landing-page.interface';

@Component({
  selector: 'app-meal-plan',
  templateUrl: './meal-plan.component.html',
  styleUrls: ['./meal-plan.component.css'],
})
export class MealPlanComponent implements OnInit {
  mealPlanResponse: any = {};
  shoppingListData: any[] = [];
  energy: any[] = [];
  macros: any[] = [];
  vitamins: any[] = [];
  minerals: any[] = [];
  expanded: boolean = false;
  displayedColumns: string[] = ['nutrientName', 'target', 'actual'];
  start_date: any;
  end_date: any;
  nutrientSections: Record<string, any[]> = {};

  constructor(
    private route: ActivatedRoute,
    private toast: HotToastService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    // take Query from
    this.route.queryParams.subscribe((params) => {
      this.start_date = params['start_date'] || null;
      this.end_date = params['end_date'] || null;
    });

    this.mealPlanResponse = sampleMealPlanData

    this.shoppingListData = this.transformMealPlanToShoppingList(
                this.mealPlanResponse
              );

    this.categorizeNutrients()

    // change The order of meals: should be Breakfast, Snack, Lunch, Snack, Dinner, Snack
    this.mealPlanResponse.days.forEach(
      (day: { recipes: { meal_name: string }[] }) => {
        day.recipes.sort(
          (a: { meal_name: string }, b: { meal_name: string }) => {
            const mealOrder = [
              'Breakfast',
              'Snack',
              'Lunch',
              'Snack',
              'Dinner',
              'Snack',
            ];
            return (
              mealOrder.indexOf(a.meal_name) - mealOrder.indexOf(b.meal_name)
            );
          }
        );
      }
    );

    
    
  }

    transformMealPlanToShoppingList(mealPlan: any): ShoppingList[] {
      if (!mealPlan || !mealPlan.days || !Array.isArray(mealPlan.days)) {
        console.error(
          'Invalid mealPlanResponse structure for shopping list generation:',
          mealPlan
        );
        this.toast.error(
          'Could not generate shopping list: Invalid meal plan data.'
        );
        return [];
      }
  
      const shoppingListByDate: ShoppingList[] = [];
  
      mealPlan.days.forEach((day: any) => {
        if (!day.date || !day.recipes || !Array.isArray(day.recipes)) {
          console.warn(
            'Skipping day in shopping list due to missing date or recipes:',
            day
          );
          return; // Skip this day if data is malformed
        }
  
        const dailyItems: { name: string; quantity: string; unit: string }[] = [];
  
        day.recipes.forEach((recipe: any) => {
          if (
            !recipe.ingredients_with_quantities ||
            !Array.isArray(recipe.ingredients_with_quantities)
          ) {
            console.warn(
              'Skipping recipe in shopping list due to missing ingredients_with_quantities:',
              recipe
            );
            return; // Skip this recipe
          }
  
          // Start from index 1 to skip the header row like ['Ingredient Name', 'Quantity', ...]
          for (let i = 1; i < recipe.ingredients_with_quantities.length; i++) {
            const ingredientData = recipe.ingredients_with_quantities[i];
  
            if (Array.isArray(ingredientData) && ingredientData.length >= 3) {
              const name = ingredientData[0]
                ? String(ingredientData[0]).trim()
                : 'Unknown Item';
              const quantity = ingredientData[1]
                ? String(ingredientData[1]).trim()
                : 'N/A';
              const unit = ingredientData[2]
                ? String(ingredientData[2]).trim()
                : ''; // Unit can be empty
  
              // Ensure we are not accidentally picking up a header if it's malformed
              if (name && name.toLowerCase() !== 'ingredient name') {
                dailyItems.push({ name, quantity, unit });
              }
            } else {
              console.warn(
                'Skipping malformed ingredient data in shopping list:',
                ingredientData
              );
            }
          }
        });
  
        if (dailyItems.length > 0) {
          shoppingListByDate.push({
            date: day.date,
            'shopping-list': dailyItems,
          });
        }
      });
      console.log('Generated Shopping List Data:', shoppingListByDate);
      return shoppingListByDate;
    }


  openShoppingListDialog(): void {
    if (!this.shoppingListData || this.shoppingListData.length === 0) {
      this.toast.info(
        'Shopping list is empty or not yet loaded. Please generate a meal plan first.'
      );
    }
    const dialogConfig = new MatDialogConfig();
    dialogConfig.width = '500px'; // Set the width of the dialog
    dialogConfig.data = {
      shoppingListData: this.shoppingListData,
      minDate: localStorage.getItem('minDate'),
      maxDate: localStorage.getItem('maxDate'),
    };
    dialogConfig.autoFocus = false; // Disable auto-focus
    const dialogRef = this.dialog.open(
      ShoppingListLandingPageComponent,
      dialogConfig
    );

    dialogRef.afterOpened().subscribe(() => {
      const dialogContent = document.querySelector('.popup-max-height');
      if (dialogContent) {
        dialogContent.scrollTop = 0;
      }
    });
  }

  formatDate(date: string): string {
    const [year, month, day] = date.split('-').map(Number);
    const localDate = new Date(year, month - 1, day);
    // console.log('Original Date:', date);
    // console.log('Local Date (Corrected):', localDate.toLocaleString());

    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return localDate.toLocaleDateString('en-US', options);
  }

  getDayOfWeek(date: string): string {
    const days = [
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
      'Sunday',
    ];
    const localDate = new Date(date);
    return days[localDate.getDay()];
  }
  readonly defaultImgPath =
    '../../../assets/images/meal-plan-images/default_meal_picture.png';
  readonly startDate = startDate;

  getImageUrl(id: number): string {
    const path = `https://storage.googleapis.com/mealplaniq-may-2024-recipe-images/${id}.jpg`;
    //const path = `../../../assets/images/meal-plan-images/default_meal_picture.png`;

    // check if the image exists
    const img = new Image();
    img.src = path;
    if (img.complete) {
      return path;
    } else {
      return this.defaultImgPath;
    }
  }

  openRecipeDialog(recipe: any): void {
    const data = {
      minDate: new Date(this.start_date!).getTime(),
      maxDate: new Date(this.end_date!).getTime(),
    };

    // if (
    //   this.userSubscriptionTypeId === 1 ||
    //   this.userSubscriptionTypeId === 2 ||
    //   this.userSubscriptionTypeId === 3
    // ) {
    this.dialog.open(RecipeDialogComponent, {
      data: {
        recipe: recipe,
        imageUrl: this.getImageUrl(recipe.id),
        ingredientsUrl: this.getIngredientsCsvUrl(recipe.id), // Added URL for ingredients CSV, @author BCIT May 2025
        instructionsUrl: this.getInstructionsCsvUrl(recipe.id), // Added URL for instructions CSV, @author BCIT May 2025
        showActions: false,
      },
      width: '800px',
    });
  }

  categorizeNutrients() {
    this.energy = []; // add new "Energy" category
    this.macros = [];
    this.vitamins = [];
    this.minerals = [];

    // define nutrient aliases
    const nutrientAliases: { [key: string]: string } = {
      'thiamin (mg)': 'Vitamin B1 / Thiamine (mg)',
      'riboflavin (mg)': 'Vitamin B2 / Riboflavin (mg)',
      'niacin (mg)': 'Vitamin B3 / Niacin (mg)',
      'vitamin_b5 (mg)': 'Vitamin B5 / Pantothenic Acid (mg)',
      'vitamin_b6 (mg)': 'Vitamin B6 / Pyridoxine (mg)',
      'vitamin_b12 (ug)': 'Vitamin B12 / cyanocobalamin (ug)',
      'folate (ug)': 'Vitamin B9 / Folate (ug)',
      'vitamin_a (iu)': 'Vitamin A (iu)',
      'vitamin_c (mg)': 'Vitamin C (mg)',
      'vitamin_d (iu)': 'Vitamin D (iu)',
      'vitamin_e (mg)': 'Vitamin E (mg)',
      'vitamin_k (ug)': 'Vitamin K (ug)',
    };

    this.mealPlanResponse.tableData.forEach((nutrient: any) => {
      const nutrientName = nutrient.nutrientName.toLowerCase();
      // replace nutrient name with alias if it exists

      if (nutrientAliases[nutrientName]) {
        nutrient.displayName = nutrientAliases[nutrientName];
      } else {
        // use the original name if no alias is found
        nutrient.displayName = nutrient.nutrientName;
      }

      nutrient.displayName = nutrient.displayName.replace(
        /\((.*?)\)/g,
        (match: any, p1: any) => `(${p1.toLowerCase()})`
      );

      nutrient.displayName = nutrient.displayName
        .split(' ')
        .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      // console.log('1234:', nutrient.displayName);

      // Parse display_target as range
      if (
        typeof nutrient.display_target === 'string' &&
        nutrient.display_target.includes('-')
      ) {
        const [min, max] = nutrient.display_target
          .split('-')
          .map((val: string) => parseFloat(val.trim()));
        nutrient.display_target_min = min;
        nutrient.display_target_max = max;
      } else {
        const target = parseFloat(nutrient.display_target);
        nutrient.display_target_min = target;
        nutrient.display_target_max = target;

        if (nutrient.actualValue < target) {
          nutrient.display_target_max = target;
          nutrient.display_target_min = null;
        } else {
          nutrient.display_target_min = target;
          nutrient.display_target_max = null;
        }
      }

      if (nutrientName === 'energy (calories)') {
        this.energy.push(nutrient);
      } else if (
        ['fiber (g)', 'carbohydrates (g)', 'protein (g)', 'fats (g)'].includes(
          nutrientName
        )
      ) {
        this.macros.push(nutrient);
      } else if (Object.keys(nutrientAliases).includes(nutrientName)) {
        nutrient.displayName = nutrientAliases[nutrientName];
        this.vitamins.push(nutrient);
      } else {
        nutrient.displayName = nutrient.nutrientName;
        this.minerals.push(nutrient);
      }
      nutrient.displayName = nutrient.displayName
        .split(' ')
        .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      // console.log('1234:', nutrient.displayName);
    });
    // sort minerals and vitamins
    this.minerals.sort((a, b) => a.displayName.localeCompare(b.displayName));
    this.vitamins.sort((a, b) => {
      const extractVitaminInfo = (name: string) => {
        const match = name.match(/vitamin\s*(\D*)(\d*)/i);
        if (match) {
          const letterPart = match[1].toUpperCase();
          const numberPart = match[2] ? parseInt(match[2], 10) : 0;
          return { letterPart, numberPart };
        }
        return { letterPart: name, numberPart: 0 };
      };

      const aInfo = extractVitaminInfo(a.displayName);
      const bInfo = extractVitaminInfo(b.displayName);

      // sort by letterPart first, then by numberPart
      if (aInfo.letterPart === bInfo.letterPart) {
        return aInfo.numberPart - bInfo.numberPart;
      }
      return aInfo.letterPart.localeCompare(bInfo.letterPart);
    });
  }


  getIngredientsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
  }

  getInstructionsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
  }
}

