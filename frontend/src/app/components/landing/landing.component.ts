import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { FormControl, FormGroup, NgForm } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatExpansionPanel } from '@angular/material/expansion';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { Observable } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { RecipeDialogComponent } from '../dialogues/recipe/recipe.component';
import { RefreshComponent } from 'src/app/services/refresh/refresh.component';
import { environment } from 'src/environments/environment';
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
import { ChangeDetectorRef } from '@angular/core';
import { NgZone } from '@angular/core';
import { SearchDialogComponent } from '../search-dialog/search-dialog.component';
import { OutOfRangeDialogComponent } from '../dialogues/out-of-range-dialog/out-of-range-dialog.component';
import { UsersService } from 'src/app/services/users.service';

@Component({
  selector: 'app-landing',
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css'],
})
export class LandingComponent implements OnInit {
  expanded: boolean = false; // expanded state of the panel--for the nutrient table

  // group the nutrients into 3 categories: macros, vitamins, minerals
  macros: any[] = [];
  vitamins: any[] = [];
  minerals: any[] = [];
  energy: any[] = [];

  constructor(
    private http: HttpClient,
    private dialog: MatDialog,
    private router: Router,
    private toast: HotToastService,
    private refresh: RefreshComponent,
    private zone: NgZone,
    private cdRef: ChangeDetectorRef,
    private route: ActivatedRoute,
    private usersService: UsersService
  ) {}

  // change date format to e.g. September 14, 2024
  formatDate(date: string): string {
    const [year, month, day] = date.split('-').map(Number);
    const localDate = new Date(year, month - 1, day);
    console.log('Original Date:', date);
    console.log('Local Date (Corrected):', localDate.toLocaleString());

    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return localDate.toLocaleDateString('en-US', options);
  }
  // generate day of the week
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

  readonly MIN_PEOPLE = 1;
  readonly MAX_PEOPLE = 6;
  readonly TAC_KEY = 'acceptedTac';
  readonly defaultImgPath =
    '../../../assets/images/meal-plan-images/default_meal_picture.png';
  readonly OUT_OF_RANGE =
    'This meal plan has some nutrients which are out of the target range.   Please see the table at the bottom for details.';
  readonly NO_RECIPES =
    "We're sorry!  We could not find a meal plan that fits your constraints.";
  readonly PAID_SUBSCRIPTION_TYPES = [2, 3, 4, 5];

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
  userId: string | null = null;
  isFromHamburger: boolean = false;

  people: {
    age?: number | null;
    weight?: number | null;
    height?: number | null;
    gender?: string | null;
    activityLevel?: string | null;
  }[] = Array.from({ length: this.MIN_PEOPLE }, () => ({
    age: undefined,
    weight: undefined,
    height: undefined,
    gender: undefined,
    activityLevel: undefined,
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
  likedFoods = new FormControl<string[]>([]);
  dislikedFoods = new FormControl<string[]>([]);
  cuisines = new FormControl<string[]>([]);
  allergies = new FormControl<string[]>([]);
  breakfasts = new FormControl<string[]>([]);
  snacks = new FormControl<string[]>([]);
  expandedStates: boolean[][] = [];
  snackExpandedStates: boolean[] = [];

  async ngOnInit() {
    this.userId = localStorage.getItem('uid');
    console.log('user ID: ' + this.userId);
    console.log('email: ' + localStorage.getItem('email'));

    this.route.queryParamMap.subscribe((params) => {
      this.isFromHamburger = params.get('guest') === 'true';
    });

    if (localStorage.getItem('uid')) {
      try {
        const response: any = await this.http
          .get(
            `${
              environment.baseUrl
            }/api/subscription_type_id/${localStorage.getItem('uid')}`
          )
          .toPromise();
        if (response.subscription_type_id) {
          localStorage.setItem(
            'subscription_type_id',
            response.subscription_type_id
          ); // 1: free trial, 2: paid trial, 3: monthly, 4: quarterly, 5: yearly
          this.userSubscriptionTypeId = response.subscription_type_id;
        }
      } catch (error) {
        console.error('Error:', error);
      }
    } else {
      this.userSubscriptionTypeId = 0;
    }
    console.log('subscription type ID:' + this.userSubscriptionTypeId);
    // Prefill the profile info for logged in user
    if (localStorage.getItem('uid')) {
      this.usersService.loadCachedUserProfile();
      this.usersService.profile$.subscribe((user) => {
        if (user) {
          this.people[0].age = Number(user.age);
          this.people[0].weight = Number(user.weight);
          this.people[0].height = Number(user.height);
          this.people[0].gender = user.gender;
          this.people[0].activityLevel = user.activity_level;
          this.selectedUnit = user.selected_unit || 'metric';
          this.selectedHealthGoal = user.health_goal;
          this.selectedHealthGoalIndex = this.healthGoals.findIndex(
            (goal) => goal.value === user.health_goal
          );
        }
      });
      this.usersService.preference$.subscribe((user) => {
        if (user) {
          this.snacks.setValue(user.snacks || []);
          this.breakfasts.setValue(user.breakfasts || []);
          this.likedFoods.setValue(user.likedFoods || []);
          this.dislikedFoods.setValue(user.dislikedFoods || []);
          this.cuisines.setValue(user.favouriteCuisines || []);
          this.allergies.setValue(user.allergies || []);
          this.selectedDietaryConstraint = user.dietaryConstraint || 'none';
          this.selectedReligiousConstraint = user.religiousConstraint || 'none';
        }
      });
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
    console.log('included recipes:', data.includedRecipes);
    console.log('this included recipes:', this.includedRecipes);

    // if (!data.maxDate && data.minDate) {
    //   data.maxDate = data.minDate;
    // }

    console.log(data.maxDate);
    console.log(data.minDate);
    localStorage.setItem('minDate', String(data.minDate));
    localStorage.setItem('maxDate', String(data.maxDate));

    if (!data.minDate || !data.maxDate) {
      this.toast.error('Please select both start date and end date!');
    } else if (!this.people) {
      this.toast.error('Please enter the details!');
    } else {
      if (
        this.PAID_SUBSCRIPTION_TYPES.includes(this.userSubscriptionTypeId) ||
        (this.userSubscriptionTypeId === 0 && data.maxDate === data.minDate) || // non-signed user
        this.userSubscriptionTypeId === 1 // TODO: Replace this line with the one below before production
        // (this.userSubscriptionTypeId === 1 && data.maxDate === data.minDate) // free trial user
      ) {
        this.element.nativeElement.style.display = 'block';
        this.element.nativeElement.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'start',
        });
        this.showSpinner = true;
        this.searchClicked = true;

        const updateResult = this.updateLocalStorage(data);

        this.http
          .post(`${environment.baseUrl}/api`, data, {
            responseType: 'text',
          })
          .subscribe(
            (response) => {
              // console.log('Raw Response:', response);

              console.log(response); //here we have the nutrient data
              this.element.nativeElement.style.display = 'none';
              this.errorDiv.nativeElement.style.display = 'none';
              this.showSpinner = false;
              this.mealPlanResponse = JSON.parse(response);

              // Populate the nutrient table when the meal plan is generated
              // BCIT May 2025
              if (this.mealPlanResponse.tableData) {
                this.categorizeNutrients();
              }
              // Populate the shopping list when the meal plan is generated
              // BCIT May 2025
              this.shoppingListData = this.transformMealPlanToShoppingList(
                this.mealPlanResponse
              );
              this.cdRef.detectChanges();
              // this.getShoppingListFromBackend().subscribe(
              //   (secondResponse) => {
              //     console.log('Fetched Shopping List: ', secondResponse);
              //     this.shoppingListData = secondResponse;
              //   },
              //   (error) => {
              //     console.error(error);
              //   }
              // );

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
        if (
          this.PAID_SUBSCRIPTION_TYPES.includes(this.userSubscriptionTypeId) &&
          data.maxDate !== data.minDate
        ) {
          this.showSpinner = false;
          this.errorDiv.nativeElement.style.display = 'block';
          this.element.nativeElement.style.display = 'none';
          const selectedHealthGoalObject = healthGoals.find(
            (goal) => goal.value === this.selectedHealthGoal
          );
        } else if (
          (this.userSubscriptionTypeId === 0 &&
            data.maxDate === data.minDate) ||
          (this.userSubscriptionTypeId === 1 && data.maxDate === data.minDate)
        ) {
          this.showSpinner = false;
          this.errorDiv.nativeElement.style.display = 'block';
          this.element.nativeElement.style.display = 'none';
          const selectedHealthGoalObject = healthGoals.find(
            (goal) => goal.value === this.selectedHealthGoal
          );
        } else if (
          this.userSubscriptionTypeId === 0 &&
          data.maxDate != data.minDate
        ) {
          this.showSpinner = false;
          this.errorDiv.nativeElement.style.display = 'none';
          this.element.nativeElement.style.display = 'none';

          const title = 'Subscription Required';
          const message =
            'Multi-day plans require a subscription. Sign up and try it now for only $5/month. Cancel anytime.';
          this.openDialog(title, message, '/sign-up', 'Sign Up');
        } else {
          // this.toast.error('Unsubscribed users can only generate a meal plan for one day!');
          this.showSpinner = false;
          this.errorDiv.nativeElement.style.display = 'none';
          this.element.nativeElement.style.display = 'none';

          const title = 'Subscription Required';
          const message =
            'Multi-day plans require a subscription. Try it now for only $5/month. Cancel anytime.';
          this.openDialog(title, message, '/payment', 'Upgrade');
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
   * Gets the URL for the ingredients CSV file based on the recipe's ID.
   *
   * @param id The unique identifier of the recipe.
   * @returns The URL pointing to the ingredients CSV file.
   *
   * @example
   * const ingredientsUrl = this.getIngredientsCsvUrl(456);
   * // ingredientsUrl will be "https://storage.googleapis.com/meal_planiq_ingredients_files/456.csv"
   *
   * @author BCIT May 2025
   */
  getIngredientsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_ingredients_files/${id}.csv`;
  }

  /**
   * Gets the URL for the instructions CSV file based on the recipe's ID.
   *
   * @param id The unique identifier of the recipe.
   * @returns The URL pointing to the instructions CSV file.
   *
   * @example
   * const instructionsUrl = this.getInstructionsCsvUrl(456);
   * // instructionsUrl will be "https://storage.googleapis.com/meal_planiq_instructions_files/456_instructions.csv"
   *
   * @author BCIT May 2025
   */
  getInstructionsCsvUrl(id: number): string {
    return `https://storage.googleapis.com/meal_planiq_instructions_files/${id}_instructions.csv`;
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
        this.mealPlanResponse = response.meal_plan;
        this.shoppingListData = response.shopping_list;
        console.log('updated meal plan (refresh)', this.mealPlanResponse);

        this.categorizeNutrients();

        if (response.shopping_list) {
          this.shoppingListData = response.shopping_list;
          console.log(
            'Shopping List from refreshRecipe service:',
            this.shoppingListData
          );
        } else {
          // Fallback if the service unexpectedly doesn't provide it
          console.warn(
            'Shopping list not provided by refresh service, transforming manually.'
          );
          this.shoppingListData = this.transformMealPlanToShoppingList(
            this.mealPlanResponse
          );
        }
        this.cdRef.detectChanges();
        // After the meal plan is updated, get the updated shopping list
        // this.getShoppingListFromBackend().subscribe(
        //   (updatedShoppingList) => {
        //     this.shoppingListData = updatedShoppingList;
        //   },
        //   (error) => {
        //     console.error(error);
        //   }
        // );
      },
      (error) => {
        this.toast.error(
          'Opps look like the server is too busy, try again later!'
        );
        console.log('error', error);
      }
    );
  }

  deleteRecipe(id: string): void {
    console.log('Deleting recipe with ID:', id);

    this.refresh.deleteRecipe(id, this.mealPlanResponse).subscribe(
      (response) => {
        if (response.error) {
          this.toast.error(response.error);
          console.error('Error from backend:', response.error);
          return;
        }

        // Successfully deleted recipe and got updated meal plan
        this.toast.success('Recipe deleted and meal plan refreshed!');
        console.log('recipe replaced (delete)', response);

        // Update the frontend with the updated meal plan from the backend
        this.mealPlanResponse = this.updateMealPlan(response.meal_plan);
        console.log('updated meal plan (delete)', this.mealPlanResponse);
        this.categorizeNutrients();

        if (response.shopping_list) {
          this.shoppingListData = response.shopping_list;
          console.log(
            'Shopping List from deleteRecipe service:',
            this.shoppingListData
          );
        } else {
          console.warn(
            'Shopping list not provided by delete service, transforming manually.'
          );
          this.shoppingListData = this.transformMealPlanToShoppingList(
            this.mealPlanResponse
          );
        }
        this.cdRef.detectChanges();

        // After the meal plan is updated, get the updated shopping list
        // this.getShoppingListFromBackend().subscribe(
        //   (updatedShoppingList) => {
        //     this.shoppingListData = updatedShoppingList;
        //   },
        //   (error) => {
        //     console.error(error);
        //   }
        // );
      },
      (error) => {
        this.toast.error('Oops, the server is too busy, try again later!');
        console.log('error', error);
      }
    );
  }

  updateNutrientTable(recipe: any) {
    console.log('recipe test:', recipe);
    const nutrientsToUpdate = [
      'calories',
      'carbohydrates',
      'protein',
      'fat',
      'fiber',
      'fiber',
      'calcium',
      'iron',
      'zinc',
      'vitamin_a',
      'vitamin_c',
      'vitamin_d',
      'vitamin_e',
      'vitamin_k',
    ];
    nutrientsToUpdate.forEach((key) => {
      const nutrient = this.mealPlanResponse.tableData.find((n: any) =>
        n.nutrientName.toLowerCase().includes(key)
      );
      if (nutrient) {
        nutrient.actual -= parseFloat(recipe[key] || 0);
      }
    });
    this.mealPlanResponse.tableData.forEach((nutrient: any) => {
      if (nutrient.actual < 0) {
        nutrient.actual = 0;
      }
    });
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
    const data = {
      minDate: this.startDate.get('start')!.value?.getTime(),
      maxDate: this.startDate.get('end')!.value?.getTime(),
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
    // } else if (this.userSubscriptionTypeId === 0) {
    //   const title = 'Sign Up and Try!';
    //   const message =
    //     'To see recipe details for this plan, please sign up.  No credit card or payment required.';
    //   this.openDialog(title, message, '/sign-up', 'Sign Up');
    // }
  }

  getShoppingListFromBackend(): Observable<ShoppingList[]> {
    return this.http.post<ShoppingList[]>(
      `${environment.baseUrl}/api/get-shopping-list`,
      this.mealPlanResponse,
      {
        headers: new HttpHeaders({
          'Content-Type': 'application/json',
        }),
      }
    );
  }

  /**
   * Transforms the meal plan response into a shopping list format.
   *
   * @param mealPlan The meal plan response object.
   * @returns An array of shopping lists, each containing a date and items.
   *
   * @author BCIT May 2025
   */
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

  /**
   * Generates a status message for a given nutrient, indicating whether its actual value
   * is lower or higher than the recommended target range.
   *
   * Extracts the unit from the nutrient's display name (if present inside parentheses)
   * and formats a readable message accordingly.
   *
   * @param nutrient - The nutrient object containing actual, min, max, and displayName values.
   * @returns A formatted status message string, or an empty string if within range.
   *
   * @author BCIT May 2025
   */
  getNutrientStatusMessage(nutrient: any): string {
    const actual = nutrient.actual; // actual value from backend
    const min = nutrient.display_target_min; // target minimum value
    const max = nutrient.display_target_max; // target maximum value
    const name = nutrient.displayName; // nutrient display name

    // Extract unit from displayName (text inside parentheses)
    const unitMatch = name.match(/\(([^)]+)\)/);
    const unit = unitMatch ? unitMatch[1] : ''; // fallback to empty if no unit found

    // Clean up display name by removing unit and parentheses
    const cleanName = name.replace(/\s*\(.*?\)/, '');

    // Return message depending on value status
    if (actual < min && min != null) {
      return `${cleanName} is ${actual}${
        unit ? ' ' + unit : ''
      }, lower than the recommended ${min}${unit ? ' ' + unit : ''}.`;
    } else if (actual > max && max != null) {
      return `${cleanName} is ${actual}${
        unit ? ' ' + unit : ''
      }, higher than the recommended ${max}${unit ? ' ' + unit : ''}.`;
    } else {
      return ''; // No message if within range or if no min/max provided
    }
  }

  /**
   * Aggregates all out-of-range messages for nutrients in the current meal plan.
   * Adds a predefined header message if any nutrient is found out of range.
   *
   * Combines all nutrients (energy, macros, vitamins, minerals) into a single list for evaluation.
   *
   * @returns An array of status messages for out-of-range nutrients.
   *
   * @author BCIT May 2025
   */
  getOutOfRangeMessages(): string[] {
    const messages: string[] = [];

    // Combine nutrients from all categories into one array
    const allNutrients = [
      ...this.energy,
      ...this.macros,
      ...this.vitamins,
      ...this.minerals,
    ];

    // Check each nutrient's status message
    allNutrients.forEach((nutrient) => {
      const message = this.getNutrientStatusMessage(nutrient);
      if (message) {
        // Add header message only once when first out-of-range nutrient found
        if (messages.length === 0) {
          messages.push(this.OUT_OF_RANGE);
        }
        messages.push(message);
      }
    });

    return messages;
  }

  /**
   * Opens a popup dialog window displaying out-of-range nutrient messages.
   * Excludes the header message and passes only the nutrient-specific messages to the dialog component.
   * @author BCIT May 2025
   */
  openOutOfRangeDialog(): void {
    // Skip the OUT_OF_RANGE header (first element) and pass the rest
    const messages = this.getOutOfRangeMessages().slice(1);

    // Open Angular Material dialog with messages as injected data
    this.dialog.open(OutOfRangeDialogComponent, {
      width: '600px',
      data: messages,
    });
  }
  /**
   * Replaces a recipe in the meal plan at the specified day and recipe position.
   *
   * Calls the refresh service's replaceRecipe endpoint with the selected recipe ID,
   * and updates the meal plan and nutrient tables on successful response.
   * Also updates the shopping list based on the returned data.
   *
   * @param dayIndex - The index of the day in the meal plan to replace the recipe in.
   * @param recipeIndex - The index of the recipe within the day to replace.
   * @param newRecipeId - The ID of the new recipe to insert into the meal plan.
   *
   * @author BCIT May 2025
   */
  replaceRecipe(
    dayIndex: number,
    recipeIndex: number,
    newRecipeId: string
  ): void {
    this.refresh
      .replaceRecipe(newRecipeId, dayIndex, recipeIndex, this.mealPlanResponse)
      .subscribe(
        (response) => {
          this.toast.success('Recipe replaced successfully!');
          console.log('recipe replaced (replace)', response);

          // Update meal plan and nutrients table
          this.processUpdatedMealPlan(response.meal_plan);

          // Update shopping list from server response if available
          if (response.shopping_list) {
            this.shoppingListData = response.shopping_list;
            console.log(
              'Shopping List from refreshRecipe service:',
              this.shoppingListData
            );
          } else {
            // Fallback if shopping list was not returned
            console.warn(
              'Shopping list not provided by refresh service, transforming manually.'
            );
            this.shoppingListData = this.transformMealPlanToShoppingList(
              this.mealPlanResponse
            );
          }

          // Trigger Angular change detection manually for UI updates
          this.cdRef.detectChanges();
        },
        (error) => {
          this.toast.error('Oops, the server is too busy, try again later!');
          console.error('error', error);
        }
      );
  }

  /**
   * Updates the meal plan and re-categorizes the nutrients for display.
   *
   * @param mealPlan - The updated meal plan object returned from the backend.
   *
   * @author BCIT May 2025
   */
  processUpdatedMealPlan(mealPlan: any): void {
    this.mealPlanResponse = this.updateMealPlan(mealPlan);
    this.categorizeNutrients();
  }

  /**
   * Opens the custom Search Dialog to allow users to manually search and select a replacement recipe.
   *
   * Handles subscription-level permissions for access to this feature.
   *
   * @param dayIndex - The index of the day in the meal plan for the recipe to replace.
   * @param recipeIndex - The index of the recipe within that day's meal plan.
   *
   * @author BCIT May 2025
   */
  openSearchDialog(dayIndex: number, recipeIndex: number): void {
    // if (
    //   this.userSubscriptionTypeId === 1 ||
    //   this.userSubscriptionTypeId === 2 ||
    //   this.userSubscriptionTypeId === 3
    // ) {
    const dialogRef = this.dialog.open(SearchDialogComponent);

    // Wait for the dialog to close and act on the selected recipe
    dialogRef.afterClosed().subscribe((selectedRecipe) => {
      if (selectedRecipe?.id) {
        this.replaceRecipe(dayIndex, recipeIndex, selectedRecipe);
      }
    });
    // } else if (this.userSubscriptionTypeId === 0) {
    //   // For unsubscribed users, show upgrade prompt dialog
    //   const title = 'Sign Up and Try!';
    //   const message = 'To see recipe details for this plan, please sign up. No credit card or payment required.';
    //   this.openDialog(title, message, '/sign-up', 'Sign Up');
    // }
  }

  /**
    Returns the user-friendly label (viewValue) for a given value

    @param value - The internal value to match (e.g., 'egg')
    @param list - The list of options with value and viewValue pairs
    @returns The corresponding viewValue (e.g., 'Eggs') or the original value if not found
  */
  getViewValue(
    value: string,
    list: { value: string; viewValue: string }[]
  ): string {
    return list.find((item) => item.value === value)?.viewValue || value;
  }

  updateLocalStorage(data: any): void {
    const localProfile = {
      user_name: JSON.parse(localStorage.getItem('userProfile') || '{}').user_name,
      email: localStorage.getItem('email'),
      age: data.people[0].age,
      weight: data.people[0].weight,
      height: data.people[0].height,
      gender: data.people[0].gender,
      activity_level: data.people[0].activityLevel,
      health_goal: data.healthGoal,
      selected_unit: data.selectedUnit,
      user_id: localStorage.getItem('uid')
    };

    const localPreference = {
      likedFoods: data.likedFoods,
      dislikedFoods: data.dislikedFoods,
      favouriteCuisines: data.favouriteCuisines,
      allergies: data.allergies,
      snacks: data.snacks,
      breakfasts: data.breakfasts,
      dietaryConstraint: data.dietaryConstraint,
      religiousConstraint: data.religiousConstraint,
    };

    this.usersService.updateLocalUserPreference(localPreference);
    this.usersService.updateLocalUserProfile(localProfile);
  }
}
