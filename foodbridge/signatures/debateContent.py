from typing import List
import dspy

class DebateContent(dspy.Signature):
    """
    Given webcontent, decide if it contains enough pantry information.
    We require the following information:
    - Pantry Location
    - Pantry Operational Days and Hours
    If the information is found, info_found should be set to True. Else, info_found should be set to False.
    If the information is found, fill in the pantryLocation, operationalDays, and operationalHours fields.
    the page can have multiple pantries, in that case, any pantry information can be selected.
    """

    webContent: List[str] = dspy.InputField(description="Web content to be analyzed")
    pantryLocation: str = dspy.OutputField(description="Location of the pantry")
    operationalDays: str = dspy.OutputField(description="Days the pantry is operational")
    operationalHours: str = dspy.OutputField(description="Hours the pantry is operational")
    info_found: bool = dspy.OutputField()
