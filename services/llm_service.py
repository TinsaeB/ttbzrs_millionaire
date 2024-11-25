import ollama
from typing import Dict, List
import asyncio
from datetime import datetime

class LLMService:
    def __init__(self, model_name: str = "llama3.2"):
        self.model = model_name
        
    async def get_response(self, prompt: str, context: str = "") -> Dict:
        try:
            full_prompt = f"""You are a financial advisor helping someone who just won a million dollars.
                        Previous context: {context}
                        User message: {prompt}
                        
                        Provide helpful, practical advice while keeping the conversation engaging and fun.
                        Focus on realistic financial planning while maintaining an optimistic tone."""
            
            response = ollama.chat(model=self.model, messages=[{
                'role': 'user',
                'content': full_prompt
            }])
            
            return {
                'status': 'success',
                'message': response['message']['content'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    async def analyze_document(self, text: str) -> Dict:
        try:
            prompt = f"""Analyze this financial document and provide key insights:
                        {text[:2000]}...
                        
                        Provide a brief summary and any relevant financial advice in the context of having won a million dollars."""
            
            response = ollama.chat(model=self.model, messages=[{
                'role': 'user',
                'content': prompt
            }])
            
            return {
                'status': 'success',
                'message': response['message']['content'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
