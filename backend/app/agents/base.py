from abc import ABC, abstractmethod
from openai import OpenAI
from ..core.config import get_settings
import json

settings = get_settings()

class BaseAgent(ABC):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.GPT_MODEL
    
    async def _get_completion(self, prompt: str, system_message: str = None) -> str:
        try:
            # Always append JSON request to the prompt
            json_prompt = f"{prompt}\n\nYou must respond with a valid JSON object. No other text or explanation should be included."
            
            messages = []
            if system_message:
                messages.append({
                    "role": "system", 
                    "content": f"{system_message}\nYou must respond with valid JSON only."
                })
            messages.append({"role": "user", "content": json_prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Get the response content
            content = response.choices[0].message.content
            
            # Validate JSON
            try:
                # Try parsing to ensure it's valid JSON
                json.loads(content)
                return content
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {content}")
                raise ValueError("Invalid JSON response from OpenAI")
                
        except Exception as e:
            print(f"Error in OpenAI API call: {str(e)}")
            raise
    
    @abstractmethod
    async def process(self, *args, **kwargs):
        """Process method to be implemented by each agent"""
        pass 