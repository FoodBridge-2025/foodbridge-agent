from typing import List
import dspy
from selenium.webdriver.remote.webelement import WebElement

from ..signatures.pantryAutofill import PantryAutofill


class PantryContentExtractor(dspy.Module):
    def __init__(self, webContent:List[str]):
        self.webContent:List[str] = webContent
        self.extractContent = dspy.ChainOfThought(PantryAutofill)
    
    def forward(self):
        return self.extractContent(webContent=self.webContent)