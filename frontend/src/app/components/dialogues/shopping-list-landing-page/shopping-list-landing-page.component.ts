import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  ShoppingList,
  ProcessedShoppingItem,
  UNIT_HIERARCHY,
  UNIT_CONVERSION_TO_TEASPOONS,
  UNIT_NORMALIZATION_MAP,
  AggregationWorkData,
} from './shopping-list-landing-page.interface';

@Component({
  selector: 'app-shopping-list-landing-page',
  templateUrl: './shopping-list-landing-page.component.html',
  styleUrls: ['./shopping-list-landing-page.component.css'],
})
export class ShoppingListLandingPageComponent implements OnInit {
  data: {
    shoppingListData: ShoppingList[];
    minDate: string;
    maxDate: string;
  };

  categorizedShoppingList: Map<string, ProcessedShoppingItem[]> = new Map();
  orderedCategories: string[] = [];

  private readonly CATEGORY = [
    'Produce',
    'Meat Department',
    'Seafood',
    'Dairy',
    'Baking Aisle',
    'Baked Goods',
    'Junk Food',
    'Breakfast Aisle',
    'Frozen Food',
    'Canned Food',
    'Pasta',
    'Cooler',
    'Seasoning/Spices/Sauces',
    'Other',
  ];

  constructor(@Inject(MAT_DIALOG_DATA) private dialogData: any) {
    this.data = dialogData;
  }

  ngOnInit(): void {
    if (
      this.data &&
      this.data.shoppingListData &&
      this.data.shoppingListData.length > 0
    ) {
      console.log(
        'Processing shopping lists for dates:',
        this.data.shoppingListData.map((sl) => sl.date)
      );
      this.processAndCategorizeShoppingList();
    } else {
      console.log('Shopping list data is empty or not in the expected format.');
      // Ensure data is initialized to avoid errors in template
      this.data = { shoppingListData: [], minDate: '', maxDate: '' };
    }
  }

  private normalizeUnit(unitStr?: string): string | null {
    if (!unitStr) return null;
    const lowerUnit = unitStr.toLowerCase().trim();
    return UNIT_NORMALIZATION_MAP[lowerUnit] || lowerUnit;
  }

  private determineCategory(itemName: string): string {
    const lowerItemName = itemName.toLowerCase().trim();
    for (const category of this.CATEGORY) {
      if (category === 'Other') continue;
      const keywords = this.categoryKeywords[category];
      if (keywords) {
        if (
          keywords.some(
            (keyword) => keyword.toLowerCase().trim() === lowerItemName
          )
        ) {
          return category;
        }
      }
    }
    for (const category in this.categoryKeywords) {
      if (this.CATEGORY.includes(category) && category !== 'Other') continue;
      const keywords = this.categoryKeywords[category];
      if (keywords) {
        if (
          keywords.some(
            (keyword) => keyword.toLowerCase().trim() === lowerItemName
          )
        ) {
          return category;
        }
      }
    }
    return 'Other';
  }

  private parseQuantity(qty: string | number): number | null {
    if (typeof qty === 'number') return qty;
    if (typeof qty === 'string') {
      const trimmedQty = qty.trim();
      // Try direct parse for simple numbers like "2", "0.5"
      const num = parseFloat(trimmedQty);
      if (!isNaN(num) && isFinite(num) && num.toString() === trimmedQty) {
        return num;
      }
      // Try fraction "a/b" or "a b/c" (e.g. "1 1/2")
      const fractionMatch = trimmedQty.match(/^(\d+)\s+(\d+)\/(\d+)$/);
      if (fractionMatch) {
        const whole = parseInt(fractionMatch[1], 10);
        const numerator = parseInt(fractionMatch[2], 10);
        const denominator = parseInt(fractionMatch[3], 10);
        if (
          !isNaN(whole) &&
          !isNaN(numerator) &&
          !isNaN(denominator) &&
          denominator !== 0
        ) {
          return whole + numerator / denominator;
        }
      } else {
        const simpleFractionMatch = trimmedQty.match(/^(\d+)\/(\d+)$/);
        if (simpleFractionMatch) {
          const numerator = parseInt(simpleFractionMatch[1], 10);
          const denominator = parseInt(simpleFractionMatch[2], 10);
          if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
            return numerator / denominator;
          }
        }
      }
    }
    return null; // Cannot parse
  }

  private formatNumberForDisplay(num: number): string {
    if (num === Math.floor(num)) {
      // Whole number
      return num.toString();
    }
    // Check for common fractions to display them nicely
    if (Math.abs(num - 0.25) < 1e-5) return '0.25';
    if (Math.abs(num - 0.5) < 1e-5) return '0.5';
    if (Math.abs(num - 0.75) < 1e-5) return '0.75';
    if (Math.abs(num - 0.33) < 1e-2 || Math.abs(num - 0.333) < 1e-3)
      return '0.33'; // Approx 1/3
    if (Math.abs(num - 0.66) < 1e-2 || Math.abs(num - 0.666) < 1e-3)
      return '0.67'; // Approx 2/3

    // Otherwise, round to 2 decimal places if not whole
    return parseFloat(num.toFixed(2)).toString();
  }

  private aggregateItems(
    rawItems: {
      name: string;
      quantity: string | number;
      unit?: string;
      category: string;
    }[]
  ): ProcessedShoppingItem[] {
    const aggregationMap = new Map<string, AggregationWorkData>();

    rawItems.forEach((item) => {
      // ... (existing logic for populating aggregationMap - no changes here) ...
      // (This part is from your previous correct version)
      const itemKey = `${item.category}_${item.name.toLowerCase().trim()}`;

      if (!aggregationMap.has(itemKey)) {
        aggregationMap.set(itemKey, {
          name: item.name,
          category: item.category,
          summableVolume: {
            totalInTeaspoons: 0,
            largestUnitNormalized: null,
            largestUnitHierarchyValue: -1,
            entryCount: 0,
          },
          countable: {
            totalCount: 0,
            entryCount: 0,
          },
          nonSummableOther: [],
          totalOriginalEntryCount: 0,
        });
      }
      const aggData = aggregationMap.get(itemKey)!;
      aggData.totalOriginalEntryCount++;

      const numQuantity = this.parseQuantity(item.quantity);
      const normalizedUnit = this.normalizeUnit(item.unit);

      const isVolumeUnit =
        normalizedUnit !== null &&
        UNIT_HIERARCHY.hasOwnProperty(normalizedUnit) &&
        UNIT_CONVERSION_TO_TEASPOONS.hasOwnProperty(normalizedUnit);

      const countableUnits = ['each', 'piece', 'unit'];
      const isCountable =
        numQuantity !== null &&
        !isVolumeUnit &&
        (normalizedUnit === null || countableUnits.includes(normalizedUnit));

      if (isVolumeUnit && numQuantity !== null) {
        aggData.summableVolume.entryCount++;
        const quantityInTeaspoons =
          numQuantity * UNIT_CONVERSION_TO_TEASPOONS[normalizedUnit!];
        aggData.summableVolume.totalInTeaspoons += quantityInTeaspoons;
        const currentUnitHierarchyValue = UNIT_HIERARCHY[normalizedUnit!];
        if (
          currentUnitHierarchyValue >
          aggData.summableVolume.largestUnitHierarchyValue
        ) {
          aggData.summableVolume.largestUnitHierarchyValue =
            currentUnitHierarchyValue;
          aggData.summableVolume.largestUnitNormalized = normalizedUnit;
        }
      } else if (isCountable) {
        aggData.countable.entryCount++;
        aggData.countable.totalCount += numQuantity!;
      } else {
        aggData.nonSummableOther.push({
          quantity: item.quantity,
          unit: item.unit,
        });
      }
    });

    // --- Format for display ---
    const finalProcessedItems: ProcessedShoppingItem[] = [];
    aggregationMap.forEach((aggData) => {
      const displayParts: string[] = [];
      const needsPrefixOverall = aggData.totalOriginalEntryCount > 1;
      let primaryUnitForDisplay = '';

      let itemEffectiveNumericQuantity = 0; // To store the primary quantity for pluralization check
      let isPrimaryQuantityDetermined = false;

      // --- 1. Process Countable Part ---
      if (aggData.countable.entryCount > 0) {
        itemEffectiveNumericQuantity = aggData.countable.totalCount;
        isPrimaryQuantityDetermined = true;
        let countableStr = itemEffectiveNumericQuantity.toString();
        if (needsPrefixOverall) {
          countableStr = `> ${countableStr}`;
        }
        displayParts.push(countableStr);
      }

      // --- 2. Process Summable Volume Part ---
      if (
        aggData.countable.entryCount === 0 &&
        aggData.summableVolume.entryCount > 0 &&
        aggData.summableVolume.largestUnitNormalized
      ) {
        const needsPrefixForSummableVolume =
          aggData.summableVolume.entryCount > 1;
        const displayTargetUnitNorm =
          aggData.summableVolume.largestUnitNormalized;
        const teaspoonsPerDisplayTargetUnit =
          UNIT_CONVERSION_TO_TEASPOONS[displayTargetUnitNorm];

        if (teaspoonsPerDisplayTargetUnit > 0) {
          // Avoid division by zero
          let quantityInDisplayTargetUnit =
            aggData.summableVolume.totalInTeaspoons /
            teaspoonsPerDisplayTargetUnit;
          itemEffectiveNumericQuantity = quantityInDisplayTargetUnit; // Store for pluralization
          isPrimaryQuantityDetermined = true;

          let finalDisplayNumStr = this.formatNumberForDisplay(
            quantityInDisplayTargetUnit
          );
          const numericValueForPlural = parseFloat(finalDisplayNumStr); // Use for pluralizing unit
          const unitStr =
            Math.abs(numericValueForPlural - 1) < 1e-5
              ? displayTargetUnitNorm
              : displayTargetUnitNorm === 'pinch'
              ? 'pinches'
              : displayTargetUnitNorm + 's';

          let summablePartStr = `${finalDisplayNumStr} ${unitStr}`;
          if (
            needsPrefixForSummableVolume ||
            (needsPrefixOverall &&
              aggData.summableVolume.entryCount === 1 &&
              aggData.nonSummableOther.length > 0)
          ) {
            summablePartStr = `> ${summablePartStr}`;
          }
          displayParts.push(summablePartStr);
          if (!primaryUnitForDisplay) primaryUnitForDisplay = unitStr;
        } else {
          displayParts.push(
            `${this.formatNumberForDisplay(
              aggData.summableVolume.totalInTeaspoons
            )} tsp (conv. error)`
          );
        }
      }

      // --- 3. Process Non-Summable Other Part ---
      if (
        aggData.countable.entryCount === 0 &&
        aggData.summableVolume.entryCount === 0
      ) {
        aggData.nonSummableOther.forEach((nsEntry, index) => {
          // Try to parse quantity for non-summable to check for pluralization, if it's simple number
          if (!isPrimaryQuantityDetermined && index === 0) {
            // Only for the first non-summable part
            const nsNumQty = this.parseQuantity(nsEntry.quantity);
            if (nsNumQty !== null) {
              itemEffectiveNumericQuantity = nsNumQty;
              isPrimaryQuantityDetermined = true;
            }
          }
          let nsPart = `${nsEntry.quantity} ${nsEntry.unit || ''}`.trim();
          if (nsPart) {
            if (needsPrefixOverall && index === 0) {
              nsPart = `> ${nsPart}`;
            }
            displayParts.push(nsPart);
          }
          if (!primaryUnitForDisplay && nsEntry.unit)
            primaryUnitForDisplay = nsEntry.unit;
        });
      } else if (
        aggData.nonSummableOther.length > 0 &&
        (aggData.countable.entryCount > 0 ||
          aggData.summableVolume.entryCount > 0)
      ) {
        aggData.nonSummableOther.forEach((nsEntry) => {
          let nsPart = `${nsEntry.quantity} ${nsEntry.unit || ''}`.trim();
          if (nsPart) displayParts.push(nsPart);
        });
      }

      let finalQuantityString = displayParts.join(', ');

      // Fallback quantity string if empty
      if (!finalQuantityString && aggData.totalOriginalEntryCount > 0) {
        finalQuantityString = needsPrefixOverall
          ? '> (No valid quantity)'
          : '(No valid quantity)';
      } else if (
        isPrimaryQuantityDetermined &&
        itemEffectiveNumericQuantity < 1e-5 && // Effectively zero
        displayParts.length === 1 &&
        displayParts[0].startsWith('0 ')
      ) {
        // And shows "0 [unit]"
        // This case was for showing "0 cups" etc. if sum was 0.
        // It might conflict with pluralization logic if itemEffectiveNumericQuantity is 0.
        // The pluralization check `itemEffectiveNumericQuantity - 1 > 1e-5` will handle it.
      }

      // --- Pluralize Item Name ---
      let finalItemName = aggData.name;
      if (
        isPrimaryQuantityDetermined &&
        itemEffectiveNumericQuantity - 1 > 1e-5
      ) {
        // quantity is greater than 1 (with tolerance)
        const lowerName = aggData.name.toLowerCase();
        if (!lowerName.endsWith('(s)') && !lowerName.endsWith('s')) {
          finalItemName += '(s)';
        }
        // If it ends with 's' (like "apples") or "(s)", we don't add another "(s)".
      }

      finalProcessedItems.push({
        name: finalItemName, // Use potentially pluralized name
        category: aggData.category,
        quantity:
          finalQuantityString ||
          (aggData.totalOriginalEntryCount > 0 ? '(No quantity)' : '0'),
        unit: primaryUnitForDisplay,
      });
    });
    return finalProcessedItems;
  }

  private processAndCategorizeShoppingList(): void {
    let allItems: ProcessedShoppingItem[] = [];

    this.data.shoppingListData.forEach((dailyList) => {
      dailyList['shopping-list'].forEach((item) => {
        allItems.push({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          category: this.determineCategory(item.name),
        });
      });
    });

    // 2. Aggregate items (sum quantities for identical items)
    const aggregatedItems = this.aggregateItems(allItems);

    // 3. Group aggregated items by category for display
    this.categorizedShoppingList.clear();
    aggregatedItems.forEach((item) => {
      const itemsInCategory =
        this.categorizedShoppingList.get(item.category) || [];
      itemsInCategory.push(item);
      this.categorizedShoppingList.set(item.category, itemsInCategory);
    });

    // Sort items within each category alphabetically by name
    this.categorizedShoppingList.forEach((items) => {
      items.sort((a, b) => a.name.localeCompare(b.name));
    });

    // Determine the order of categories for display
    const presentCategories = Array.from(this.categorizedShoppingList.keys());
    this.orderedCategories = this.CATEGORY.filter((cat) =>
      presentCategories.includes(cat)
    );
    const remainingCategories = presentCategories
      .filter((cat) => !this.CATEGORY.includes(cat))
      .sort();
    this.orderedCategories.push(...remainingCategories);

    console.log('Categorized Shopping List:', this.categorizedShoppingList);
    console.log('Ordered Categories:', this.orderedCategories);
  }

  // Helper function for the template to get categories in the desired order
  public getCategories(): string[] {
    return this.orderedCategories;
  }

  private readonly categoryKeywords: { [key: string]: string[] } = {
    Produce: [
      'acorn squash',
      'apple',
      'apples',
      'arugula',
      'asparagus',
      'avocado',
      'baby bok choy',
      'baby spinach',
      'basil leaves',
      'bell pepper',
      'berries',
      'bok choy',
      'broccoli',
      'butternut squash',
      'cabbage',
      'carrot',
      'carrots',
      'cauliflower',
      'celery',
      'cherry tomatoes',
      'cilantro',
      'cucumber',
      'daikon radish',
      'eggplant',
      'fennel bulb',
      'fresh thyme',
      'garlic',
      'ginger',
      'green beans',
      'green bell pepper',
      'green onion',
      'herb',
      'herbs',
      'jalapeno',
      'kale',
      'leek',
      'lemon',
      'lettuce',
      'lime',
      'mushroom',
      'napa cabbage',
      'onion',
      'parsley',
      'pepper',
      'potato',
      'radishes',
      'roma tomatoes',
      'scallions',
      'spinach',
      'sweet potato',
      'tomato',
      'turnip',
      'zucchini',
    ],
    'Meat Department': [
      'bacon',
      'beef',
      'chicken',
      'chicken breast',
      'chicken breast half',
      'chicken thighs',
      'ground beef',
      'ham',
      'lamb',
      'pork',
      'pork belly',
      'sausage',
      'steak',
      'turkey',
    ],
    Seafood: [
      'anchovies',
      'calamari',
      'clams',
      'cod',
      'crabmeat',
      'fish',
      'mussels',
      'salmon',
      'scallops',
      'shrimp',
      'tuna',
    ],
    Dairy: [
      'butter',
      'cheddar cheese',
      'cream cheese',
      'feta cheese',
      'greek yogurt',
      'heavy whipping cream',
      'mexican cheese',
      'milk',
      'mozzarella cheese',
      'parmesan cheese',
      'ricotta cheese',
      'sour cream',
      'yogurt',
    ],
    'Baking Aisle': [
      'all-purpose flour',
      'purpose flour',
      'baking powder',
      'baking soda',
      'brown sugar',
      'cocoa powder',
      'confectioner sugar',
      'cornstarch',
      'flour',
      'granulated sugar',
      'salt',
      'sea salt',
      'vanilla extract',
      'white sugar',
      'yeast',
    ],
    'Baked Goods': [
      'bagel',
      'baguette',
      'bread',
      'ciabatta bread',
      'corn tortillas',
      'flour tortilla',
      'naan',
      'pita bread',
      'wonton wrappers',
    ],
    'Junk Food': ['coke classic', 'chips', 'soda', 'soft drink', 'sprite'],
    'Breakfast Aisle': [
      'cereal',
      'granola',
      'oatmeal',
      'pancake mix',
      'waffles',
    ],
    'Frozen Food': [
      'frozen corn',
      'frozen peas',
      'frozen spinach',
      'frozen berries',
      'ice cream',
    ],
    'Canned Food': [
      'canned beans',
      'canned tomatoes',
      'canned tuna',
      'soup',
      'tomato paste',
    ],
    Pasta: [
      'fettuccine',
      'lasagna noodles',
      'pasta',
      'ramen noodles',
      'spaghetti',
    ],
    Cooler: ['egg', 'egg white', 'eggs', 'hard-boiled eggs'],
    'Seasoning/Spices/Sauces': [
      'adobo sauce',
      'balsamic glaze',
      'barbecue sauce',
      'black pepper',
      'buffalo sauce',
      'cajun seasoning',
      'caesar dressing',
      'caraway seed',
      'chili flakes',
      'chili garlic sauce',
      'chili oil',
      'chili powder',
      'cinnamon',
      'coriander',
      'cumin',
      'curry powder',
      'dijon mustard',
      'enchilada sauce',
      'fennel seed',
      'fish sauce',
      'garlic powder',
      'gochujang',
      'hoisin sauce',
      'hot sauce',
      'italian seasoning',
      'ketchup',
      'marinara sauce',
      'mayonnaise',
      'mustard',
      'nutritional yeast',
      'old bay seasoning',
      'olive oil',
      'oregano',
      'oyster sauce',
      'paprika',
      'pepper',
      'red pepper flake',
      'salsa',
      'salt',
      'salt pepper',
      'sesame oil',
      'soy sauce',
      'sriracha',
      'taco seasoning',
      'tamarind paste',
      'thyme',
      'tomato paste',
      'turmeric',
      'vanilla extract',
      'vinegar',
      'white vinegar',
      'wasabi paste',
      'worcestershire sauce',
      'balsamic vinegar',
      'apple cider vinegar',
      'rice vinegar',
      'chili oil',
      'toasted sesame oil',
      'coconut oil',
      'neutral oil',
      'vegetable oil',
      'canola oil',
      'avocado oil',
    ],
  };
}
