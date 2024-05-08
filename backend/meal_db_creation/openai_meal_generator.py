import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI


def retrieve_recipe_details(recipe_file_path):
    df = pd.read_excel(recipe_file_path)
    informal_name = df["Informal Name"].tolist()

    # Remove suffix number from informal name
    dish_types = [name[:-1].strip() for name in informal_name]
    dish_names = df["Generated Name"].tolist()
    numbers = df["Number"].tolist()

    recipe_details = {
        "dish_types": dish_types,
        "dish_names": dish_names,
        "numbers": numbers
    }

    return recipe_details


def generate_ingredients_and_instructions(dish_type: str, dish_name:str , number: int) -> dict:
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
                - For the "Instructions" key:
                  - Return a string where each instruction is separated by a newline character ('\\n').
                  - Each instruction should be in the format: "step_number,instruction".
            
                For example, the response should follow this structure:
                {
                    "Ingredients": "Black olives,1,cup\\nCapers,2,tablespoons",
                    "Instructions": "1,Peel the carrots and dice finely\\n2,In a skillet, melt the butter"
                }
            
                Make sure that the response is accurate, concise, and follows this structure.
                
                Additionally, any temperatures should be expressed in Fahrenheit only and quantity should be expressed
                in decimal form. If the particular recipe dish is straightforward like toast, the instructions can just
                be an empty string "".
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
    print(parsed_response)
    return parsed_response


def create_csv_file(recipe_details: dict, recipe_number: int):


def main():
    recipe_details = retrieve_recipe_details("recipe_names/basic_starches.xlsx")

    test_counter = 2

    for i in range(test_counter):
        dish_type = recipe_details["dish_types"][i]
        dish_name = recipe_details["dish_names"][i]
        number = int(recipe_details["numbers"][i])

        recipe_details_dict = generate_ingredients_and_instructions(dish_type, dish_name, number)
        create_csv_file(recipe_details_dict, number)


if __name__ == "__main__":
    main()
