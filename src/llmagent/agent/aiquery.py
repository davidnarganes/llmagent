import logging
from typing import Optional, List
import openai
import os
from anthropic import AnthropicBedrock
from dotenv import load_dotenv
import os

load_dotenv()

class AIQueryClient:
    def __init__(self, provider: str):
        self.provider = provider.lower()
        if self.provider == 'openai':
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                raise ValueError("OpenAI API key is not set in environment variables.")
        elif self.provider == 'anthropic':
            self.claude_client = AnthropicBedrock()
        else:
            raise ValueError("Unsupported provider. Please use 'openai' or 'anthropic'.")

    def query(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int = 100, 
        stop_sequences: Optional[List[str]] = ["```\n"], 
        temperature: float = 0, 
        top_k: int = 1
    ) -> Optional[str]:
        try:
            if self.provider == 'openai':
                return self.query_openai(model, prompt, max_tokens, stop_sequences, temperature)
            elif self.provider == 'anthropic':
                return self.query_anthropic(model, prompt, max_tokens, stop_sequences, temperature, top_k)
            else:
                logging.error(f"Unsupported provider: {self.provider}")
                return None
        except Exception as e:
            logging.error(f"Error querying {self.provider}: {e}")
            return None

    def query_openai(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int, 
        stop_sequences: Optional[List[str]], 
        temperature: float
    ) -> Optional[str]:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stop=stop_sequences,
                temperature=temperature
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logging.error(f"Error querying OpenAI: {e}")
            return None

    def query_anthropic(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int, 
        stop_sequences: Optional[List[str]], 
        temperature: float, 
        top_k: int
    ) -> Optional[str]:
        try:
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                stop_sequences=stop_sequences,
                temperature=temperature,
                top_k=top_k,
            )
            return response.content[0].text.strip()
        except Exception as e:
            logging.error(f"Error querying Anthropic: {e}")
            return None

if __name__ == '__main__':
    
    # Example usage:
    client = AIQueryClient(provider='openai')
    response = client.query(model='gpt-3.5-turbo', prompt='Hello, world!', max_tokens=50)
    print(response)

    # client = AIQueryClient(provider='anthropic')
    # response = client.query(model='anthropic.claude-3-sonnet-20240229-v1:0', prompt='Hello, world!', max_tokens=50)
    # print(response)
