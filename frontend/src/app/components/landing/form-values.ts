import { FormControl, FormGroup } from '@angular/forms';
import {
  Unit,
  ActivityLevel,
  Gender,
  Vegetarian,
  HealthGoal,
  Religious,
  Allergy,
  LikedFood,
  DislikedFood,
  Cuisine,
  Breakfast,
  Snack,
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
  // { value: 'Female', viewValue: 'Other' },
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

export const likedFoodsList: LikedFood[] = [
  { value: 'pizza', viewValue: 'Pizza' },
  { value: 'burger', viewValue: 'Burgers' },
  { value: 'sushi', viewValue: 'Sushi' },
  { value: 'pasta', viewValue: 'Pasta' },
  { value: 'salad', viewValue: 'Salads' },
];

export const dislikedFoodsList: DislikedFood[] = [
  { value: 'anchovies', viewValue: 'Anchovies' },
  { value: 'olive', viewValue: 'Olives' },
  { value: 'cilantro', viewValue: 'Cilantro' },
  { value: 'blue cheese', viewValue: 'Blue Cheese' },
  { value: 'liver', viewValue: 'Liver' },
  { value: 'tofu', viewValue: 'Tofu' },
];

export const cuisinesList: Cuisine[] = [
  { value: 'american', viewValue: 'American' },
  { value: 'chinese', viewValue: 'Chinese' },
  { value: 'japanese', viewValue: 'Japanese' },
  { value: 'korean', viewValue: 'Korean' },
  { value: 'french', viewValue: 'French' },
  { value: 'italian', viewValue: 'Italian' },
  { value: 'mexican', viewValue: 'Mexican' },
];

export const allergiesList: Allergy[] = [
  { value: 'dairy', viewValue: 'Dairy' },
  { value: 'egg', viewValue: 'Eggs' },
  { value: 'gluten', viewValue: 'Gluten' },
  { value: 'grain', viewValue: 'Grain' },
  { value: 'peanut', viewValue: 'Peanut' },
  { value: 'seafood', viewValue: 'Seafood' },
  { value: 'sesame', viewValue: 'Sesame' },
  { value: 'shellfish', viewValue: 'Shellfish' },
  { value: 'soy', viewValue: 'Soy' },
  { value: 'sulfite', viewValue: 'Sulfite' },
  { value: 'tree nut', viewValue: 'Tree Nuts' },
  { value: 'wheat', viewValue: 'Wheat' },
];

export const breakfastList: Breakfast[] = [
  { value: 'bagel', viewValue: 'Bagels' },
  { value: 'cereal', viewValue: 'Cereal' },
  { value: 'coffee', viewValue: 'Coffee' },
  { value: 'cream of wheat', viewValue: 'Cream of Wheat' },
  { value: 'hashbrown', viewValue: 'Hashbrowns' },
  { value: 'juice', viewValue: 'Juice' },
  { value: 'oatmeal', viewValue: 'Oatmeal' },
  { value: 'pancake', viewValue: 'Pancakes' },
  { value: 'toast', viewValue: 'Toast' },
  { value: 'waffle', viewValue: 'Waffles' },
];

export const snackList: Snack[] = [
  { value: 'berries', viewValue: 'Berries' },
  { value: 'cracker', viewValue: 'Crackers' },
  { value: 'dried fruit', viewValue: 'Dried Fruit' },
  { value: 'fruit', viewValue: 'Fruit' },
  { value: 'nut', viewValue: 'Nuts' },
  { value: 'snack bar', viewValue: 'Snack Bars' },
  { value: 'trail mix', viewValue: 'Trail Mix' },
  { value: 'veggies and dips', viewValue: 'Veggies & Dip' },
  { value: 'yogurt', viewValue: 'Yohgurt' },
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
  end: new FormControl(new Date(year, month, tomorrow)),
});
export const endDate = new FormGroup({
  start: new FormControl(new Date(year, month, 15)),
  end: new FormControl(new Date(year, month, 19)),
});
