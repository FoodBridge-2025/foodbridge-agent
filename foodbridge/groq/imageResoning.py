import os
from typing import List

import dspy
from foodbridge.signatures.DebateQuality import DebateQuality as DebateQualitySignature
from foodbridge.vectorDb.FoodDb import FoodDb
from flask import json
from groq import Groq
import base64

def parse_nutrition_data(data_string):
    # Remove the outer quotes if present
    data_string = data_string.strip("'")
    
    # Split the string into individual components
    components = data_string.split("|")
    
    # Dictionary to store the parsed data
    nutrition_data = ""
    
    for component in components:
        if not component:
            continue
            
        # Extract the parts using split
        parts = component.split("amount:")
        if len(parts) != 2:
            continue
            
        # Get food component name
        food_comp = parts[0].replace("food component:", "").strip()
        
        # Split the second part to get amount and unit
        amount_unit = parts[1].split("unit:")
        if len(amount_unit) != 2:
            continue
        
        amount = amount_unit[0].strip()
        amount_conv = 0 

        try:
            amount_conv = float(amount)
        except:
            continue

        if amount_conv < 20:
            continue

        nutrition_data += f"|{food_comp} - {amount_conv}| "
    
    return nutrition_data

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_output(image_path) -> str:
    base64_image = encode_image(image_path)

    client = Groq(api_key=os.getenv('API_KEY_GROQ'))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify food Items and ESTIMATE their weights. Return a list of food items and their weights (in grams or Ounces). Output must be in a valid JSON format. JSON format: {food_items : [{'food_name': 'food_name1', 'weight': 'weight_value1'}, {'food_name': 'food_name2', 'weight': 'weight_value2'}]}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
        temperature=0.8,
        max_completion_tokens=512,
        response_format={"type": "json_object"},
        top_p=1,
        stream=False,
        stop=None,
    )

    print(chat_completion.choices[0].message.content)
    if chat_completion.choices[0].message.content:
        return  chat_completion.choices[0].message.content
    return "Can't Parse Image"

def parseImageOutput(image_output):
    output = image_output
    if output == "Can't Parse Image":
        return output
    try:
        food_db = FoodDb()
        food_items = json.loads(output)["food_items"]
        if len(food_items) > 3:
            food_items = food_items[:3]
        food_names = [food_item["food_name"] for food_item in food_items]
        food_weights = [food_item["weight"] for food_item in food_items]
        food_fact = {}
        sol:List[str] = []


        for food_name in food_names:
            food_dict = food_db.search_similar_foods(food_name, n_results=1)
            if len(food_fact) > 3: break
            for key, value in food_dict.items():
                if key not in food_fact:
                    try:
                        value = parse_nutrition_data(value)
                    except(Exception) as e:
                        print(e)
                    food_fact[key] = value
        
        for key, value in food_fact.items():
            sol.append(f"|| item - {key} : nuitrition {value} ||")

        return sol, food_names, food_weights
    except Exception as e:
        print(e)
        return "Vector DB Error"

def reason_image(iamge_path) -> str:
    image_output = get_image_output(iamge_path)
    context, food_names, food_weights = parseImageOutput(image_output)
    if (context == "Vector DB Error" or context == "Can't Parse Image") and type(context) == str:
        return context
    # try:
    #     client = Groq(api_key=os.getenv('API_KEY_GROQ'))
    #     completion = client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "user",
    #                   "content": f"""
    #                       I have the following food items and their associated weights (in grams or oz) {image_output}
    #                       Here are the nutritional information about similar food items: {context} 
    #                       Rate the nutritional value of the food items on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.
    #                       Justify your rating with a reasoning.
    #                       Do not name the identified food items in your reasoning.
    #                       There should be only one rating for all the food items.
    #                       Output Json format: {"{'rating': 'rating_value', 'reasoning': 'reasoning'}"}
    #                       Output must be in a valid JSON format.
    #                   """
    #             }
    #         ],
    #         model="llama-3.1-8b-instant",
    #         temperature=0.5,
    #         max_completion_tokens=1024,
    #         top_p=1,
    #         stop=None,
    #         stream=False,
    #         response_format={"type": "json_object"},
    #     )
    #     # completion = client.chat.completions.create(
    #     #     model="deepseek-r1-distill-llama-70b",
    #     #     messages=[
    #     #         {
    #     #             "role": "user",
    #     #              "content": f"""
    #     #                  I have the following food items and their associated weights (in grams or oz) {image_output}
    #     #                  Here are the nutritional information about similar food items: {context} 
    #     #                  Rate the nutritional value of the food items on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.
    #     #                  Output Json format: {"{'rating': 'rating_value'}"}
    #     #                  Output must be in a valid JSON format.
    #     #              """
    #     #         }
    #     #     ],
    #     #     temperature=0.6,
    #     #     max_completion_tokens=512,
    #     #     top_p=0.95,
    #     #     stream=False,
    #     #     response_format={"type": "json_object"}
    #     # )
    #     print(completion.choices[0].message.content)
    #     if completion.choices[0].message.content:
    #         return completion.choices[0].message.content
    #     return "Can't Parse Image"
    # except(Exception) as e:
    #     print(e)
    #     return "Can't Parse Image"
    try:
        rate = dspy.Predict(DebateQualitySignature)
        print("waiting on the model")
        response = rate(food_items=food_names, food_weights=food_weights, context=context)
        sol = "{'rating':" +  str(response.rating) + ", 'reasoning':" + str(response.reasoning) +"}"
        return sol
    except(Exception) as e:
        print(e)
        return "Can't Parse Image"
