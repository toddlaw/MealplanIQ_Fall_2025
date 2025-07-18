from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import re

# --- Data Structure ---
@dataclass
class ShoppingListItem:
    name: str
    quantity: str
    unit: str

@dataclass
class ShoppingList:
    date: str
    shopping_list: List[ShoppingListItem]

@dataclass
class ProcessedShoppingItem:
    name: str
    quantity: str
    unit: str
    category: str

# --- Constants ---
VOLUME_UNIT_HIERARCHY: Dict[str, int] = {
    'cup': 4,
    'tablespoon': 3,
    'teaspoon': 2,
    'pinch': 1,
}

VOLUME_UNIT_CONVERSION_TO_TEASPOONS: Dict[str, float] = {
    'teaspoon': 1,
    'tablespoon': 3,
    'cup': 48,
    'pinch': 1/16,
}

WEIGHT_UNIT_HIERARCHY: Dict[str, int] = {
    'pound': 2,
    'ounce': 1,
}

WEIGHT_UNIT_CONVERSION_TO_OUNCES: Dict[str, float] = {
    'ounce': 1,
    'pound': 16,
}

DENSITY_OUNCES_PER_CUP: Dict[str, float] = {
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
}

UNIT_NORMALIZATION_MAP: Dict[str, str] = {
    'tsp': 'teaspoon', 'teaspoons': 'teaspoon', 't': 'teaspoon',
    'tbsp': 'tablespoon', 'tablespoons': 'tablespoon', 'T': 'tablespoon', 'tbls': 'tablespoon',
    'cup': 'cup', 'cups': 'cup', 'c': 'cup',
    'pinch': 'pinch', 'pinches': 'pinch',
    'oz': 'ounce', 'ounce': 'ounce', 'ounces': 'ounce',
    'lb': 'pound', 'lbs': 'pound',
    'each': 'each', 'piece': 'piece', 'pieces': 'piece', 'unit': 'unit', 'units': 'unit',
    'clove': 'clove', 'cloves': 'clove',
}

CATEGORIES: List[str] = [
    'Produce', 'Meat Department', 'Seafood', 'Dairy', 'Deli', 'Baking Aisle',
    'Baked Goods', 'Junk Food', 'Breakfast Aisle', 'Frozen Food', 'Canned Food',
    'Pasta', 'Cooler', 'Seasoning/Spices/Sauces', 'Other'
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    'Produce': [
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
    'Seafood': [
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
    'Dairy': [
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
    'Deli': [
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
    'Frozen Food': ['frozen corn','frozen peas','frozen spinach','frozen berries','ice cream'],
    'Canned Food': [      'canned beans',
      'canned tomatoes',
      'canned tuna',
      'soup',
      'tomato paste',
      'cream mushroom soup',],
    'Pasta': [      'fettuccine',
      'lasagna noodles',
      'pasta',
      'ramen noodles',
      'spaghetti',],
    'Cooler': [      'egg',
      'egg white',
      'eggs',
      'hard-boiled eggs',
      'margerine',
      'egg yolk',],
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
    ]
}

# --- 유틸 함수 ---

def normalize_unit(unit_str: Optional[str]) -> Optional[str]:
    if not unit_str:
        return None
    key = unit_str.strip().lower()
    return UNIT_NORMALIZATION_MAP.get(key, key)


def parse_quantity(qty: Any) -> Optional[float]:
    # 숫자 또는 분수, 소수 모두 지원
    if isinstance(qty, (int, float)):
        return float(qty)
    s = str(qty).strip()
    try:
        return float(s)
    except ValueError:
        pass
    # "1 1/2"
    m = re.match(r"^(\d+)\s+(\d+)/(\d+)$", s)
    if m:
        whole, nume, den = m.groups()
        return int(whole) + int(nume)/int(den)
    # "a/b"
    m = re.match(r"^(\d+)/(\d+)$", s)
    if m:
        nume, den = m.groups()
        return int(nume)/int(den)
    return None


def format_number_for_display(num: float) -> str:
    if num.is_integer():
        return str(int(num))
    for val, disp in [(0.25,'0.25'),(0.5,'0.5'),(0.75,'0.75')]:
        if abs(num-val) < 1e-5:
            return disp
    if abs(num-1/3)<1e-2:
        return '0.33'
    if abs(num-2/3)<1e-2:
        return '0.67'
    return str(round(num,2))


def pluralize_unit(unit: str, quantity: float) -> str:
    if not unit or abs(quantity-1)<1e-5:
        return unit
    if unit == 'pinch':
        return 'pinches'
    return unit + 's' if not unit.endswith('s') else unit


def is_flour_or_sugar_type(item_name: str) -> bool:
    ln = item_name.lower()
    return any(key in ln for key in ['flour','sugar'])


def get_density_oz_per_cup(item_name: str) -> Optional[float]:
    ln = item_name.lower()
    for key, dens in DENSITY_OUNCES_PER_CUP.items():
        if key in ln:
            return dens
    return None


def determine_category(item_name: str) -> str:
    ln = item_name.lower().strip()
    for cat in CATEGORIES:
        if cat == 'Other':
            continue
        kws = CATEGORY_KEYWORDS.get(cat, [])
        if any(kw.lower().strip() == ln for kw in kws):
            return cat
    return 'Other'


def transform_meal_plan_to_shopping_list(meal_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    날별 raw meal_plan → [{'date','shopping-list':[{...}]}]
    """
    out: List[Dict[str, Any]] = []
    for day in meal_plan.get('days', []):
        date = day.get('date')
        items: List[Dict[str, str]] = []
        for rec in day.get('recipes', []):
            for row in rec.get('ingredients_with_quantities', [])[1:]:
                if len(row) < 3:
                    continue
                name = str(row[0]).strip()
                if not name or name.lower()=='ingredient name':
                    continue
                qty = str(row[1]).strip() or '0'
                unit = str(row[2]).strip() or ''
                items.append({'name': name, 'quantity': qty, 'unit': unit})
        if items:
            out.append({'date': date, 'shopping-list': items})
    return out


def aggregate_items(raw_items):
    buckets = {}
    for it in raw_items:
        name = it['name'].strip()
        cat = determine_category(name)
        key = f"{cat}__{name.lower()}"
        if key not in buckets:
            buckets[key] = {
                'name': name, 'category': cat,
                'vol_tsp': 0.0, 'wt_oz': 0.0,
                'count': 0.0, 'count_unit': '',
                'non_sum': [], 'entries': 0
            }
        b = buckets[key]
        b['entries'] += 1
        num = parse_quantity(it['quantity'])
        uni = normalize_unit(it['unit'])
        if num is None:
            b['non_sum'].append((it['quantity'], it['unit']))
            continue
        if is_flour_or_sugar_type(name) and uni in VOLUME_UNIT_CONVERSION_TO_TEASPOONS:
            dens = get_density_oz_per_cup(name)
            if dens:
                tsp = num * VOLUME_UNIT_CONVERSION_TO_TEASPOONS[uni]
                oz = tsp / 48 * dens
                b['wt_oz'] += oz
                continue
        if uni in VOLUME_UNIT_CONVERSION_TO_TEASPOONS:
            b['vol_tsp'] += num * VOLUME_UNIT_CONVERSION_TO_TEASPOONS[uni]
            continue
        if uni in WEIGHT_UNIT_CONVERSION_TO_OUNCES:
            b['wt_oz'] += num * WEIGHT_UNIT_CONVERSION_TO_OUNCES[uni]
            continue
        if uni in (None, '', 'each', 'piece', 'unit', 'clove'):
            b['count'] += num
            b['count_unit'] = uni or ''
            continue
        b['non_sum'].append((it['quantity'], it['unit']))

    result = []
    for b in buckets.values():
        qty_str = ''
        unit_disp = ''
        if b['count'] > 0:
            val = b['count']
            unit_disp = pluralize_unit(b['count_unit'], val) if b['count_unit'] else ''
            qty_str = f"{format_number_for_display(val)} {unit_disp}".strip()
        elif b['wt_oz'] > 0:
            if b['wt_oz'] >= WEIGHT_UNIT_CONVERSION_TO_OUNCES['pound']:
                unit_disp = 'pound'
                val = b['wt_oz'] / 16
            else:
                unit_disp = 'ounce'
                val = b['wt_oz']
            qty_str = f"{format_number_for_display(val)} {pluralize_unit(unit_disp, val)}"
        elif b['vol_tsp'] > 0:
            if b['vol_tsp'] >= VOLUME_UNIT_CONVERSION_TO_TEASPOONS['cup']:
                unit_disp = 'cup'
                val = b['vol_tsp'] / 48
            elif b['vol_tsp'] >= VOLUME_UNIT_CONVERSION_TO_TEASPOONS['tablespoon']:
                unit_disp = 'tablespoon'
                val = b['vol_tsp'] / 3
            else:
                unit_disp = 'teaspoon'
                val = b['vol_tsp']
            qty_str = f"{format_number_for_display(val)} {pluralize_unit(unit_disp, val)}"
        else:
            parts = [f"{q} {u}".strip() for q, u in b['non_sum']]
            qty_str = ", ".join(parts) if parts else '(No quantity)'
        result.append(ProcessedShoppingItem(
            name=b['name'],
            quantity=qty_str,
            unit=unit_disp,
            category=b['category']
        ))
    return result


def process_and_categorize_shopping_list(
    shopping_list_data: List[Dict[str, Any]]
) -> (List[str], Dict[str, List[ProcessedShoppingItem]]):
    """
    [{...}] → ordered categories, category→ProcessedShoppingItem 리스트 매핑
    """
    all_items: List[Dict[str, Any]] = []
    for day in shopping_list_data:
        raw = [it for it in day['shopping-list']
               if not (it['name'].lower()=='water' or
                       ('water' in it['name'].lower() and
                        all(x not in it['name'].lower() for x in ['watermelon','watercress','water chestnut'])))]
        all_items.extend(raw)
    processed = aggregate_items(all_items)
    categorized: Dict[str, List[ProcessedShoppingItem]] = {}
    for itm in processed:
        categorized.setdefault(itm.category, []).append(itm)
    for items in categorized.values():
        items.sort(key=lambda x: x.name)
    present = [c for c in CATEGORIES if c in categorized]
    extras = sorted(c for c in categorized if c not in CATEGORIES)
    ordered = present + extras
    return ordered, categorized

