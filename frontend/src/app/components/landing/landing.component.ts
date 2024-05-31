import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { FormControl, FormGroup, NgForm } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatExpansionPanel } from '@angular/material/expansion';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { RecipeDialogComponent } from '../dialogues/recipe/recipe.component';
import { RefreshComponent } from 'src/app/services/refresh/refresh.component';
import {
  units,
  activityLevels,
  genders,
  vegetarians,
  healthGoals,
  religiousConstraints,
  likedFoodsList,
  dislikedFoodsList,
  cuisinesList,
  allergiesList,
  startDate,
  endDate,
  breakfastList,
  snackList,
} from './form-values';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialogModule,
  MatDialogConfig,
} from '@angular/material/dialog';
import { TermsAndConditionsComponent } from '../dialogues/tac-dialog/tac-dialog.component';
import { GeneratePopUpComponent } from '../dialogues/generate-pop-up/generate-pop-up.component';
import { ShoppingListLandingPageComponent } from '../dialogues/shopping-list-landing-page/shopping-list-landing-page.component';
import { ShoppingList } from '../dialogues/shopping-list-landing-page/shopping-list-landing-page.interface';

@Component({
  selector: 'app-landing',
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css'],
})
export class LandingComponent implements OnInit {
  constructor(
    private http: HttpClient,
    private dialog: MatDialog,
    private router: Router,
    private toast: HotToastService,
    private refresh: RefreshComponent
  ) {}

  readonly MIN_PEOPLE = 1;
  readonly MAX_PEOPLE = 6;
  readonly TAC_KEY = 'acceptedTac';
  readonly defaultImgPath =
    '../../../assets/images/meal-plan-images/default_meal_picture.png';
  readonly OUT_OF_RANGE =
    'This meal plan has some nutrients which are out of the target range.   Please see the table at the bottom for details.';
  readonly NO_RECIPES =
    "We're sorry!  We could not find a meal plan that fits your constraints.";

  @ViewChild('peoplePanel') peoplePanel!: MatExpansionPanel;
  @ViewChild('peopleForm') peopleForm!: NgForm;
  @ViewChild('scrollToMe') element!: ElementRef;
  @ViewChild('start') start!: ElementRef;
  @ViewChild('errorDiv') errorDiv!: ElementRef;

  mealPlanResponse: any = {};
  numRecipes: number = 0;
  numDays: number = 0;
  showSpinner: boolean = false;
  panelOpenState: boolean = true;
  minDate: Date = new Date();
  maxDate: Date = new Date();
  numOfPeople: number = this.MIN_PEOPLE;
  receivedData: string = '';
  recipe: any[] = [];
  bmiValue: number = 0;
  tdeeValue: number = 0;
  selectedOption: string = 'keep';
  recipesFetched = false;
  includedRecipes: number[] = [];
  excludedRecipes: number[] = [];
  selectedOptions: string[][] = [];
  searchClicked: boolean = false;
  selectedHealthGoalIndex: number = 3;
  userSubscriptionTypeId: number = 0;
  updatedMealPlan: any;
  shoppingListData: ShoppingList[] = [];

  people: {
    age: number | null;
    weight: number | null;
    height: number | null;
    gender: string | null;
    activityLevel: string | null;
  }[] = Array.from({ length: this.MIN_PEOPLE }, () => ({
    age: null,
    weight: null,
    height: null,
    gender: null,
    activityLevel: null,
  }));

  readonly displayedColumns: string[] = ['nutrientName', 'target', 'actual'];
  readonly mealNames: string[] = ['Breakfast', 'Lunch', 'Dinner'];

  // Form content
  readonly units = units;
  readonly activityLevels = activityLevels;
  readonly genders = genders;
  readonly vegetarians = vegetarians;
  readonly healthGoals = healthGoals;
  readonly religiousConstraints = religiousConstraints;
  readonly likedFoodsList = likedFoodsList;
  readonly dislikedFoodsList = dislikedFoodsList;
  readonly cuisinesList = cuisinesList;
  readonly allergiesList = allergiesList;
  readonly startDate = startDate;
  readonly endDate = endDate;
  readonly breakfastList = breakfastList;
  readonly snackList = snackList;

  selectedUnit: string = 'metric';
  selectedDietaryConstraint: string = vegetarians[0].value;
  selectedHealthGoal: string = healthGoals[3].value; // Initialize to make the fourth item active by default
  selectedReligiousConstraint: string = religiousConstraints[0].value;
  likedFoods = new FormControl('');
  dislikedFoods = new FormControl('');
  cuisines = new FormControl('');
  allergies = new FormControl('');
  breakfasts = new FormControl('');
  snacks = new FormControl('');
  expandedStates: boolean[][] = [];
  snackExpandedStates: boolean[] = [];

  async ngOnInit() {
    console.log('user ID: ' + localStorage.getItem('uid'));
    console.log('email: ' + localStorage.getItem('email'));

    if (localStorage.getItem('uid')) {
      try {
        const response: any = await this.http
          .get(
            'http://127.0.0.1:5000/api/subscription_type_id/' +
              localStorage.getItem('uid')
          )
          .toPromise();
        if (response.subscription_type_id) {
          localStorage.setItem(
            'subscription_type_id',
            response.subscription_type_id
          ); // 1: monthly, 2: yearly, 3: free-trial for signed up user
          this.userSubscriptionTypeId = response.subscription_type_id;
        }
      } catch (error) {
        console.error('Error:', error);
      }
    } else {
      this.userSubscriptionTypeId = 0;
    }
    console.log('subscription type ID:' + this.userSubscriptionTypeId);
    // prefill the profile info for logged in user
    if (localStorage.getItem('uid')) {
      this.http
        .get(
          'http://127.0.0.1:5000/api/landing/profile/' +
            localStorage.getItem('uid')
        )
        .subscribe((data: any) => {
          this.people[0].age = data.age;
          this.people[0].weight = data.weight;
          this.people[0].height = data.height;
          this.people[0].gender = data.gender;
          this.people[0].activityLevel = data.activity_level;
          this.selectedUnit = data.selected_unit || 'metric';
        });
    }
  }

  /**
   * Shows the terms and conditions dialog and sends the data if the terms and conditions are accepted
   */
  showTermsAndConditions() {
    // make sure the form is valid
    if (this.peopleForm.invalid) {
      return;
    }

    if (localStorage.getItem(this.TAC_KEY) === 'true') {
      this.sendData();
    } else if (
      !localStorage.getItem(this.TAC_KEY) ||
      localStorage.getItem(this.TAC_KEY) === 'false'
    ) {
      const dialogRef = this.dialog.open(TermsAndConditionsComponent, {
        width: '1000px',
      });

      dialogRef.afterClosed().subscribe((accepted) => {
        if (accepted) {
          localStorage.setItem(this.TAC_KEY, 'true');
          this.sendData();
        } else {
          localStorage.setItem(this.TAC_KEY, 'false');
        }
      });
    }
  }

  /**
   * Sends the data from the form to the backend
   */
  sendData() {
    this.mealPlanResponse = {};
    this.expandedStates = [];
    // this.snackExpandedStates = [];
    this.selectedOptions = [];

    const data = {
      people: this.people,
      user_id: localStorage.getItem('uid') || null,
      selectedUnit: this.selectedUnit,
      dietaryConstraint: this.selectedDietaryConstraint,
      healthGoal: this.selectedHealthGoal,
      religiousConstraint: this.selectedReligiousConstraint,
      likedFoods: this.likedFoods.value,
      dislikedFoods: this.dislikedFoods.value,
      favouriteCuisines: this.cuisines.value,
      allergies: this.allergies.value,
      snacks: this.snacks.value,
      breakfasts: this.breakfasts.value,
      minDate: this.startDate.get('start')!.value?.getTime(),
      maxDate: this.startDate.get('end')!.value?.getTime(),
      includedRecipes: this.includedRecipes,
      excludedRecipes: this.excludedRecipes,
    };

    // if (!data.maxDate && data.minDate) {
    //   data.maxDate = data.minDate;
    // }

    console.log(data.maxDate);
    console.log(data.minDate);
    localStorage.setItem('minDate', String(data.minDate));
    localStorage.setItem('maxDate', String(data.maxDate));

    if (!data.likedFoods) {
      data.likedFoods = 'None';
    }

    if (!data.minDate || !data.maxDate) {
      this.toast.error('Please select both start date and end date!');
    } else if (!this.people) {
      this.toast.error('Please enter the details!');
    } else {
      if (
        this.userSubscriptionTypeId === 1 ||
        this.userSubscriptionTypeId === 2 ||
        (this.userSubscriptionTypeId === 0 &&
          data.maxDate === data.minDate &&
          this.selectedHealthGoal === 'lose_weight') ||
        (this.userSubscriptionTypeId === 3 &&
          this.selectedHealthGoal === 'lose_weight')
      ) {
        this.element.nativeElement.style.display = 'block';
        this.element.nativeElement.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'start',
        });
        this.showSpinner = true;
        this.searchClicked = true;
        this.http
          .post('http://127.0.0.1:5000/api', data, {
            responseType: 'text',
          })
          .subscribe(
            (response) => {
              console.log(response);
              this.element.nativeElement.style.display = 'none';
              this.errorDiv.nativeElement.style.display = 'none';
              this.showSpinner = false;
              this.mealPlanResponse = JSON.parse(response);
              this.getShoppingListFromBackend().subscribe(
                (secondResponse) => {
                  console.log('Fetched Shopping List: ', secondResponse);
                  this.shoppingListData = secondResponse;
                },
                (error) => {
                  console.error(error);
                }
              );

              const numDays = this.getNumDays(this.mealPlanResponse);
              for (let i = 0; i < numDays; i++) {
                this.expandedStates.push(
                  new Array(this.mealPlanResponse.days[i].recipes.length).fill(
                    false
                  )
                );
                this.selectedOptions.push(new Array(3).fill('keep'));
              }

              // this.snackExpandedStates = new Array(
              //   this.mealPlanResponse.snacks.length
              // ).fill(false);

              this.includeAllRecipes(this.mealPlanResponse.days);
            },
            (error) => {
              console.error('Error sending data:', error);
              this.element.nativeElement.style.display = 'none';
              this.showSpinner = false;
              this.errorDiv.nativeElement.style.display = 'block';
            }
          );
      } else {
        this.showSpinner = false;
        this.errorDiv.nativeElement.style.display = 'block';
        this.element.nativeElement.style.display = 'none';
        const selectedHealthGoalObject = healthGoals.find(
          (goal) => goal.value === this.selectedHealthGoal
        );
        const title = "Sorry, we can't generate the meal plan.";
        if (localStorage.getItem('uid')) {
          // User is logged in
          const message =
            'Selected health goal is for subscribed users.<br> Subscribe to get the meal plan to ' +
            selectedHealthGoalObject?.viewValue +
            '!<br> Without subscription, you can generate meal plan to lose weight only.';
          this.openDialog(title, message, '/payment', 'Subscribe');
        } else {
          // User is not logged in
          const message =
            'Login to explore more features!<br>Without login, you can only generate the meal plan to lose weight for one day.';
          this.openDialog(title, message, '/login', 'Login');
        }
      }
    }
  }

  /**
   * Gets the total price of the recipe
   * @returns The total price of the recipe
   */
  getTotalPrice(): number {
    let totalPrice = 0;
    if (this.recipe && this.recipe.length > 0) {
      for (const recipeItem of this.recipe) {
        totalPrice += recipeItem.price;
      }
    }
    return Number(totalPrice.toFixed(2));
  }

  /**
   * Changes the number of people in the form
   * @param change The change in the number of people, always 1 or -1
   */
  changeFields(change: number) {
    this.numOfPeople += change;
    const difference = this.numOfPeople - this.people.length;

    if (difference > 0) {
      for (let i = 0; i < difference; i++) {
        this.people.push({
          age: null,
          weight: null,
          height: null,
          gender: null,
          activityLevel: null,
        });
      }
    } else if (difference < 0) {
      this.people.splice(this.numOfPeople);
    }
  }

  /**
   * Toggles the expanded state of the recipe card at the given index
   * @param index The index of the recipe card to toggle
   */
  toggleExpand(i: number, j: number) {
    this.expandedStates[i][j] = !this.expandedStates[i][j];
  }

  // /**
  //  * Toggles the expanded state of the snack card at the given index
  //  * @param index The index of the snack card to toggle
  //  */
  // toggleSnackExpand(i: number) {
  //   this.snackExpandedStates[i] = !this.snackExpandedStates[i];
  // }

  /**
   * Closes the people panel
   */
  closePanel() {
    this.peoplePanel.close();
  }

  /**
   * Sets the selected unit to the given unit
   * @param unit The unit to set the selected unit to, either 'metric' or 'imperial'
   */
  setSelectedUnit(unit: string): void {
    this.selectedUnit = unit;
  }

  /**
   * Gets the image url for a recipe based on the id of the recipe
   * @param id The id of the recipe
   * @returns The url of the image
   */
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

  /**
   * Click handler for the "Get Full Meal Plan" button
   */
  getFullMealPlan() {}

  /**
   * Replace a recipe in the meal plan
   * @param id The id of the recipe to be replaced
   */
  refreshRecipe(id: string) {
    console.log(this.mealPlanResponse);
    this.refresh.refreshRecipe(id, this.mealPlanResponse).subscribe(
      (response) => {
        this.toast.success('Recipe refreshed successfully!');
        console.log('recipe replaced', response);
        this.mealPlanResponse = this.updateMealPlan(response.meal_plan);
        console.log('updated meal plan', this.mealPlanResponse);

        // After the meal plan is updated, get the updated shopping list
        this.getShoppingListFromBackend().subscribe(
          (updatedShoppingList) => {
            this.shoppingListData = updatedShoppingList;
          },
          (error) => {
            console.error(error);
          }
        );
      },
      (error) => {
        this.toast.error(
          'Opps look like the server is too busy, try again later!'
        );
        console.log('error', error);
      }
    );
  }

  openShoppingListDialog(): void {
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

  /**
   * Update the meal plan data with the new meal plan
   * @param mealPlan The new meal plan with a replaced recipe
   * @returns The updated meal plan data
   */
  updateMealPlan(mealPlan: any) {
    this.mealPlanResponse = mealPlan;
    return this.mealPlanResponse;
  }

  /**
   * Refreshes the snack list
   * @param id  The id of the snack
   * @param i  The index of the snack
   */
  refreshSnack(id: number, i: number) {
    this.recipe = [];
    for (const snack of this.mealPlanResponse.snacks) {
      this.recipe.push(snack);
    }
  }

  /**
   * Listener for the "Replace Meal" dropdown
   * @param event The event that triggered the listener
   * @param id The id of the recipe
   */
  onReplaceMealChange(event: any, id: number, i: number, j: number) {
    const value = event.value;

    if (value === 'replace') {
      if (!this.excludedRecipes.includes(id)) {
        // add the recipe to the excluded recipes
        this.excludedRecipes.push(id);

        // remove the recipe from the included recipes
        const index = this.includedRecipes.indexOf(id);
        if (index > -1) {
          this.includedRecipes.splice(index, 1);
        }
      }
    } else if (value === 'keep') {
      // remove the recipe from the excluded recipes
      const index = this.excludedRecipes.indexOf(id);
      if (index > -1) {
        this.excludedRecipes.splice(index, 1);
      }

      // add the recipe to the included recipes
      if (!this.includedRecipes.includes(id)) {
        this.includedRecipes.push(id);
      }
    }
  }

  /**
   * Changes the selected health goal when the health goal is changed
   * @param index The index of the health goal
   * @param healthGoal The health goal to change to
   */
  healthGoalChange(index: number, healthGoal: string) {
    this.selectedHealthGoal = healthGoal;
    this.selectedHealthGoalIndex = index;
    // reset the included and excluded recipes since the health goal changed
    this.includedRecipes = [];
    this.excludedRecipes = [];
  }

  /**
   * Checks if the passed object is empty
   * @param obj The object to check
   * @returns True if the object is empty, false otherwise
   */
  isEmpty(obj: any) {
    return Object.keys(obj).length === 0;
  }

  /**
   * Rounds the given number to the nearest integer
   * @param num The number to round
   * @returns The rounded number
   */
  floor(num: number) {
    return Math.floor(num);
  }

  /**
   * Gets the number of recipes in the meal plan
   * @param response The response from the backend
   * @returns The number of recipes in the meal plan
   */
  getNumRecipes(response: any) {
    let numRecipes = 0;
    for (const day of response.days) {
      numRecipes += day.recipes.length;
    }
    this.numRecipes = numRecipes;
    return numRecipes;
  }

  /**
   * Gets the number of days in the meal plan
   * @param response The response from the backend
   * @returns The number of days in the meal plan
   */
  getNumDays(response: any) {
    this.numDays = response.days.length;
    return response.days.length;
  }

  /**
   * Adds all recipes to the included recipes and clears the excluded recipes
   * @param days The days in the meal plan
   */
  includeAllRecipes(days: any[]) {
    this.includedRecipes = [];
    for (const day of days) {
      for (const recipe of day.recipes) {
        if (!this.includedRecipes.includes(recipe.id)) {
          this.includedRecipes.push(recipe.id);
        }
      }
    }

    // clear the excluded recipes
    this.excludedRecipes = [];
  }

  /**
   * Formats a given vitamin string to be displayed
   * @param vitamin The vitamin string to format
   * @returns The formatted vitamin string
   */
  displayVitamin(vitamin: string) {
    // given a string "vitamin_A", return "Vitamin A"
    const vitaminLetter = vitamin.split('_')[1].toUpperCase();
    return `Vitamin ${vitaminLetter}`;
  }

  /**
   * Scrolls to the top of the page when called
   */
  scrollToTop() {
    this.start.nativeElement.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
      inline: 'start',
    });
  }

  openDialog(
    title: string,
    message: string,
    redirectUrl: string,
    confirmLabel: string
  ) {
    const dialogRef = this.dialog.open(GeneratePopUpComponent, {
      width: '500px',
      data: { title, message, confirmLabel },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.router.navigate([redirectUrl]);
      }
    });
  }

  openRecipeDialog(recipe: any): void {
    this.dialog.open(RecipeDialogComponent, {
      data: {
        recipe: recipe,
        imageUrl: this.getImageUrl(recipe.id),
      },
      width: '800px',
    });
  }

  getShoppingListFromBackend(): Observable<ShoppingList[]> {
    return this.http.post<ShoppingList[]>(
      'http://127.0.0.1:5000/api/get-shopping-list',
      this.mealPlanResponse,
      {
        headers: new HttpHeaders({
          'Content-Type': 'application/json',
        }),
      }
    );
  }
}
