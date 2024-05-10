import { FormControl, FormGroup } from '@angular/forms';
import {
  Unit,
  ActivityLevel,
  Gender,
  Vegetarian,
  HealthGoal,
  Religious,
} from './interfaces';

export const units: Unit[] = [
  { value: 'metric', viewValue: 'Metric' },
  { value: 'imperial', viewValue: 'Imperial' },
];

export const activityLevels: ActivityLevel[] = [
  { value: 'Sedentary', viewValue: 'Sedentary' },
  { value: 'Low_Active', viewValue: 'Light' },
  { value: 'Active', viewValue: 'Moderate' },
  { value: 'Very_Active', viewValue: 'Heavy' },
];

export const genders: Gender[] = [
  { value: 'Male', viewValue: 'Male' },
  { value: 'Female', viewValue: 'Female' },
  { value: 'Female', viewValue: 'Other' },
];

export const vegetarians: Vegetarian[] = [
  { value: 'none', viewValue: 'None' },
  { value: 'vegetarian', viewValue: 'Vegetarian' },
  { value: 'vegan', viewValue: 'Vegan' },
  { value: 'pescatarian', viewValue: 'Pescatarian' },
];

export const healthGoals: HealthGoal[] = [
  { value: 'fight_cancer', viewValue: 'Fight Cancer' },
  { value: 'fight_heart_disease', viewValue: 'Fight Heart Disease' },
  { value: 'fight_diabetes', viewValue: 'Fight Diabetes' },
  { value: 'lose_weight', viewValue: 'Lose Weight' },
  { value: 'sports_build_muscle', viewValue: 'Build Muscle' },
];

export const religiousConstraints: Religious[] = [
  { value: 'none', viewValue: 'None' },
  { value: 'halal', viewValue: 'Halal' },
  { value: 'kosher', viewValue: 'Kosher' },
];

export const likedFoodsList = [
  'Pizza',
  'Burger',
  'Sushi',
  'Pasta',
  'Salad',
  'Ice Cream',
];

export const dislikedFoodsList = [
  'Anchovies',
  'Olives',
  'Cilantro',
  'Blue Cheese',
  'Liver',
  'Tofu',
];

export const cuisinesList = [
  'American',
  'Italian',
  'Mexican',
  'Japanese',
  'Indian',
  'Greek',
  'Chinese',
];

export const allergiesList = [
  'Dairy',
  'Egg',
  'Gluten',
  'Grain',
  'Peanut',
  'Seafood',
  'Sesame',
  'Shellfish',
  'Soy',
  'Sulfite',
  'Tree Nut',
  'Wheat',
];

const today = new Date();
const tomorrow = today.getDate() + 1;
const weekFromTomorrow = today.getDate() + 8;

const month = today.getMonth();
const year = today.getFullYear();
const day = today.getDate() + 1;
const weekLaterDay = today.getDate() + 7;

export const startDate = new FormGroup({
  start: new FormControl(new Date(year, month, tomorrow)),
  end: new FormControl(new Date(year, month, weekFromTomorrow)),
});
export const endDate = new FormGroup({
  start: new FormControl(new Date(year, month, 15)),
  end: new FormControl(new Date(year, month, 19)),
});
