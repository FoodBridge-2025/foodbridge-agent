from typing import List
import dspy
from selenium.webdriver.remote.webelement import WebElement

from foodbridge.signatures.debateAction import DebateAction
from ..search.search import clickElement, getWebContent, goBack
from ..signatures.debateContent import DebateContent


class PantryLoop(dspy.Module):
    def __init__(self, links: List[str]):
        self.initial_links = [links[0]]
        self.webContent:List[str] = []
        self.previousPageContent:List[str] = []
        self.clickable_elements:List[WebElement] = []
        self.DebateContent = dspy.ChainOfThought(DebateContent)
        self.DebateAction = dspy.ChainOfThought(DebateAction)
    
    def forward(self):
        for start_link in self.initial_links:
            action_limit = 10
            self.webContent, self.clickable_elements_text, self.clickable_elements  = getWebContent(start_link)
            self.previousPage = self.webContent
            while(action_limit > 0):
                action_limit -= 1
                print(f"Fetching info for action: {10 - action_limit}")
                info = self.DebateContent(webContent=self.webContent)
                print(f"info for action {10 - action_limit} : {info}")
                if info.info_found:
                    return info
                print(f"Fetching next action for action: {10 - action_limit}")
                action = self.DebateAction(webContent=self.webContent, actionButtons=self.clickable_elements_text, previousWebContent=self.previousPage)
                print(f"action for action {10 - action_limit} : {action}") 
                if action.action == "click":
                    self.previousPage = self.webContent
                    clickElement(self.clickable_elements[action.buttonIndex])
                    self.webContent, self.clickable_elements_text, self.clickable_elements = getWebContent()
                else:
                    if len(self.previousPage) == 0:
                        break
                    self.previousPage = self.webContent
                    goBack()
                    self.webContent, self.clickable_elements_text, self.clickable_elements = getWebContent()

                
        