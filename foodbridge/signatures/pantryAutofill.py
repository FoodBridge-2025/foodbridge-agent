from typing import List
import dspy

class PantryAutofill(dspy.Signature):
    """
    Given webcontent, Fetch all possible Pantry information.
    We require the following information:
    - Pantry Name
    - Address
    - Phone Number
    - Operational Days 
    - Operational Hours
    If any of the above information is not found return unspecified
    """

    webContent: List[str] = dspy.InputField(description="Web content to be analyzed")
    pantryName: str = dspy.OutputField(description="Name of the pantry")
    pantryAddress: str = dspy.OutputField(description="Address of the pantry")
    pantryPhoneNumber: str = dspy.OutputField(description="Phone number of the pantry")
    operationalDays: str = dspy.OutputField(description="Days the pantry is operational")
    operationalHours: str = dspy.OutputField(description="Hours the pantry is operational")