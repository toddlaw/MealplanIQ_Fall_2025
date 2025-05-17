export interface ShoppingList {
  date: string;
  'shopping-list': {
    name: string;
    quantity: string;
    unit: string;
  }[];
}

export interface ProcessedShoppingItem {
  name: string;
  quantity: string | number;
  unit: string;
  category: string;
}

export const VOLUME_UNIT_HIERARCHY: { [normalizedUnit: string]: number } = {
  cup: 4,
  tablespoon: 3,
  teaspoon: 2,
  pinch: 1,
};

export const VOLUME_UNIT_CONVERSION_TO_TEASPOONS: {
  [normalizedUnit: string]: number;
} = {
  teaspoon: 1,
  tablespoon: 3, // 3 teaspoons in 1 tablespoon
  cup: 48, // 16 tablespoons in a cup * 3 tsp/tbsp = 48 tsp
  pinch: 1 / 16, // An approximation for a pinch (can be adjusted)
};

export const WEIGHT_UNIT_HIERARCHY: { [normalizedUnit: string]: number } = {
  pound: 2,
  ounce: 1,
};

export const WEIGHT_UNIT_CONVERSION_TO_OUNCES: {
  [normalizedUnit: string]: number;
} = {
  ounce: 1,
  pound: 16,
};

export const DENSITY_OUNCES_PER_CUP: { [itemName: string]: number } = {
  'flour': 4.25,
  'all-purpose flour': 4.25,
  'purpose flour': 4.25,
  'self-rising flour': 4.0,
  'bread flour': 4.5,
  'whole wheat flour': 4.0,
  'wheat flour': 4.0,
  'white flour': 4.25,
  'cake flour': 3.9,
  'sugar': 7.0,
  'granulated sugar': 7.0,
  'brown sugar': 7.5,
  'white sugar': 7.0,
  'powdered sugar': 4.0,
  'confectioner sugar': 4.0,
};

export const UNIT_NORMALIZATION_MAP: { [unit: string]: string } = {
  teaspoon: 'teaspoon',
  teaspoons: 'teaspoon',
  tsp: 'teaspoon',
  t: 'teaspoon',
  tablespoon: 'tablespoon',
  tablespoons: 'tablespoon',
  tbsp: 'tablespoon',
  T: 'tablespoon',
  tbls: 'tablespoon',
  cup: 'cup',
  cups: 'cup',
  c: 'cup',
  pinch: 'pinch',
  pinches: 'pinch', // Normalized to 'pinch'

  ounce: 'ounce',
  ounces: 'ounce',
  oz: 'ounce',
  pound: 'pound',
  pounds: 'pound',
  lb: 'pound',
  lbs: 'pound',

  each: 'each',
  piece: 'piece',
  pieces: 'piece', // Normalized to 'piece'
  unit: 'unit',
  units: 'unit', // Normalized to 'unit'
  cloves: 'clove', // Normalized to 'clove'
  clove: 'clove',
};

export interface AggregationWorkData {
  name: string;
  category: string;
  summableVolume: {
    totalInTeaspoons: number;
    largestUnitNormalized: string | null;
    largestUnitHierarchyValue: number;
    entryCount: number;
  };
  summableWeight: {
    totalInOunces: number;
    largestUnitNormalized: string | null;
    largestUnitHierarchyValue: number;
    entryCount: number;
  };
  countable: {
    totalCount: number;
    entryCount: number;
  };
  nonSummableOther: Array<{ quantity: string | number; unit?: string }>;
  totalOriginalEntryCount: number;
  isFlourOrSugar: boolean;
}
