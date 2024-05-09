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
                The user will provide you 2 things for a cooking recipe: 
                1. The recipe type (e.g. rice dish, chicken dish, etc), 
                2. The recipe name (e.g. fried rice, chicken curry, etc), 
                Please generate the ingredients and instructions for the recipe given. 
                
                Please provide the response in a JSON format with the following structure:
                - The object should start with '{' and end with '}'.
                - Include two keys: "Ingredients" and "Instructions".
                - For the "Ingredients" key:
                  - Return a string where each ingredient is separated by a newline character ('\\n').
                  - Each ingredient should be in the format: "ingredient_name,quantity,unit".
                  - Ensure that each ingredient has a quantity and a unit separated by a comma ','. For ingredients 
                    that don't have a measurement unit like ounces, teaspoons, etc, use your best judgement for a 
                    replacement. If unsure, an empty string "" can be used.
                - For the "Instructions" key:
                  - Return a string where each instruction is separated by a newline character ('\\n').
                  - Each instruction should be in the format: "step_number,instruction".
                  - Make sure there's a comma between the step number and the instruction and not period.
                  - Any temperatures should be expressed in Fahrenheit only. 
                  - If the particular recipe dish is straightforward like toast, the instructions can just be an 
                    empty string "".
            
                For example, the response should follow this structure:
                {
                    "Ingredients": "Black olives,1,cup\\nGarlic,2,cloves",
                    "Instructions": "1,Peel the carrots and dice finely\\n2,In a skillet, melt the butter"
                }
            
                Make sure that the response is accurate, concise, and follows this structure.
                """
            },
            {
                "role": "user",
                "content": f"I have a {dish_type} recipe named {dish_name}."
                           f"Please generate the ingredients and instructions for me."
            }
        ],
    )

    response_content = chat_completion.choices[0].message.content
    parsed_response = json.loads(response_content)
    # print(parsed_response)
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
    # Create ingredients csv file
    ingredients_data = extract_ingredients_info(recipe_details["Ingredients"])
    df_ingredients = pd.DataFrame(ingredients_data)
    df_ingredients.to_csv(f"ingredients_csv/{recipe_number}.csv", index=False)

    # Create instructions csv file
    instructions_data = extract_instructions_data(recipe_details["Instructions"])
    df_instructions = pd.DataFrame(instructions_data)
    df_instructions.to_csv(f"instructions_csv/{recipe_number}.csv", index=False)


def main():
    recipe_details = retrieve_recipe_details("recipe_names/new_recipes.xlsx")

    start_number = 200838  # Change this to the recipe number you want to start from

    # Find the index of the start number
    start_index = recipe_details["Number"].index(start_number)

    # Otherwise, use this for the for loop range
    rows = len(recipe_details["Number"])

    for i in range(start_index, rows):
        dish_type = recipe_details["Informal Name"][i]
        dish_name = recipe_details["Generated Name"][i]
        number = int(recipe_details["Number"][i])

        recipe_details_dict = generate_ingredients_and_instructions(dish_type, dish_name, number)
        create_csv_file(recipe_details_dict, number)


if __name__ == "__main__":
    main()
