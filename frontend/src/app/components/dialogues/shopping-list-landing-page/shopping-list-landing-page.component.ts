import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  ShoppingList,
  ProcessedShoppingItem,
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
    'Meat & Poultry',
    'Seafood',
    'Dairy',
    'Bakery',
    'Pantry',
    'Beverages',
    'Other',
  ];

  private readonly categoryKeywords: { [category: string]: string[] } = {
    Produce: [
      'potato',
      'onion',
      'tomato',
      'lettuce',
      'apple',
      'banana',
      'broccoli',
      'carrot',
      'garlic',
      'spinach',
      'pepper',
      'lemon',
      'lime',
      'celery',
      'cucumber',
      'mushroom',
      'avocado',
      'berries',
      'zucchini',
      'eggplant',
      'corn',
      'herb',
      'herbs',
    ],
    'Meat & Poultry': [
      'chicken',
      'beef',
      'pork',
      'turkey',
      'lamb',
      'sausage',
      'bacon',
      'veal',
      'mince',
    ],
    Seafood: [
      'salmon',
      'tuna',
      'shrimp',
      'cod',
      'tilapia',
      'crab',
      'lobster',
      'fish',
      'mackerel',
      'sardines',
    ],
    Dairy: [
      'milk',
      'cheese',
      'yogurt',
      'butter',
      'egg',
      'eggs',
      'cream',
      'sour cream',
      'almond milk',
      'soy milk',
      'oat milk',
      'tofu',
      'creme fraiche',
    ],
    Bakery: [
      'bread',
      'bagel',
      'bun',
      'tortilla',
      'croissant',
      'muffin',
      'pastry',
      'baguette',
      'rolls',
    ],
    Pantry: [
      'flour',
      'sugar',
      'rice',
      'pasta',
      'oil',
      'vinegar',
      'salt',
      'spice',
      'baking powder',
      'baking soda',
      'yeast',
      'canned',
      'beans',
      'lentils',
      'oats',
      'cereal',
      'coffee',
      'tea',
      'jam',
      'honey',
      'peanut butter',
      'soy sauce',
      'broth',
      'stock',
      'chocolate',
      'nuts',
      'seeds',
      'syrup',
      'condiment',
      'dressing',
    ],
    Beverages: ['water', 'juice', 'soda', 'wine', 'beer', 'drink'],
  };

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

  private determineCategory(itemName: string): string {
    const lowerItemName = itemName.toLowerCase();
    for (const category in this.categoryKeywords) {
      if (
        this.categoryKeywords[category].some((keyword) =>
          lowerItemName.includes(keyword)
        )
      ) {
        return category;
      }
    }
    return 'Other'; // Default category
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

  private aggregateItems(
    items: ProcessedShoppingItem[]
  ): ProcessedShoppingItem[] {
    const aggregatedMap = new Map<string, ProcessedShoppingItem>();

    items.forEach((item) => {
      const key = `${item.category.toLowerCase()}_${item.name.toLowerCase()}_${(
        item.unit || ''
      ).toLowerCase()}`;
      const existing = aggregatedMap.get(key);

      if (existing) {
        const q1 = this.parseQuantity(existing.quantity);
        const q2 = this.parseQuantity(item.quantity);

        if (q1 !== null && q2 !== null) {
          existing.quantity = (q1 + q2).toString(); // Sum and convert back to string. Could format better.
        } else {
          // If cannot parse/sum, and quantities are different strings, append.
          if (
            existing.quantity.toString().trim() !==
            item.quantity.toString().trim()
          ) {
            existing.quantity = `${existing.quantity}, ${item.quantity}`;
          }
        }
      } else {
        // Store a copy to avoid modifying the original items array during iteration if it were the same.
        aggregatedMap.set(key, { ...item });
      }
    });
    return Array.from(aggregatedMap.values());
  }

  private processAndCategorizeShoppingList(): void {
    let allItems: ProcessedShoppingItem[] = [];

    // 1. Flatten all items from all dates and assign initial category
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
}
