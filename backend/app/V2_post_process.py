import csv
import datetime
import ast
import json
import pandas as pd
from typing import List, Dict


def post_process_results(recipe_df, optimized_results, x, min_date, days):
    """
    Called to process the results from the optimization function in addition
    to other data so that a JSON response can be sent to the frontend.

    recipe_df: pandas dataframe of recipes
    optimized_results: dictionary of results from the optimization function
    form of
    {
        'recipes': [ {'name': 'recipe_name', 'multiples': 2}, ... ],
        'status': 'Optimal',
        'constraint_targets': [{'nutrientName': 'calories', 'actual': 2000, 'target': 2000 - 3000}, ...]
    }

    """
    print("===============")
    
    response = {}
    response['constraints_loosened'] = optimized_results["constraints_loosened"]
    response['tableData'] = create_table_data(optimized_results)
    
    #print("\n\n RECIPES:\n\n", optimized_results['recipes'])
    recipes = extract_recipes(optimized_results['recipes'])
    #print("\n\nEXTRACTED RECIPES:\n\n", recipes)
    processed_recipe = process_recipes(recipe_df, recipes)
    #print("\n\nprocessed Recipe:\n\n", processed_recipe)
    recipes_balanced_by_day = sort_by_tags(processed_recipe)
    #print("\n\nSORTED BY TAGS:\n\n", recipes_balanced_by_day)
    days = create_days_array(recipes_balanced_by_day, min_date, days)
    response['days'] = days
    
    return response

def create_table_data(optimized_results):
    """

    """
    table_data = []
    for constraint in optimized_results["constraint_targets"]:
        entry = {}
        entry["nutrientName"] = constraint["name"]
        entry["actual"] = constraint["actual"]
        entry["target"] = constraint["target"]
        table_data.append(entry)

    return table_data

def extract_recipes(array_of_recipe_dict):
    """
    Given an array of recipe dictionaries, creates multiple entries for any with
    multiples > 1. the recipe dict is in the form
    {
        'name': 'recipe_name',
        'multiples': 2
    }

    returns an array with the recipe name
    """
    recipes = []
    for recipe in array_of_recipe_dict:
        while recipe['multiples'] > 0:
            recipes.append(recipe['name'])
            recipe['multiples'] -= 1

    return recipes

def process_recipes(recipe_df, recipes):
    """
    Returns list of processed recipes by appending information described in process_recipe()
    """
    processed_recipe = []
    for recipe in recipes:
        processed_recipe.append(process_recipe(recipe_df, recipe))
        
    return processed_recipe

def sort_by_tags(processed_recipe):
    """
    Sort recipes into groups of 9 based on meal criteria:
    - 1 lunch
    - 1 dinner
    - 2 snacks
    - 2 sides
    - 3 breakfasts
    """
    
    num_days = len(processed_recipe) / 9 
    
    breakfast_recipes = []
    lunch_recipes = []
    main_recipes = []
    side_recipes = []
    snack_recipes = []
    
    # Calculate maximum allowed for each category
    max_lunch = num_days * 1    # 1 per day
    max_main = num_days * 1     # 1 per day
    max_snack = num_days * 2    # 2 per day
    max_side = num_days * 2     # 2 per day
    max_breakfast = num_days * 3 # 3 per day
    
    for meal_dict in processed_recipe:
        # Remove the outer quotes and square brackets, then split by comma
        meal_slots_str = meal_dict['meal_slot'].strip('"[]').split(',')
        # Clean up each item by removing quotes and spaces
        meal_slots = [slot.strip().strip("'") for slot in meal_slots_str]
        
        #print("\n\nMEAL_SLOTS\n\n",meal_slots)
        
        # Check if meal_slot has only one element
        if len(meal_slots) == 1:
            
            #print("\n\nMEAL SLOT HAS LENGTH OF ONE\n\n")
            for slot in meal_slots:
                if slot == 'breakfast'and len(breakfast_recipes) < max_breakfast:
                    meal_dict["meal_name"] = "Breakfast"
                    breakfast_recipes.append(meal_dict)
                elif slot == 'lunch'and len(lunch_recipes) < max_lunch:
                    meal_dict["meal_name"] = "Lunch"
                    lunch_recipes.append(meal_dict)
                elif slot == 'main'and len(main_recipes) < max_main:
                    meal_dict["meal_name"] = "Main"
                    main_recipes.append(meal_dict)
                elif slot == 'side' and len(side_recipes) < max_side:
                    meal_dict["meal_name"] = "Side"
                    side_recipes.append(meal_dict)
                elif slot == 'snack'and len(snack_recipes) < max_snack:
                    meal_dict["meal_name"] = "Snack"
                    snack_recipes.append(meal_dict)
                
        if len(meal_slots) > 1:  # For items with 2+ meal slots
            #print("\n\nMEAL SLOT HAS LENGTH OF TWO\n\n")
            # Try to place the recipe in the category that needs it most
            placed = False
            for slot in meal_slots:
                if slot == 'lunch' and len(lunch_recipes) < max_lunch:
                    meal_dict["meal_name"] = "Lunch"
                    lunch_recipes.append(meal_dict)
                    placed = True
                    break
                elif slot == 'main' and len(main_recipes) < max_main:
                    meal_dict["meal_name"] = "Main"
                    main_recipes.append(meal_dict)
                    placed = True
                    break
                elif slot == 'snack' and len(snack_recipes) < max_snack:
                    meal_dict["meal_name"] = "Snack"
                    snack_recipes.append(meal_dict)
                    placed = True
                    break
                elif slot == 'side' and len(side_recipes) < max_side:
                    meal_dict["meal_name"] = "Side"
                    side_recipes.append(meal_dict)
                    placed = True
                    break
                elif slot == 'breakfast' and len(breakfast_recipes) < max_breakfast:
                    meal_dict["meal_name"] = "Breakfast"
                    breakfast_recipes.append(meal_dict)
                    placed = True
                    break
    
    lunch_recipes = [
                        {'carbohydrates': '13.8442', 'country': 'Australian', 'fat': '5.9841', 'price': 'N/A', 'protein': '5.7645', 'region': 'Australasian ', 'title': 'Savory Baking Powder Bread', 'ingredients': ['purpose flour', 'salt', 'baking powder', 'milk'
                            ], 'calories': '121.382', 'meal_slot': "['lunch', 'side']", 'id': '5425', 'cook_time': '40 minutes', 'prep_time': '5 minutes', 'sub_region': 'Australian ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Set the oven to preheat at 375Â°F (190Â°C).'
                                ],
                                ['2', 'In a large mixing bowl, combine flour, salt, and baking powder by sifting them together. Gradually incorporate milk to form a soft dough. Shape the dough into a round and position it on an ungreased baking sheet.'
                                ],
                                ['3', 'Bake in the preheated oven for 30 minutes. After removing the loaf from the oven, slice it in half and return to bake for an additional 10 minutes. Transfer to a wire rack to cool before serving.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['purpose flour', '2', 'cups', '', '-', '-', '-', '-'
                                ],
                                ['salt', '1/2', 'teaspoon', '', '-', '-', '-', '-'
                                ],
                                ['baking powder', '4', 'teaspoons', '', '9.752', '5.0968', '0.0', '0.0'
                                ],
                                ['milk', '3/4', 'cup', '', '111.63', '8.7474', '5.7645', '5.9841'
                                ]
                            ],
                            'meal_name':'Lunch'
                        },
                        {'carbohydrates': '13.8442', 'country': 'Australian', 'fat': '5.9841', 'price': 'N/A', 'protein': '5.7645', 'region': 'Australasian ', 'title': 'Savory Baking Powder Bread', 'ingredients': ['purpose flour', 'salt', 'baking powder', 'milk'
                            ], 'calories': '121.382', 'meal_slot': "['lunch', 'side']", 'id': '5425', 'cook_time': '40 minutes', 'prep_time': '5 minutes', 'sub_region': 'Australian ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Set the oven to preheat at 375Â°F (190Â°C).'
                                ],
                                ['2', 'In a large mixing bowl, combine flour, salt, and baking powder by sifting them together. Gradually incorporate milk to form a soft dough. Shape the dough into a round and position it on an ungreased baking sheet.'
                                ],
                                ['3', 'Bake in the preheated oven for 30 minutes. After removing the loaf from the oven, slice it in half and return to bake for an additional 10 minutes. Transfer to a wire rack to cool before serving.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['purpose flour', '2', 'cups', '', '-', '-', '-', '-'
                                ],
                                ['salt', '1/2', 'teaspoon', '', '-', '-', '-', '-'
                                ],
                                ['baking powder', '4', 'teaspoons', '', '9.752', '5.0968', '0.0', '0.0'
                                ],
                                ['milk', '3/4', 'cup', '', '111.63', '8.7474', '5.7645', '5.9841'
                                ]
                            ],
                            'meal_name':'Lunch'
                        },
                        {'carbohydrates': '13.8442', 'country': 'Australian', 'fat': '5.9841', 'price': 'N/A', 'protein': '5.7645', 'region': 'Australasian ', 'title': 'Savory Baking Powder Bread', 'ingredients': ['purpose flour', 'salt', 'baking powder', 'milk'
                            ], 'calories': '121.382', 'meal_slot': "['lunch', 'side']", 'id': '5425', 'cook_time': '40 minutes', 'prep_time': '5 minutes', 'sub_region': 'Australian ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Set the oven to preheat at 375Â°F (190Â°C).'
                                ],
                                ['2', 'In a large mixing bowl, combine flour, salt, and baking powder by sifting them together. Gradually incorporate milk to form a soft dough. Shape the dough into a round and position it on an ungreased baking sheet.'
                                ],
                                ['3', 'Bake in the preheated oven for 30 minutes. After removing the loaf from the oven, slice it in half and return to bake for an additional 10 minutes. Transfer to a wire rack to cool before serving.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['purpose flour', '2', 'cups', '', '-', '-', '-', '-'
                                ],
                                ['salt', '1/2', 'teaspoon', '', '-', '-', '-', '-'
                                ],
                                ['baking powder', '4', 'teaspoons', '', '9.752', '5.0968', '0.0', '0.0'
                                ],
                                ['milk', '3/4', 'cup', '', '111.63', '8.7474', '5.7645', '5.9841'
                                ]
                            ],
                            'meal_name':'Lunch'
                        }
                    ]
    side_recipes = [
                        {'carbohydrates': '7.8748', 'country': 'Italian', 'fat': '0.162', 'price': 'N/A', 'protein': '4.2984', 'region': 'European ', 'title': 'Classic Homemade Italian Bread', 'ingredients': ['water', 'white sugar', 'yeast', 'salt', 'purpose flour'
                            ], 'calories': '49.554', 'meal_slot': "['side']", 'id': 
                    '10884', 'cook_time': '60 minutes', 'prep_time': '20 minutes', 'sub_region': 'Italian ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Assemble all ingredients needed for the recipe.'
                                ],
                                ['2', 'Combine warm water, sugar, and yeast in a medium mixing bowl. Let the mixture sit until the yeast becomes foamy.'
                                ],
                                ['3', 'Stir in 4 cups of flour and beat until smooth. Cover and let the mixture rest for 15 minutes.'
                                ],
                                ['4', 'Knead until soft and smooth is going to turn into "Knead until the dough is soft and smooth." '
                                ],
                                ['5', 'After the dough has doubled, deflate it by punching it down. Divide it into three portions, place them back into the bowl, cover, and allow them to rise once more.'
                                ],
                                ['6', 'Shape dough into loaves. Place on a baking sheet lined with parchment paper. Brush with olive oil, and sprinkle with sesame seeds or other toppings. Cover with a damp cloth and let rise until doubled in size. Baking time and temperature may vary based on the loaf size and oven.'
                                ],
                                ['7', 'Sorry, I cannot complete this task.'
                                ],
                                ['8', 'Mistake loaves with water and place in the preheated oven.'
                                ],
                                ['9', 'Assemble and bake as directed in the original recipe.'
                                ],
                                ['10', 'The revised step based on the review feedback is "We have updated the recipe to include a bake time of 25 to 30 minutes."'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['water', '3', 'cups', '', '0.0', '0.0', '0.0', '0.0'
                                ],
                                ['white sugar', '1', 'teaspoon', '', '16.254', '4.1992', '0.0', '0.0'
                                ],
                                ['yeast', '1', 'tablespoon', '', '33.3', '3.6756', '4.2984', '0.162'
                                ],
                                ['salt', '1', 'tablespoon', '', '-', '-', '-', '-'
                                ],
                                ['purpose flour', '7', 'cups', '', '-', '-', '-', '-'
                                ]
                            ],
                            'meal_name':'Side'
                        },
                        {'carbohydrates': '61.0093', 'country': 'US', 'fat': '0.425', 'price': 'N/A', 'protein': '0.6824', 'region': 'North American ', 'title': 'Cinnamon Spiced Apple Sauce', 'ingredients': ['apple', 'cinnamon', 'water', 'brown sugar'
                            ], 'calories': '232.6', 'meal_slot': "['side']", 'id': '14161', 'cook_time': '30 minutes', 'prep_time': '15 minutes', 'sub_region': 'US ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Cook shredded apples in a medium saucepan on medium low heat. Sprinkle with cinnamon, add water, and cook until apples are soft and mushy.'
                                ],
                                ['2', 'Incorporate the brown sugar and blend thoroughly; optionally, add a scoop of ice cream before serving.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['apple', '2', '', 'peeled cored shredded', '130.0', '34.525', '0.65', '0.425'
                                ],
                                ['cinnamon', '1', 'teaspoon', 'ground', '-', '-', '-', '-'
                                ],
                                ['water', '1/4', 'cup', '', '0.0', '0.0', '0.0', '0.0'
                                ],
                                ['brown sugar', '3', 'tablespoons', '', '102.6', '26.4843', '0.0324', '0.0'
                                ]
                            ],
                            'meal_name':'Side'
                        },
                        {'carbohydrates': '0.2701', 'country': 'US', 'fat': '27.0148', 'price': 'N/A', 'protein': '0.0411', 'region': 'North American ', 'title': 'Seasoned Oven-Roasted Potatoes', 'ingredients': ['olive oil', 'potato', 'oregano', 'salt', 'black pepper'
                            ], 'calories': '239.7328', 'meal_slot': "['side']", 'id': '18425', 'cook_time': '65 minutes', 'prep_time': '10 minutes', 'sub_region': 'US ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Roasted sweet potato cubes will complement a variety of meals during fall.'
                                ],
                                ['2', 'Compile a list of ingredients and detailed instructions using the recipe below. Let me know if you would like to go over the details of the recipe.'
                                ],
                                ['3', 'Here is a revised step for you: "These roasted sweet potato cubes are flavored with a simple mix of dried oregano, salt, and pepper, but feel free to customize the seasonings to your preference."'
                                ],
                                ['4', 'Here are the steps to reword:\r\n\r\n1. Preheat the oven to 350 degrees F (175 degrees C). \r\n2. Grease a 9x13 inch baking pan. \r\n3. In a medium mixing bowl, cream together the shortening, margarine, white sugar, and brown sugar until smooth. \r\n4. Beat in the eggs one by one, then stir in the peanut butter and vanilla. \r\n5. Combine the flour, cocoa, baking powder, baking soda, and cream of tartar. \r\n6. Stir the dry ingredients into the sugar mixture. \r\n7. Mix in the oats, walnuts (if desired), and chocolate chips. \r\n8. Drop rounded spoonfuls of dough onto the prepared cookie sheets. \r\n9. Bake for 8 to 10 minutes in the preheated oven. \r\n10. Allow cookies to cool on the baking sheet for 5 minutes before moving them to a wire rack to cool completely. \r\n\r\nPlease let me know if you need further assistance with rewording the steps.'
                                ],
                                ['5', 'Bake the sweet potatoes until fork-tender in a preheated 350°F oven, usually around 45 minutes for three large cubed sweet potatoes.'
                                ],
                                ['6', 'Preheat oven to 350 degrees F. Grease cookie sheets.'
                                ],
                                ['7', 'You can refrigerate any leftover baked sweet potato cubes in an airtight container, and they will stay fresh for up to five days.'
                                ],
                                ['8', 'Bob Seale enthusiastically praises this sweet potato dish, noting its delicious flavor. He shares that he roasted the sweet potatoes on a baking sheet, turning them midway to attain a crispy texture. Just before serving, Bob drizzled a few drops of fresh lemon juice over them for a flavorful touch.'
                                ],
                                ['9', '“This dish received high praise,” remarked <a data-component="link" data-ordinal="1" data-source="inlineLink" data-type="internalLink" href="https://www.allrecipes.com/cook/15867062">Patti Copeland Talcott</a>. “I paired it with a pork loin roast, and it was a fantastic blend. Super simple to prepare and absolutely delicious.”'
                                ],
                                ['10', '"Linda mentioned that this recipe is straightforward to make; she substituted Herbs de Provence for oregano and plans to make it again."'], ['11', 'Corey Williams contributed to the editorial process for this recipe.'], ['12', 'Collect all the necessary ingredients.'], ['13', 'Preheat the oven to 350 degrees Fahrenheit (175 degrees Celsius). Lightly grease a glass or nonstick baking dish with a thin coat of olive oil.'
                                ],
                                ['14', 'Prepare sweet potatoes by washing, peeling, and cutting them into medium-sized pieces.'
                                ],
                                ['15', 'Stir the sweet potato cubes with olive oil in the baking dish. Add a sprinkle of oregano, salt, and pepper to season.'
                                ],
                                ['16', 'Bake until the sweet potatoes are soft and easily pierced with a fork, typically around 45 minutes to an hour.'
                                ],
                                ['17', 'Savor the delicious baked sweet potatoes!'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['olive oil', '2', 'tablespoons', '', '238.68', '0.0', '0.0', '27.0'
                                ],
                                ['potato', '3', '', 'sweet', '-', '-', '-', '-'
                                ],
                                ['oregano', '2', 'pinches', '', '0.3312', '0.0862', '0.0112', '0.0054'
                                ],
                                ['salt', '2', 'pinches', '', '-', '-', '-', '-'
                                ],
                                ['black pepper', '2', 'pinches', 'ground', '0.7216', '0.1839', '0.0299', '0.0094'
                                ]
                            ],
                            'meal_name':'Side'
                        },
                        {'carbohydrates': '13.145', 'country': 'US', 'fat': '0.255', 'price': 'N/A', 'protein': '0.8999', 'region': 'North American ', 'title': 'Citrus Honey Glazed Chicken Breast', 'ingredients': ['orange juice', 'lime', 'honey', 'red pepper flake', 'chicken breast half', 'cilantro'
                            ], 'calories': '56.6602', 'meal_slot': "['side','snack]", 'id': '18512', 'cook_time': '12 minutes', 'prep_time': '5 minutes', 'sub_region': 'US ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Marinate the chicken in a mixture of orange juice, lime juice, honey, and red pepper flakes for 30 minutes in the refrigerator.'
                                ],
                                ['2', 'Preheat an outdoor grill over medium-high heat and lightly oil the grates.'
                                ],
                                ['3', 'Grill the marinated chicken until cooked through, about 6 to 8 minutes per side. Enjoy topped with cilantro.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['orange juice', '1/2', 'cup', '', '55.8', '12.895999999999999', '0.868', '0.248'
                                ],
                                ['lime', '1/2', '', 'juiced', '0.6302', '0.2123', '0.0106', '0.0018'
                                ],
                                ['honey', '1', 'tablespoon', '', '-', '-', '-', '-'
                                ],
                                ['red pepper flake', '1', 'teaspoon', 'crushed', '-', '-', '-', '-'
                                ],
                                ['chicken breast half', '4', '', 'skinless boneless', '-', '-', '-', '-'
                                ],
                                ['cilantro', '1', 'tablespoon', 'chopped', '0.23', '0.0367', '0.0213', '0.0052'
                                ]
                            ],
                            'meal_name':'Side'
                        },
                        {'carbohydrates': '13.145', 'country': 'US', 'fat': '0.255', 'price': 'N/A', 'protein': '0.8999', 'region': 'North American ', 'title': 'Citrus Honey Glazed Chicken Breast', 'ingredients': ['orange juice', 'lime', 'honey', 'red pepper flake', 'chicken breast half', 'cilantro'
                            ], 'calories': '56.6602', 'meal_slot': "['side','snack]", 'id': '18512', 'cook_time': '12 minutes', 'prep_time': '5 minutes', 'sub_region': 'US ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Marinate the chicken in a mixture of orange juice, lime juice, honey, and red pepper flakes for 30 minutes in the refrigerator.'
                                ],
                                ['2', 'Preheat an outdoor grill over medium-high heat and lightly oil the grates.'
                                ],
                                ['3', 'Grill the marinated chicken until cooked through, about 6 to 8 minutes per side. Enjoy topped with cilantro.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['orange juice', '1/2', 'cup', '', '55.8', '12.895999999999999', '0.868', '0.248'
                                ],
                                ['lime', '1/2', '', 'juiced', '0.6302', '0.2123', '0.0106', '0.0018'
                                ],
                                ['honey', '1', 'tablespoon', '', '-', '-', '-', '-'
                                ],
                                ['red pepper flake', '1', 'teaspoon', 'crushed', '-', '-', '-', '-'
                                ],
                                ['chicken breast half', '4', '', 'skinless boneless', '-', '-', '-', '-'
                                ],
                                ['cilantro', '1', 'tablespoon', 'chopped', '0.23', '0.0367', '0.0213', '0.0052'
                                ]
                            ],
                            'meal_name':'Side'
                        },
                        {'carbohydrates': '13.145', 'country': 'US', 'fat': '0.255', 'price': 'N/A', 'protein': '0.8999', 'region': 'North American ', 'title': 'Citrus Honey Glazed Chicken Breast', 'ingredients': ['orange juice', 'lime', 'honey', 'red pepper flake', 'chicken breast half', 'cilantro'
                            ], 'calories': '56.6602', 'meal_slot': "['side','snack]", 'id': '18512', 'cook_time': '12 minutes', 'prep_time': '5 minutes', 'sub_region': 'US ', 'instructions': [
                                ['Step', 'Instruction'
                                ],
                                ['1', 'Marinate the chicken in a mixture of orange juice, lime juice, honey, and red pepper flakes for 30 minutes in the refrigerator.'
                                ],
                                ['2', 'Preheat an outdoor grill over medium-high heat and lightly oil the grates.'
                                ],
                                ['3', 'Grill the marinated chicken until cooked through, about 6 to 8 minutes per side. Enjoy topped with cilantro.'
                                ]
                            ], 'ingredients_with_quantities': [
                                ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                ],
                                ['orange juice', '1/2', 'cup', '', '55.8', '12.895999999999999', '0.868', '0.248'
                                ],
                                ['lime', '1/2', '', 'juiced', '0.6302', '0.2123', '0.0106', '0.0018'
                                ],
                                ['honey', '1', 'tablespoon', '', '-', '-', '-', '-'
                                ],
                                ['red pepper flake', '1', 'teaspoon', 'crushed', '-', '-', '-', '-'
                                ],
                                ['chicken breast half', '4', '', 'skinless boneless', '-', '-', '-', '-'
                                ],
                                ['cilantro', '1', 'tablespoon', 'chopped', '0.23', '0.0367', '0.0213', '0.0052'
                                ]
                            ],
                            'meal_name':'Side'
                        }
                    ]
    
    breakfast_recipes = [
                            {'carbohydrates': '12.7432', 'country': 'Italian', 'fat': '22.2438', 'price': 'N/A', 'protein': '26.526', 'region': 'European ', 'title': 'Creamy Egg and Milk Manicotti Pancakes', 'ingredients': ['egg', 'milk', 'purpose flour'
                                ], 'calories': '363.34', 'meal_slot': "['breakfast','lunch']", 'id': '12367', 'cook_time': '10 minutes', 'prep_time': '5 minutes', 'sub_region': 'Italian ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Whisk together eggs and milk in a large bowl until well combined. Gradually add flour and mix until the batter is smooth. Lightly grease an 8-inch skillet or crepe pan with cooking spray over medium-high heat. Pour the batter into the pan, covering the surface evenly. Cook each pancake until golden, flipping once, for about 2 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', '', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['milk', '1', 'cup', '', '148.84', '11.6632', '7.686', '7.9788'
                                    ],
                                    ['purpose flour', '1', 'cup', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '9.7213', 'country': 'French', 'fat': '14.4312', 'price': 'N/A', 'protein': '19.0001', 'region': 'European ', 'title': 'Cinnamon French Toast', 'ingredients': ['egg', 'white sugar', 'milk', 'cinnamon', 'salt', 'bread'
                                ], 'calories': '250.1088', 'meal_slot': "['breakfast']", 'id': '9860', 'cook_time': '5 minutes', 'prep_time': '5 minutes', 'sub_region': 'French ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Combine beaten eggs, sugar, milk, cinnamon, and salt in a large, shallow bowl. Dip the bread slices into the egg mixture to coat.'
                                    ],
                                    ['2', 'Spray a skillet with cooking spray and preheat over medium heat. In batches, cook the bread in the hot skillet until golden brown, about 2 to 3 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', 'beaten', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['white sugar', '2', 'teaspoons', '', '32.508', '8.3983', '0.0', '0.0'
                                    ],
                                    ['milk', '1', 'teaspoon', '', '3.1008', '0.243', '0.1601', '0.1662'
                                    ],
                                    ['cinnamon', '1', 'teaspoon', 'ground', '-', '-', '-', '-'
                                    ],
                                    ['salt', '1/4', 'teaspoon', '', '-', '-', '-', '-'
                                    ],
                                    ['bread', '6', 'slices', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '12.7432', 'country': 'Italian', 'fat': '22.2438', 'price': 'N/A', 'protein': '26.526', 'region': 'European ', 'title': 'Creamy Egg and Milk Manicotti Pancakes', 'ingredients': ['egg', 'milk', 'purpose flour'
                                ], 'calories': '363.34', 'meal_slot': "['breakfast','lunch']", 'id': '12367', 'cook_time': '10 minutes', 'prep_time': '5 minutes', 'sub_region': 'Italian ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Whisk together eggs and milk in a large bowl until well combined. Gradually add flour and mix until the batter is smooth. Lightly grease an 8-inch skillet or crepe pan with cooking spray over medium-high heat. Pour the batter into the pan, covering the surface evenly. Cook each pancake until golden, flipping once, for about 2 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', '', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['milk', '1', 'cup', '', '148.84', '11.6632', '7.686', '7.9788'
                                    ],
                                    ['purpose flour', '1', 'cup', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '9.7213', 'country': 'French', 'fat': '14.4312', 'price': 'N/A', 'protein': '19.0001', 'region': 'European ', 'title': 'Cinnamon French Toast', 'ingredients': ['egg', 'white sugar', 'milk', 'cinnamon', 'salt', 'bread'
                                ], 'calories': '250.1088', 'meal_slot': "['breakfast']", 'id': '9860', 'cook_time': '5 minutes', 'prep_time': '5 minutes', 'sub_region': 'French ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Combine beaten eggs, sugar, milk, cinnamon, and salt in a large, shallow bowl. Dip the bread slices into the egg mixture to coat.'
                                    ],
                                    ['2', 'Spray a skillet with cooking spray and preheat over medium heat. In batches, cook the bread in the hot skillet until golden brown, about 2 to 3 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', 'beaten', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['white sugar', '2', 'teaspoons', '', '32.508', '8.3983', '0.0', '0.0'
                                    ],
                                    ['milk', '1', 'teaspoon', '', '3.1008', '0.243', '0.1601', '0.1662'
                                    ],
                                    ['cinnamon', '1', 'teaspoon', 'ground', '-', '-', '-', '-'
                                    ],
                                    ['salt', '1/4', 'teaspoon', '', '-', '-', '-', '-'
                                    ],
                                    ['bread', '6', 'slices', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '12.7432', 'country': 'Italian', 'fat': '22.2438', 'price': 'N/A', 'protein': '26.526', 'region': 'European ', 'title': 'Creamy Egg and Milk Manicotti Pancakes', 'ingredients': ['egg', 'milk', 'purpose flour'
                                ], 'calories': '363.34', 'meal_slot': "['breakfast','lunch']", 'id': '12367', 'cook_time': '10 minutes', 'prep_time': '5 minutes', 'sub_region': 'Italian ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Whisk together eggs and milk in a large bowl until well combined. Gradually add flour and mix until the batter is smooth. Lightly grease an 8-inch skillet or crepe pan with cooking spray over medium-high heat. Pour the batter into the pan, covering the surface evenly. Cook each pancake until golden, flipping once, for about 2 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', '', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['milk', '1', 'cup', '', '148.84', '11.6632', '7.686', '7.9788'
                                    ],
                                    ['purpose flour', '1', 'cup', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '9.7213', 'country': 'French', 'fat': '14.4312', 'price': 'N/A', 'protein': '19.0001', 'region': 'European ', 'title': 'Cinnamon French Toast', 'ingredients': ['egg', 'white sugar', 'milk', 'cinnamon', 'salt', 'bread'
                                ], 'calories': '250.1088', 'meal_slot': "['breakfast']", 'id': '9860', 'cook_time': '5 minutes', 'prep_time': '5 minutes', 'sub_region': 'French ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Combine beaten eggs, sugar, milk, cinnamon, and salt in a large, shallow bowl. Dip the bread slices into the egg mixture to coat.'
                                    ],
                                    ['2', 'Spray a skillet with cooking spray and preheat over medium heat. In batches, cook the bread in the hot skillet until golden brown, about 2 to 3 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', 'beaten', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['white sugar', '2', 'teaspoons', '', '32.508', '8.3983', '0.0', '0.0'
                                    ],
                                    ['milk', '1', 'teaspoon', '', '3.1008', '0.243', '0.1601', '0.1662'
                                    ],
                                    ['cinnamon', '1', 'teaspoon', 'ground', '-', '-', '-', '-'
                                    ],
                                    ['salt', '1/4', 'teaspoon', '', '-', '-', '-', '-'
                                    ],
                                    ['bread', '6', 'slices', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '12.7432', 'country': 'Italian', 'fat': '22.2438', 'price': 'N/A', 'protein': '26.526', 'region': 'European ', 'title': 'Creamy Egg and Milk Manicotti Pancakes', 'ingredients': ['egg', 'milk', 'purpose flour'
                                ], 'calories': '363.34', 'meal_slot': "['breakfast','lunch']", 'id': '12367', 'cook_time': '10 minutes', 'prep_time': '5 minutes', 'sub_region': 'Italian ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Whisk together eggs and milk in a large bowl until well combined. Gradually add flour and mix until the batter is smooth. Lightly grease an 8-inch skillet or crepe pan with cooking spray over medium-high heat. Pour the batter into the pan, covering the surface evenly. Cook each pancake until golden, flipping once, for about 2 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', '', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['milk', '1', 'cup', '', '148.84', '11.6632', '7.686', '7.9788'
                                    ],
                                    ['purpose flour', '1', 'cup', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '9.7213', 'country': 'French', 'fat': '14.4312', 'price': 'N/A', 'protein': '19.0001', 'region': 'European ', 'title': 'Cinnamon French Toast', 'ingredients': ['egg', 'white sugar', 'milk', 'cinnamon', 'salt', 'bread'
                                ], 'calories': '250.1088', 'meal_slot': "['breakfast']", 'id': '9860', 'cook_time': '5 minutes', 'prep_time': '5 minutes', 'sub_region': 'French ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Combine beaten eggs, sugar, milk, cinnamon, and salt in a large, shallow bowl. Dip the bread slices into the egg mixture to coat.'
                                    ],
                                    ['2', 'Spray a skillet with cooking spray and preheat over medium heat. In batches, cook the bread in the hot skillet until golden brown, about 2 to 3 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', 'beaten', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['white sugar', '2', 'teaspoons', '', '32.508', '8.3983', '0.0', '0.0'
                                    ],
                                    ['milk', '1', 'teaspoon', '', '3.1008', '0.243', '0.1601', '0.1662'
                                    ],
                                    ['cinnamon', '1', 'teaspoon', 'ground', '-', '-', '-', '-'
                                    ],
                                    ['salt', '1/4', 'teaspoon', '', '-', '-', '-', '-'
                                    ],
                                    ['bread', '6', 'slices', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            },
                            {'carbohydrates': '12.7432', 'country': 'Italian', 'fat': '22.2438', 'price': 'N/A', 'protein': '26.526', 'region': 'European ', 'title': 'Creamy Egg and Milk Manicotti Pancakes', 'ingredients': ['egg', 'milk', 'purpose flour'
                                ], 'calories': '363.34', 'meal_slot': "['breakfast','lunch']", 'id': '12367', 'cook_time': '10 minutes', 'prep_time': '5 minutes', 'sub_region': 'Italian ', 'instructions': [
                                    ['Step', 'Instruction'
                                    ],
                                    ['1', 'Whisk together eggs and milk in a large bowl until well combined. Gradually add flour and mix until the batter is smooth. Lightly grease an 8-inch skillet or crepe pan with cooking spray over medium-high heat. Pour the batter into the pan, covering the surface evenly. Cook each pancake until golden, flipping once, for about 2 minutes per side.'
                                    ]
                                ], 'ingredients_with_quantities': [
                                    ['Ingredient Name', 'Quantity', 'Unit', 'State', 'Energy (kcal)', 'Carbohydrates', 'Protein (g)', 'Total Lipid (Fat) (g)'
                                    ],
                                    ['egg', '3', '', '', '214.5', '1.08', '18.84', '14.265'
                                    ],
                                    ['milk', '1', 'cup', '', '148.84', '11.6632', '7.686', '7.9788'
                                    ],
                                    ['purpose flour', '1', 'cup', '', '-', '-', '-', '-'
                                    ]
                                ],
                                'meal_name': 'Breakfast'
                            }
                        ]
    
    # print("\n\nLUNCHs\n\n",lunch_recipes,len(lunch_recipes))
    # print("\n\nMAINs\n\n",main_recipes,len(main_recipes))
    # print("\n\nSIDEs\n\n",side_recipes,len(side_recipes))
    # print("\n\nSNACKs\n\n",snack_recipes,len(snack_recipes))
    # print("\n\nBREAKFASTs\n\n",breakfast_recipes,len(breakfast_recipes))
    
    result_groups = []
    for i in range(int(num_days)):
        current_group = []
        # Add 3 breakfasts
        current_group.extend(breakfast_recipes[i*3:i*3+3])
        # Add first snack
        current_group.append(snack_recipes[i*2])
        # Add lunch
        current_group.append(lunch_recipes[i])
        # Add second snack
        current_group.append(snack_recipes[i*2+1])
        # Add main (dinner)
        current_group.append(main_recipes[i])
        # Add 2 sides
        current_group.extend(side_recipes[i*2:i*2+2])
        
        # Adds current_group (a singular day) to the list of days (day logic has not been implemented yet however)
        result_groups.append(current_group)

    return result_groups

def create_days_array(recipes_balanced_by_day, min_date, days):
    base = min_date
    date_list = [base + datetime.timedelta(days=x) for x in range(days)]
    days_array = []

    for i, date in enumerate(date_list):
        day = date.strftime("%Y-%m-%d")
        # Now we take the entire sublist for each day, no slicing needed
        days_array.append(create_meal_date(recipes_balanced_by_day[i], day))
    
    return days_array

    

def create_meal_date(recipes, day):
    """
    Given a recipe and a day of the week, creates a dictionary that contains
    all of the information for the recipe that the frontend expects
    """
    day_dict = {}

    date_object = datetime.datetime.strptime(day, '%Y-%m-%d')
    day_dict['date'] = day
    day_dict['date_weekday'] = date_object.strftime('%A %B %d')
    recipe_array = []
    for recipe in recipes:
        recipe_array.append(recipe)

    day_dict['recipes'] = recipe_array

    return day_dict


def process_recipe(recipe_df, recipe_name):
    """
    Given a pandas dataframe of recipes creates a dictionary that contains
    all of the information for the recipe with the given name that the frontend
    expects
    """
    recipe_row = recipe_df.loc[recipe_df['title'] == recipe_name]
    res = {}
    recipe_dict = {}
    recipe_dict['carbohydrates'] = recipe_row['carbohydrates_g'].values[0]
    recipe_dict['country'] = recipe_row['country'].values[0]
    recipe_dict['fat'] = recipe_row['fats_total_g'].values[0]
    recipe_dict['price'] = "N/A"
    recipe_dict['protein'] = recipe_row['protein_g'].values[0]
    recipe_dict['region'] = recipe_row['region'].values[0]
    recipe_dict['title'] = recipe_row['title'].values[0]
    recipe_dict['ingredients'] = recipe_row['ingredients'].values[0]
    recipe_dict['calories'] = recipe_row['energy_kcal'].values[0]
    recipe_dict['meal_slot'] = recipe_row['meal_slot'].values[0]
    recipe_dict['id'] = recipe_row['number'].values[0]
    recipe_dict['cook_time'] = recipe_row['cooktime'].values[0]
    recipe_dict['prep_time'] = recipe_row['preptime'].values[0]
    recipe_dict['sub_region'] = recipe_row['subregion'].values[0]

    # retrive instructions

    instruction_file_path = f'''./meal_db/instructions/instructions_{
        recipe_dict['id']}.csv'''
    ingredient_file_path = f"./meal_db/ingredients/{recipe_dict['id']}.csv"

    # instruction_content = pd.read_csv(instruction_file_path)
    # recipe_dict['instructions'] = instruction_content.values.tolist()

    with open(instruction_file_path, newline='') as csvfile:
        content = csv.reader(csvfile)
        recipe_dict['instructions'] = []
        for row in content:
            recipe_dict['instructions'].append(row)

    # retrive ingredients_with_quantities

    # cannot use pandas here, will raise an error

    with open(ingredient_file_path, newline='') as csvfile:
        content = csv.reader(csvfile)
        recipe_dict['ingredients_with_quantities'] = []
        for row in content:
            recipe_dict['ingredients_with_quantities'].append(row)

    for key, value in recipe_dict.items():
        res[key] = f"{value}"

    # Convert ingredients from a string to a list
    res['ingredients'] = ast.literal_eval(res['ingredients'])
    res['instructions'] = ast.literal_eval(res['instructions'])
    res['ingredients_with_quantities'] = ast.literal_eval(
        res['ingredients_with_quantities'])

    return res