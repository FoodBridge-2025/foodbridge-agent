from typing import List
import dspy

class DebateAction(dspy.Signature):
    """
    Our goal is to find information about a food pantry. We need to find the pantry's location, operational days, and operational hours.
    Current page does not contain enough information.
    Given Clickable Elements and previous content, decide to going back to previous page or clicking one of the clickable elements.
    If previous page is empty you should not go back.
    If you decide to click, you should provide the index of the clickable element to click.
    """

    webContent: List[str] = dspy.InputField(description="Web Content of current page which does not contain enough information")
    actionButtons: str = dspy.InputField(description="Clickable Elements on the current page")
    previousWebContent: str = dspy.InputField(description="Previous Web Content")
    action: str = dspy.OutputField(description="Action to be taken must be either: 'click' or 'back'")
    buttonIndex: int = dspy.OutputField(description="Index of the button to be clicked")
