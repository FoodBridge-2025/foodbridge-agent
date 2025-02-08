from abc import abstractmethod


class Chat:
    
    @abstractmethod
    def takeInput(self) -> str:
        pass

    @abstractmethod
    def printOutput(self, output: str) -> None:
        pass