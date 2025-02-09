from typing import List, Tuple
import dspy

class DebateQuality(dspy.Signature):
    """
        I have the food items and their associated weights (in grams or oz)
        Here are the nutritional information about similar food items: {context} 
        Rate the nutritional value of the food items on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.
        Justify your rating with a reasoning.
        There should be only one rating for all the food items.
        Output Json format: {"{'rating': 'rating_value', 'reasoning': 'reasoning'}"}
        Output must be in a valid JSON format.
    """

    food_items: List[str] = dspy.InputField(description="Food items")
    food_weights: List[str] = dspy.InputField(description="Weights of the food items")
    context: List[str] = dspy.InputField(description="Nutritional information about similar food items")
    rating: int = dspy.OutputField(description="Rate the nutritional value of the food items on a scale of 1 to 5")
    reasoning: str = dspy.OutputField(description="Justify your rating with a reasoning")