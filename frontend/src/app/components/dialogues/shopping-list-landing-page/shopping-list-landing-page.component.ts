/**
 * Shopping List Landing Page Component
 * @author BCIT May 2025
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  ShoppingList,
  ProcessedShoppingItem,
  VOLUME_UNIT_HIERARCHY,
  VOLUME_UNIT_CONVERSION_TO_TEASPOONS,
  WEIGHT_UNIT_HIERARCHY,
  WEIGHT_UNIT_CONVERSION_TO_OUNCES,
  DENSITY_OUNCES_PER_CUP,
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
    'Deli',
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
      this.data = { shoppingListData: [], minDate: '', maxDate: '' };
    }
  }

  /**
   * Normalize the unit string to a standard format.
   * @param unitStr The unit string to normalize.
   * @returns The normalized unit string or null if not applicable.
   */
  private normalizeUnit(unitStr?: string): string | null {
    if (!unitStr) return null;
    const lowerUnit = unitStr.toLowerCase().trim();
    return UNIT_NORMALIZATION_MAP[lowerUnit] || lowerUnit;
  }

  /**
   * Determine the category of an item based on its name.
   * @param itemName The name of the item.
   * @returns The category of the item.
   * If no category matches, it returns 'Other'.
   */
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
    // If no category matched, return 'Other'
    return 'Other';
  }

  /**
   * Parse a quantity string or number into a number.
   * It supports fractions (e.g. "1/2", "1 1/2") and decimal numbers (e.g. "0.5").
   * @param qty The quantity to parse.
   * @returns The parsed number or null if parsing fails.
   */
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

  /**
   * Format a number for display, rounding to 2 decimal places if necessary.
   * @param num The number to format.
   * @returns The formatted string.
   */
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

  /**
   * Pluralize a unit based on the quantity.
   * @param unit The unit to pluralize.
   * @param quantity The quantity to check.
   * @returns The pluralized unit.
   */
  private pluralizeUnit(unit: string, quantity: number): string {
    if (Math.abs(quantity - 1) < 1e-5 || !unit) {
      return unit;
    }
    if (unit === 'pinch') return 'pinches';
    if (!unit.endsWith('s')) {
      return unit + 's';
    }
    return unit;
  }

  /**
   * For the flour and sugar types, we need to check if the item is one of them.
   * This is used to determine if we should convert volume to weight.
   * @param itemName String
   * @returns If the item is flour or sugar type
   * This can be extended to include other ingredients as needed.
   */
  private isFlourOrSugarType(itemName: string): boolean {
    const lowerItemName = itemName.toLowerCase();
    if (DENSITY_OUNCES_PER_CUP.hasOwnProperty(lowerItemName)) {
      return true;
    }
    const keywords = ['flour', 'sugar'];
    return keywords.some((keyword) => lowerItemName.includes(keyword));
  }

  /**
   * Aggregate items based on their name and category.
   * It combines quantities of the same item into a single entry.
   * @param rawItems The raw items to aggregate.
   * @returns An array of processed shopping items.
   */
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
      const lowerItemName = item.name.toLowerCase().trim();
      const itemKey = `${item.category}_${lowerItemName}`;
      const isFlourSugar = this.isFlourOrSugarType(lowerItemName);

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
          summableWeight: {
            totalInOunces: 0,
            largestUnitNormalized: null,
            largestUnitHierarchyValue: -1,
            entryCount: 0,
          },
          countable: { totalCount: 0, entryCount: 0 },
          nonSummableOther: [],
          totalOriginalEntryCount: 0,
          isFlourOrSugar: isFlourSugar,
        });
      }
      const aggData = aggregationMap.get(itemKey)!;
      aggData.totalOriginalEntryCount++;

      const numQuantity = this.parseQuantity(item.quantity);
      const normalizedUnit = this.normalizeUnit(item.unit);

      if (numQuantity === null) {
        aggData.nonSummableOther.push({
          quantity: item.quantity,
          unit: item.unit,
        });
        return;
      }

      // Check if the item is flour or sugar and if the unit is volume
      if (
        aggData.isFlourOrSugar &&
        normalizedUnit &&
        VOLUME_UNIT_CONVERSION_TO_TEASPOONS.hasOwnProperty(normalizedUnit) &&
        DENSITY_OUNCES_PER_CUP[lowerItemName]
      ) {
        aggData.summableWeight.entryCount++;
        const quantityInTeaspoons =
          numQuantity * VOLUME_UNIT_CONVERSION_TO_TEASPOONS[normalizedUnit];
        const quantityInCups =
          quantityInTeaspoons / VOLUME_UNIT_CONVERSION_TO_TEASPOONS['cup']; // Base conversion on cups
        const quantityInOunces =
          quantityInCups * DENSITY_OUNCES_PER_CUP[lowerItemName];
        aggData.summableWeight.totalInOunces += quantityInOunces;

        // Determine largest weight unit (oz or lb for now)
        if (
          aggData.summableWeight.totalInOunces >=
          WEIGHT_UNIT_CONVERSION_TO_OUNCES['pound']
        ) {
          if (
            !aggData.summableWeight.largestUnitNormalized ||
            WEIGHT_UNIT_HIERARCHY['pound'] >
              aggData.summableWeight.largestUnitHierarchyValue
          ) {
            aggData.summableWeight.largestUnitNormalized = 'pound';
            aggData.summableWeight.largestUnitHierarchyValue =
              WEIGHT_UNIT_HIERARCHY['pound'];
          }
        } else {
          // Default to ounce if less than a pound or if ounce is a "larger" unit than previously stored (e.g. if nothing was stored)
          if (
            !aggData.summableWeight.largestUnitNormalized ||
            WEIGHT_UNIT_HIERARCHY['ounce'] >
              aggData.summableWeight.largestUnitHierarchyValue
          ) {
            aggData.summableWeight.largestUnitNormalized = 'ounce';
            aggData.summableWeight.largestUnitHierarchyValue =
              WEIGHT_UNIT_HIERARCHY['ounce'];
          }
        }
      }

      // Standard Volume processing (if not primarily weight or if weight conversion failed for it)
      const isVolumeUnit =
        normalizedUnit !== null &&
        VOLUME_UNIT_HIERARCHY.hasOwnProperty(normalizedUnit) &&
        VOLUME_UNIT_CONVERSION_TO_TEASPOONS.hasOwnProperty(normalizedUnit);
      if (isVolumeUnit && !aggData.isFlourOrSugar) {
        // Process as volume if NOT flour/sugar that got converted
        aggData.summableVolume.entryCount++;
        const quantityInTeaspoons =
          numQuantity * VOLUME_UNIT_CONVERSION_TO_TEASPOONS[normalizedUnit!];
        aggData.summableVolume.totalInTeaspoons += quantityInTeaspoons;
        const currentUnitHierarchyValue =
          VOLUME_UNIT_HIERARCHY[normalizedUnit!];
        if (
          currentUnitHierarchyValue >
          aggData.summableVolume.largestUnitHierarchyValue
        ) {
          aggData.summableVolume.largestUnitHierarchyValue =
            currentUnitHierarchyValue;
          aggData.summableVolume.largestUnitNormalized = normalizedUnit;
        }
      }
      // Standard Weight processing (if item unit was oz/lb initially, or if flour/sugar was entered by weight)
      else if (
        normalizedUnit !== null &&
        WEIGHT_UNIT_HIERARCHY.hasOwnProperty(normalizedUnit) &&
        WEIGHT_UNIT_CONVERSION_TO_OUNCES.hasOwnProperty(normalizedUnit)
      ) {
        aggData.summableWeight.entryCount++;
        const quantityInOunces =
          numQuantity * WEIGHT_UNIT_CONVERSION_TO_OUNCES[normalizedUnit!];
        aggData.summableWeight.totalInOunces += quantityInOunces;
        const currentUnitHierarchyValue =
          WEIGHT_UNIT_HIERARCHY[normalizedUnit!];
        if (
          currentUnitHierarchyValue >
          aggData.summableWeight.largestUnitHierarchyValue
        ) {
          aggData.summableWeight.largestUnitHierarchyValue =
            currentUnitHierarchyValue;
          aggData.summableWeight.largestUnitNormalized = normalizedUnit;
        }
      }
      // Countable processing
      else {
        const countableUnits = ['each', 'piece', 'unit', 'clove'];
        const isCountable =
          !isVolumeUnit &&
          (normalizedUnit === null || countableUnits.includes(normalizedUnit));

        if (isCountable) {
          aggData.countable.entryCount++;
          aggData.countable.totalCount += numQuantity;
        } else if (normalizedUnit) {
          aggData.nonSummableOther.push({
            quantity: item.quantity,
            unit: item.unit,
          });
        } else {
          aggData.nonSummableOther.push({
            quantity: item.quantity,
            unit: item.unit,
          });
        }
      }
    });

    // --- Format for display ---
    const finalProcessedItems: ProcessedShoppingItem[] = [];
    aggregationMap.forEach((aggData) => {
      const displayParts: string[] = [];
      const needsPrefixOverall = aggData.totalOriginalEntryCount > 1;
      let primaryUnitForDisplay = '';
      let itemEffectiveNumericQuantity = 0;
      let unitToDisplay = '';

      // Priority: 1. Flour/Sugar as Weight, 2. Countable, 3. Other Weight, 4. Volume, 5. NonSummable
      if (
        aggData.isFlourOrSugar &&
        aggData.summableWeight.entryCount > 0 &&
        aggData.summableWeight.largestUnitNormalized
      ) {
        const targetWeightUnit = aggData.summableWeight.largestUnitNormalized;
        const conversionFactor =
          WEIGHT_UNIT_CONVERSION_TO_OUNCES[targetWeightUnit];
        let quantityInTargetUnit =
          aggData.summableWeight.totalInOunces / conversionFactor;

        itemEffectiveNumericQuantity = quantityInTargetUnit;
        let numStr = this.formatNumberForDisplay(quantityInTargetUnit);
        unitToDisplay = this.pluralizeUnit(
          targetWeightUnit,
          quantityInTargetUnit
        );
        let partStr = `${numStr} ${unitToDisplay}`;
        if (needsPrefixOverall) partStr = `~ ${partStr}`;
        displayParts.push(partStr);
        primaryUnitForDisplay = unitToDisplay;
      } else if (aggData.countable.entryCount > 0) {
        itemEffectiveNumericQuantity = aggData.countable.totalCount;
        let countableStr = this.formatNumberForDisplay(
          itemEffectiveNumericQuantity
        );
        unitToDisplay = '';

        const originalItemWithUnit = rawItems.find(
          (ri) =>
            ri.name.toLowerCase().trim() ===
              aggData.name.toLowerCase().trim() &&
            this.normalizeUnit(ri.unit) &&
            ['clove', 'piece'].includes(this.normalizeUnit(ri.unit)!)
        );

        if (originalItemWithUnit && originalItemWithUnit.unit) {
          const normalizedRawUnit = this.normalizeUnit(
            originalItemWithUnit.unit
          );
          if (normalizedRawUnit) {
            unitToDisplay = this.pluralizeUnit(
              normalizedRawUnit,
              itemEffectiveNumericQuantity
            );
            countableStr = `${countableStr} ${unitToDisplay}`;
          }
        }

        if (needsPrefixOverall && !countableStr.startsWith('~ ')) {
          countableStr = `~ ${countableStr}`;
        }
        displayParts.push(countableStr);
        primaryUnitForDisplay = unitToDisplay;
      } else if (
        aggData.summableWeight.entryCount > 0 &&
        aggData.summableWeight.largestUnitNormalized
      ) {
        const targetWeightUnit = aggData.summableWeight.largestUnitNormalized;
        const conversionFactor =
          WEIGHT_UNIT_CONVERSION_TO_OUNCES[targetWeightUnit];
        let quantityInTargetUnit =
          aggData.summableWeight.totalInOunces / conversionFactor;

        itemEffectiveNumericQuantity = quantityInTargetUnit;
        let numStr = this.formatNumberForDisplay(quantityInTargetUnit);
        unitToDisplay = this.pluralizeUnit(
          targetWeightUnit,
          quantityInTargetUnit
        );
        let partStr = `${numStr} ${unitToDisplay}`;
        if (needsPrefixOverall) partStr = `~ ${partStr}`;
        displayParts.push(partStr);
        primaryUnitForDisplay = unitToDisplay;
      } else if (
        aggData.summableVolume.entryCount > 0 &&
        aggData.summableVolume.largestUnitNormalized
      ) {
        const targetVolumeUnit = aggData.summableVolume.largestUnitNormalized;
        const conversionFactor =
          VOLUME_UNIT_CONVERSION_TO_TEASPOONS[targetVolumeUnit];
        let quantityInTargetUnit =
          aggData.summableVolume.totalInTeaspoons / conversionFactor;

        itemEffectiveNumericQuantity = quantityInTargetUnit;
        let numStr = this.formatNumberForDisplay(quantityInTargetUnit);
        unitToDisplay = this.pluralizeUnit(
          targetVolumeUnit,
          quantityInTargetUnit
        );

        let partStr = `${numStr} ${unitToDisplay}`;
        if (needsPrefixOverall) partStr = `~ ${partStr}`;
        displayParts.push(partStr);
        primaryUnitForDisplay = unitToDisplay;
      } else if (
        aggData.nonSummableOther.length > 0 &&
        displayParts.length === 0
      ) {
        aggData.nonSummableOther.forEach((nsEntry, index) => {
          const parsedNsQuantity = this.parseQuantity(nsEntry.quantity);
          if (index === 0 && parsedNsQuantity !== null) {
            itemEffectiveNumericQuantity = parsedNsQuantity;
          }
          unitToDisplay = '';
          if (nsEntry.unit) {
            const normalizedNsUnit = this.normalizeUnit(nsEntry.unit);
            if (normalizedNsUnit) {
              unitToDisplay = this.pluralizeUnit(
                normalizedNsUnit,
                parsedNsQuantity ?? 0
              );
            } else {
              unitToDisplay = nsEntry.unit;
            }
          }

          let nsPart = `${nsEntry.quantity} ${unitToDisplay}`.trim();
          if (nsPart) {
            if (needsPrefixOverall && index === 0) nsPart = `~ ${nsPart}`;
            displayParts.push(nsPart);
          }
          if (!primaryUnitForDisplay && unitToDisplay)
            primaryUnitForDisplay = unitToDisplay;
        });
      }

      const filteredDisplayParts = displayParts.filter(
        (part) => part.trim().toLowerCase() !== 'n/a'
      );
      let finalQuantityString = filteredDisplayParts.join(', ');

      if (!finalQuantityString && aggData.totalOriginalEntryCount > 0) {
        finalQuantityString = needsPrefixOverall
          ? '~ (No valid quantity)'
          : '(No valid quantity)';
      } else if (
        itemEffectiveNumericQuantity < 1e-5 &&
        filteredDisplayParts.length === 1 &&
        filteredDisplayParts[0].startsWith('0')
      ) {
        finalQuantityString = filteredDisplayParts[0].startsWith('~')
          ? '~ 0'
          : '0';
      }

      const finalItemName = aggData.name;
      finalProcessedItems.push({
        name: finalItemName.toLowerCase(),
        category: aggData.category,
        quantity:
          finalQuantityString ||
          (aggData.totalOriginalEntryCount > 0 ? '(No quantity)' : '0'),
        unit: primaryUnitForDisplay,
      });
    });
    return finalProcessedItems;
  }

  /**
   * Process the shopping list data and categorize items into a map.
   * It aggregates items by their name and category, and sorts them alphabetically.
   */
  private processAndCategorizeShoppingList(): void {
    let rawItemList: {
      name: string;
      quantity: string | number;
      unit?: string;
      category: string;
    }[] = [];

    this.data.shoppingListData.forEach((dailyList) => {
      dailyList['shopping-list'].forEach((item) => {
        const lowerName = item.name.toLowerCase().trim();
        // Water is a common ingredient, but we want to ignore it in the shopping list.
        // But we want to keep words that contain "water" in them, like "watermelon" and "watercress".
        if (
          lowerName === 'water' ||
          (lowerName.includes('water') &&
            !lowerName.includes('watermelon') &&
            !lowerName.includes('watercress') &&
            !lowerName.includes('water chestnut'))
        ) {
          console.log(`Ignoring item: ${item.name}`);
          return;
        }
        // Add the item into the raw item list.
        rawItemList.push({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          category: this.determineCategory(item.name),
        });
      });
    });

    const aggregatedItems = this.aggregateItems(rawItemList);

    this.categorizedShoppingList.clear();
    aggregatedItems.forEach((item) => {
      const itemsInCategory =
        this.categorizedShoppingList.get(item.category) || [];
      itemsInCategory.push(item);
      this.categorizedShoppingList.set(item.category, itemsInCategory);
    });

    this.categorizedShoppingList.forEach((items) => {
      items.sort((a, b) => a.name.localeCompare(b.name));
    });

    const presentCategories = Array.from(this.categorizedShoppingList.keys());
    this.orderedCategories = this.CATEGORY.filter((cat) =>
      presentCategories.includes(cat)
    );
    const remainingCategories = presentCategories
      .filter((cat) => !this.CATEGORY.includes(cat))
      .sort();
    this.orderedCategories.push(...remainingCategories);

    // console.log('Categorized Shopping List:', this.categorizedShoppingList);
    // console.log('Ordered Categories:', this.orderedCategories);
  }

  public getCategories(): string[] {
    return this.orderedCategories;
  }

  /**
   * Keywords for each category
   * The keys are the category names and the values are arrays of ingredients, which are given by sponsor.
   * Because the names of the ingredients are not standardized,and we have to add all the ingredients in the list. Otherwise, the ingredients will not be categorized correctly.
   * For example, "pepper" and "red pepper flakes" should be in different categories. If we don't use exact match, they will go to the same category, which is not what we want.
   */
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
      'banana',
      'basil leaves',
      'beet',
      'bell pepper',
      'berries',
      'bok choy',
      'broccoli',
      'butternut squash',
      'cabbage',
      'carrot',
      'carrots-medium',
      'carrots',
      'cauliflower',
      'Chopped cilantro',
      'chives',
      'cranberries',
      'cucumber',
      'celery',
      'celery stalks',
      'cherry tomatoes',
      'cilantro',
      'coconut',
      'corn',
      'cucumber',
      'daikon radish',
      'eggplant',
      'fennel bulb',
      'fresh parsley',
      'fresh asparagus',
      'fresh thyme',
      'garlic',
      'ginger',
      'ginger root',
      'green beans',
      'green bell pepper',
      'green onion',
      'green onions',
      'green pepper',
      'herb',
      'herbs',
      'jalapeno',
      'jalapeno pepper - small',
      'red bell pepper - medium',
      'red onion',
      'kale',
      'leek',
      'lemon',
      'lettuce',
      'lime',
      'lime wedges',
      'mango',
      'mushroom',
      'napa cabbage',
      'onion',
      'orange',
      'parsley',
      'pepper',
      'pineapple',
      'potato',
      'radishes',
      'roma tomatoes',
      'scallions',
      'spinach',
      'strawberries',
      'sweet potato',
      'tomato',
      'turnip',
      'white onion',
      'white onion - large',
      'yellow onions',
      'zucchini',
    ],
    'Meat Department': [
      'bacon',
      'beef',
      'boneless pork shoulder',
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
      'sardines',
      'scallops',
      'shrimp',
      'tuna',
    ],
    Dairy: [
      'butter',
      'buttermilk',
      'cottage cheese',
      'cheddar cheese',
      'cream cheese',
      'feta cheese',
      'greek yogurt',
      'heavy whipping cream',
      'mexican cheese',
      'milk',
      'mozzarella cheese',
      'cheese',
      'parmesan cheese',
      'ricotta cheese',
      'swiss cheese',
      'whipping cream',
      'gruyere cheese',
      'sour cream',
      'yogurt',
      'parmesan cheese - shredded',
    ],
    Deli: [
      'ham',
      'cooked ham',
      'prosciutto slices',
      'prosciutto',
      'pepperoni',
      'turkey',
      'sliced turkey breast',
      'italian sausage',
      'smoked sausage',
      'beef brisket',
      'queso fresco',
      'coleslaw',
      'dill pickles',
      'pickled jalapenos',
      'black olives',
      'green olives',
      'pasta salad',
      'assorted meats',
      'hard-boiled eggs',
      'hummus',
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
      'grated parmesan cheese',
      'molasses',
      'salt',
      'sea salt',
      'self rising flour',
      'sugar',
      'vanilla extract',
      'wheat flour',
      'white sugar',
      'yeast',
      'clove',
      'almond extract',
      'cornmeal',
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
      'whole wheat bread',
      'whole grain bread',
      'ciabatta bread',
      'wonton wrappers',
      'sourdough bread',
    ],
    'Junk Food': [
      'coke classic',
      'chips',
      'soda',
      'soft drink',
      'sprite',
      'crackers',
      'graham crackers',
      'chocolate chips',
      'chocolate chip',
      'dark chocolate chips',
      'lime juice',
      'dried cranberries',
      'dried fruit',
      'dried apricots',
    ],
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
      'cream mushroom soup',
    ],
    Pasta: [
      'fettuccine',
      'lasagna noodles',
      'pasta',
      'ramen noodles',
      'spaghetti',
    ],
    Cooler: [
      'egg',
      'egg white',
      'eggs',
      'hard-boiled eggs',
      'margerine',
      'egg yolk',
    ],
    'Seasoning/Spices/Sauces': [
      'adobo sauce',
      'balsamic glaze',
      'barbecue sauce',
      'black pepper',
      'buffalo sauce',
      'cajun seasoning',
      'caesar dressing',
      'caraway seed',
      'celery seed',
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
      'five-spice powder',
      'garam masala',
      'garlic powder',
      'guacamole',
      'gochujang',
      'hoisin sauce',
      'hot sauce',
      'ranch dressing',
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
      'sesame seeds',
      'soy sauce',
      'sriracha',
      'taco seasoning',
      'taco seasoning mix',
      'tamarind paste',
      'thyme',
      'tomato paste',
      'turmeric',
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
      'nutmeg',
      'extra virgin olive oil',
      'white wine vinegar',
      'freshly ground black pepper',
    ],
  };
}
