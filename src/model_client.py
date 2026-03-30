import google.generativeai as genai
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Config.API_KEY)
        # Try multiple model options
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except:
                self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"