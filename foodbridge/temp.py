from typing import Literal
import dspy

class Classify(dspy.Signature):
    """Classify sentiment of a given sentence."""

    sentence: str = dspy.InputField()
    sentiment: Literal['positive', 'negative', 'neutral'] = dspy.OutputField()
    confidence: float = dspy.OutputField()