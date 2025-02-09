import os
import dspy
from dotenv import load_dotenv

load_dotenv()

lm = dspy.LM('ollama_chat/deepseek-r1:8b', api_base='http://localhost:11434', api_key='')
dspy.configure(lm=lm)