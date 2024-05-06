import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { UsersService } from 'src/app/services/users.service';
import { FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { trigger, transition, style, animate } from '@angular/animations';

interface unit {
  value: string;
  viewValue: string;
}
interface activityLevel {
  value: string;
  viewValue: string;
}
interface gender {
  value: string;
  viewValue: string;
}
interface vegeterian {
  value: string;
  viewValue: string;
}
interface healthGoal {
  value: string;
  viewValue: string;
}
interface cookingSkill {
  value: string;
  viewValue: string;
}
interface Religious {
  value: string;
  viewValue: string;
}
interface Cost {
  value: string;
  viewValue: string;
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  showSpinner: boolean = false;
  user$ = this.usersService.currentUserProfile$;
  minDate: Date;
  maxDate: Date;
  age: number = 0;
  weight: number = 0;
  weightMetric: number = 0;
  height: number = 0;
  heightMetric: number = 0;
  numOfPeople: number = 1;
  receivedData: string = '';
  recipe: any[] = [];
  bmiValue: number = 0;
  tdeeValue: number = 0;
  recipesFetched = false;
  people: {
    age: number | null;
    weight: number | null;
    height: number | null;
  }[] = [];
  selectedUnit: string = 'metric';
  units: unit[] = [
    { value: 'metric', viewValue: 'Metric' },
    { value: 'imperial', viewValue: 'Imperial' },
  ];
  selectedActivityLevel: string = '';
  activityLevels: activityLevel[] = [
    { value: 'Sedentary', viewValue: 'Sedentary' },
    { value: 'Low_Active', viewValue: 'Lightly Active' },
    { value: 'Active', viewValue: 'Moderately Active' },
    { value: 'Very_Active', viewValue: 'Very Active' },
  ];
  selectedGender: string = '';
  genders: gender[] = [
    { value: 'Male', viewValue: 'Male' },
    { value: 'Female', viewValue: 'Female' },
    { value: 'Female', viewValue: 'Other' },
  ];
  selectedDietaryConstraint: string = '';
  vegeterians: vegeterian[] = [
    { value: 'none', viewValue: 'None' },
    { value: 'vegan', viewValue: 'Vegan' },
    { value: 'pescatarian', viewValue: 'Pescatarian' },
    { value: 'lacto', viewValue: 'Lacto Vegeterian' },
    { value: 'lacto_ovo', viewValue: 'Lacto-ovo Vegeterian' },
    { value: 'ovo', viewValue: 'Ovo Vegeterian' },
    { value: 'flexitarian', viewValue: 'Flexitarians Vegeterian' },
  ];
  selectedHealthGoal: string = '';
  healthGoals: healthGoal[] = [
    { value: 'lose_weight', viewValue: 'Lose Weight' },
    { value: 'build_muscle', viewValue: 'Build Muscle' },
    { value: 'maintain_health', viewValue: 'Maintain General Health' },
  ];
  selectedCookingSkill: string = '';
  cookingSkills: cookingSkill[] = [
    { value: 'beginner', viewValue: 'Beginner' },
    { value: 'intermediate', viewValue: 'Intermediate' },
    { value: 'advanced', viewValue: 'Advanced' },
    { value: 'professional', viewValue: 'Professional' },
  ];
  selectedReligiousConstraint: string = '';
  religiousConstraints: Religious[] = [
    { value: 'none', viewValue: 'None' },
    { value: 'halal', viewValue: 'Halal' },
    { value: 'kousher', viewValue: 'Kousher' },
  ];
  selectedCost: string = '';
  Costs: Cost[] = [
    { value: '$', viewValue: '$' },
    { value: '$$', viewValue: '$$' },
    { value: '$$$', viewValue: '$$$' },
    { value: '$$$$', viewValue: '$$$$' },
  ];

  constructor(private http: HttpClient, private usersService: UsersService) {
    const currentDate = new Date();
    const maxDate = new Date();
    maxDate.setDate(currentDate.getDate() + 7);
    this.minDate = currentDate;
    this.maxDate = maxDate;
  }

  ngOnInit(): void {}

  sendData() {
    this.showSpinner = true;

    if (this.selectedUnit === 'imperial') {
      this.weightMetric = this.weight * 0.453592;
      this.heightMetric = this.height * 2.54;
    } else {
      this.weightMetric = this.weight;
      this.heightMetric = this.height;
    }

    const data = {
      age: this.age,
      weight: this.weightMetric,
      height: this.heightMetric,
      numOfPeople: this.numOfPeople,
      activityLevel: this.selectedActivityLevel,
      gender: this.selectedGender,
      dietaryConstraint: this.selectedDietaryConstraint,
      healthGoal: this.selectedHealthGoal,
      cookingSkill: this.selectedCookingSkill,
      religiousConstraint: this.selectedReligiousConstraint,
      likedFoods: this.likedFoods.value,
      dislikedFoods: this.dislikedFoods.value,
      favouriteCuisines: this.Cuisines.value,
      cost: this.selectedCost,
      minDate: this.minDate,
      maxDate: this.maxDate,
    };

    console.log('Sent data:', data);

    this.http.post('/api/endpoint', data, { responseType: 'text' }).subscribe(
      (response) => {
        console.log('Received data', response);
        this.showSpinner = false;

        const parsedResponse = JSON.parse(response);

        if (Array.isArray(parsedResponse)) {
          this.recipe = parsedResponse.filter(
            (recipeItem) => recipeItem.title && recipeItem.title.trim() !== ''
          );
        } else {
          this.recipe = [];
        }
        this.recipesFetched = true;

        // Set userBMI and userTDEE based on the parsed response from the backend
        this.bmiValue = parsedResponse[0].bmi;
        this.tdeeValue = parsedResponse[0].tdee;
      },
      (error) => {
        console.error('Error sending data:', error);
      }
    );
  }

  getTotalPrice(): number {
    let totalPrice = 0;
    if (this.recipe && this.recipe.length > 0) {
      for (const recipeItem of this.recipe) {
        totalPrice += recipeItem.price;
      }
    }
    return Number(totalPrice.toFixed(2));
  }

  addFields() {
    const diff = this.numOfPeople - this.people.length;

    if (this.numOfPeople === 1) {
      this.people = [];
    } else if (diff > 1) {
      for (let i = 1; i < diff; i++) {
        this.people.push({ age: null, weight: null, height: null });
      }
    } else if (diff < 1) {
      this.people.splice(this.numOfPeople);
    }
  }
  likedFoods = new FormControl('');
  likedFoodsList: string[] = [
    'Pizza',
    'Burger',
    'Sushi',
    'Pasta',
    'Salad',
    'Ice Cream',
  ];

  dislikedFoods = new FormControl('');
  dislikedFoodsList: string[] = [
    'Anchovies',
    'Olives',
    'Cilantro',
    'Blue Cheese',
    'Liver',
    'Tofu',
  ];

  Cuisines = new FormControl('');
  CuisinesList: string[] = [
    'Italian',
    'Mexican',
    'Japanese',
    'Indian',
    'Greek',
    'Chinese',
  ];
  changeUnit(): void {
    // Logic for handling unit change
    if (this.selectedUnit === 'metric') {
      // Perform actions specific to Metric units
      console.log('Metric units selected');
    } else if (this.selectedUnit === 'imperial') {
      // Perform actions specific to Imperial units
      console.log('Imperial units selected');
    }
  }
}
