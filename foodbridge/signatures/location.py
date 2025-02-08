from typing import List
import dspy

class Location(dspy.Signature):
    """
        All locations are within the United States.
        Users are trying to find food in a specific location.
        Extract a city or county and a area from the given input.
        Areas ares usually neighborhoods, landmarks, or specific locations within a city or county.
        If a city/county or a area can not be inferred, the confidence will be low.
        Area is optinal and does not affect the confidence score, in case its not found set it to unspecified.
        If only area can be inferred not but the city or county, only_area will be set to True and confidence should be high.
        City/County and Area should only have the name of the location, no other information.
    """

    history: List[str] = dspy.InputField(description="Conversation History")
    sentence: str = dspy.InputField(description="Current user input")
    city: str = dspy.OutputField(description="City or County")
    area: str = dspy.OutputField(description="Area within city or county")
    confidence: float = dspy.OutputField()
    only_area: bool = dspy.OutputField(description="Only area could be inferred")

class ClarifyLocation(dspy.Signature):
    """
    Given the user input we were not able to determine (city/county) or area.
    Ask a clarifying question to get either a city/county or an area.
    If the user input is completely unrelated, ask for a location politely.
    In case the area is specified but city/county is unknown, suggest city/county names which the area may belong to.
    """

    history: List[str] = dspy.InputField(description="Conversation History")
    user_input: str = dspy.InputField(description="Given this was previous user input: Ask for clarification on location.")
    area: str = dspy.InputField()
    question: str = dspy.OutputField()