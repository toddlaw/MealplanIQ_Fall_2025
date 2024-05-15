from fractions import Fraction

import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI


def retrieve_recipe_details(recipe_file_path):
    # If reading all sheets, set sheet_name=None, or remove the parameter
    df = pd.read_excel(recipe_file_path, sheet_name=["Basic Starches", "Cuisine Mains", "Cuisine Sides",
                                                     "Snacks", "Drinks", "Vegan Mains", "Vegetarian Mains",
                                                     "Fish Mains", "Tofu Mains", "Desserts",
                                                     "Additional breakfast items"])
    informal_names = [name for sheet in df for name in df[sheet]["Informal Name"].tolist()]
    generated_names = [name for sheet in df for name in df[sheet]["Generated Name"].tolist()]
    numbers = [number for sheet in df for number in df[sheet]["Number"].tolist()]

    recipe_details = {
        "Informal Name": informal_names,
        "Generated Name": generated_names,
        "Number": numbers
    }

    return recipe_details


def generate_ingredients_and_instructions(dish_type: str, dish_name: str, number: int) -> dict:
    print(f"\nGenerating ingredients and instructions for {dish_type}: {dish_name} #{number}")
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
                Generate a recipe in JSON format based on the provided recipe type and name. Ensure all ingredients use 
                units directly convertible to grams for consistent nutritional calculations.

                JSON format specifications:
                - Start and end with '{' and '}'.
                - Include two keys: "Ingredients" and "Instructions".
                - "Ingredients": A string with each ingredient formatted as "ingredient_name,quantity,unit", 
                separated by '\\n'. Only use these units: gram, ounce, tbsp, tsp, ml, L 
                (exclude cups to ensure precision).
                - "Instructions": A string with each step formatted as "step_number,instruction", separated by '\\n', 
                with temperatures in Fahrenheit. For dishes that don't require instructions, the instructions can 
                be an empty string.

                Example:
                {
                    "Ingredients": "Chicken breast,200,gram\\nOlive oil,30,ml",
                    "Instructions": "1,Preheat the oven to 375°F\\n2,Season the chicken with salt and pepper"
                }

                Ensure the response is accurate, concise, and adheres to the structure and unit requirements specified.
                """
            },
            {
                "role": "user",
                "content": f"I have a {dish_type} recipe named {dish_name}. "
                           f"Please generate the ingredients and instructions for me."
            }
        ],
    )

    response_content = chat_completion.choices[0].message.content
    parsed_response = json.loads(response_content)
    return parsed_response


def extract_ingredients_info(ingredients: str) -> dict:
    ingredients_data = {
        "Ingredients": [],
        "Quantity": [],
        "Unit": []
    }

    print(f"Ingredients list:\n{ingredients}\n")
    for ingredient in ingredients.splitlines():
        ingredients_row = ingredient.split(",")
        print(ingredients_row)

        ingredient_name = ingredients_row[0]
        ingredient_quantity = ingredients_row[1]

        # Handle case where there is no unit
        ingredient_unit = ingredients_row[2] if len(ingredients_row) > 2 else ""

        # Convert quantity to decimal form if fractional
        if "/" in ingredient_quantity:
            # Check if quantity is a mixed fraction
            if " " in ingredient_quantity:
                whole_part, fractional_part = ingredient_quantity.split(" ")
                ingredient_quantity = float(Fraction(whole_part)) + float(Fraction(fractional_part))
            else:
                ingredient_quantity = float(Fraction(ingredient_quantity))

        ingredients_data["Ingredients"].append(ingredient_name)
        ingredients_data["Quantity"].append(ingredient_quantity)
        ingredients_data["Unit"].append(ingredient_unit)

    return ingredients_data


def extract_instructions_data(instructions: str) -> dict:
    instructions_data = {
        "Step": [],
        "Instruction": []
    }

    print(f"\nInstructions:\n{instructions}")
    for instruction in instructions.splitlines():
        # OpenAI's response might still have periods instead of commas between step number and instruction
        instructions_row = instruction.replace(".", ",")
        instructions_row = instructions_row.split(",")

        step_number = instructions_row[0]
        instruction_text = instructions_row[1]

        instructions_data["Step"].append(step_number)
        instructions_data["Instruction"].append(instruction_text)

    return instructions_data


def create_csv_file(recipe_details: dict, recipe_number: int):
    try:
        # Create ingredients csv file
        ingredients_data = extract_ingredients_info(recipe_details["Ingredients"])
        df_ingredients = pd.DataFrame(ingredients_data)
        df_ingredients.to_csv(f"ingredients_csv/{recipe_number}.csv", index=False)

        # Create instructions csv file
        instructions_data = extract_instructions_data(recipe_details["Instructions"])
        df_instructions = pd.DataFrame(instructions_data)
        df_instructions.to_csv(f"instructions_csv/{recipe_number}.csv", index=False)
    except (ValueError, IndexError):
        # Create empty ingredients CSV file with "invalid_format" suffix if the response format is incorrect
        # Skip creating the ingredients csv file
        # The AI response often contains invalid formats, like missing commas between Quantity and Unit
        with open("invalid_format_recipes.txt", 'a') as file:
            file.write(f"Invalid format for recipe {recipe_number}.\nRecipe {recipe_number} details: {recipe_details}")

        df_empty = pd.DataFrame()
        df_empty.to_csv(f"ingredients_csv/{recipe_number}_invalid_format.csv", index=False)
