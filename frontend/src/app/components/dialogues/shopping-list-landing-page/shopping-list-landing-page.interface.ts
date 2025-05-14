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

export const UNIT_HIERARCHY: { [normalizedUnit: string]: number } = {
  cup: 4,
  tablespoon: 3,
  teaspoon: 2,
  pinch: 1,
  // Units not in this hierarchy (e.g., 'bag', 'clove', 'item', 'piece')
  // are treated as non-convertible by this specific logic path.
};

export const UNIT_CONVERSION_TO_TEASPOONS: {
  [normalizedUnit: string]: number;
} = {
  teaspoon: 1,
  tablespoon: 3, // 3 teaspoons in 1 tablespoon
  cup: 48, // 16 tablespoons in a cup * 3 tsp/tbsp = 48 tsp
  pinch: 1 / 16, // An approximation for a pinch (can be adjusted)
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
  pinches: 'pinch',

  // Countable units (map them to a consistent "countable" identifier or themselves)
  each: 'each',
  piece: 'piece',
  pieces: 'piece',
  unit: 'unit',
  units: 'unit',
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

  countable: { 
    totalCount: number;
    entryCount: number;
  };
  
  nonSummableOther: Array<{ quantity: string | number; unit?: string }>; 
  totalOriginalEntryCount: number;
}

