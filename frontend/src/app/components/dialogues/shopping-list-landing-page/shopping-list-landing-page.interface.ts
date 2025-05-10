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
