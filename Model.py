# Import necessary libraries
from google.generativeai import ChatSession
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import pandas as pd
import json
import os


# Path to your real API key
path = 'Key.key' # 
with open(path) as f:
    key = f.read().strip()

# Set your default model for Gemini
GEMINI_DEFFAULT_MODEL = 'gemini-1.5-flash'


# Class for interacting with the Gemini model
class GeminiModel:
    def __init__(self, model: str = ..., 
                 key: str = ..., 
                 safe_setting: dict[HarmCategory, HarmBlockThreshold] = ...) -> None:
        
        # Use the default model if none is provided
        if model == ...:
            model = GEMINI_DEFFAULT_MODEL
            
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE    
        }        
        self.model = genai.GenerativeModel(model)
        self.session = ChatSession(self.model)
        try:
            # Use the environment API key if none is provided
            if key == ...:
                self.key = os.environ["GEMINI_API_KEY"]
            else:
                self.key = key
        except:
            # Fallback key (replace with your actual key)
            raise ValueError('Invalid Gemini API key')
        genai.configure(api_key=self.key)
    def set_key(self, key):
        # Set a new API key
        self.key = key
        genai.configure(api_key=self.key)
    
    def response(self, text, prompt):
        # Send a message to the Gemini model and retrieve the response
        response = self.session.send_message(f"{prompt}\n{text}\n")
        final = ''
        for chunk in response:
            final += chunk.text + '\n'
        return final.strip()