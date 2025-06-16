export interface ProfileUser {
  uid?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  displayName?: string;
  phone?: string;
  address?: string;
  photoURL?: string;
  gender?: string;
  age?: number;
  weight?: number;
  height?: number;
  selectedUnit?: string;
  activityLevel?: string;
  likedFoods?: string[];
  dislikedFoods?: string[];
  favouriteCuisines?: string[];
  allergies?: string[];
  religiousConstraint?: string;
  dietaryConstraint?: string;
}
