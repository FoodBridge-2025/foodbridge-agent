from .chat import Chat

class TerminalChat(Chat):

    def takeInput(self) -> str:
        user_input = input()
        return user_input

    def getOutput(self, output: str) -> None:
        print(output)