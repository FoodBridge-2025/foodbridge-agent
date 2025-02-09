from typing import Dict, List
import dspy
import dspy.primitives
from foodbridge.chatInputs.terminal_chat import TerminalChat
from foodbridge.signatures.location import Location as LocationSignature, ClarifyLocation

class Location(dspy.Module):
    def __init__(self):
        self.chat = TerminalChat()
        self.conversation:List[str] = []
        self.generate_location = dspy.Predict(LocationSignature)
        self.generate_query = dspy.Predict(ClarifyLocation)
        self.location_info = {"city": "", "area": ""}

    def forward(self) -> Dict[str, str]:
        while self.location_info["city"] == None or len(self.location_info["city"]) == 0:
            statement = self.chat.takeInput()
            follow_up = ""
            print(f"Finding locations from input")
            location_output = self.generate_location(sentence=statement, history=self.conversation)
            print(f"location output: {location_output}")
            if location_output.confidence < 0.5:
                query_output = self.generate_query(user_input=statement, area="unspecified", history=self.conversation)
                print(f"question gen output: {query_output}")
                self.chat.printOutput(query_output.question)
                follow_up = query_output.question
            elif location_output.only_area:
                query_output = self.generate_query(user_input=statement, area=location_output.area, history=self.conversation)
                self.location_info["area"] = location_output.area
                print(f"question gen output: {query_output}")
                self.chat.printOutput(query_output.question)
                follow_up = query_output.question
            elif location_output.city and location_output.city != "" and location_output.city != "unspecified":
                self.location_info["city"] = location_output.city
                if location_output.area and location_output.area != "" and location_output.area != "unspecified":
                    self.location_info["area"] = location_output.area
                self.location_info["city"] = location_output.city

            
            self.conversation.append("user :" + statement)
            if follow_up:
                self.conversation.append("bot :" + follow_up)
        
        return self.location_info