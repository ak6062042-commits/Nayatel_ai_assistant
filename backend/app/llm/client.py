#from sentence_transformers import SentenceTransformer
import app.config as config
from dotenv import load_dotenv
import os
from openai import OpenAI

class LLMClient:
    def __init__(self, model: str = config.MODEL_VERSION):
        env_path = config.ENV_PATH
        load_dotenv(dotenv_path = env_path)
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
        self.model = model
    
    def generate(self, prompt: str, maxtoken: int = config.MAX_TOKEN, max_temperature: float = config.TEMPERATURE):
        try:
            response = self.client.chat.completions.create( 
                model = self.model, messages = [{"role": "user", "content": prompt}], 
                max_completion_tokens = maxtoken , temperature = max_temperature, reasoning_effort = "minimal")
            return response.choices[0].message.content.strip()
    
        except Exception as e:
            print(f"llm generation failed: {e}")
            raise
        
        
class EmbeddingClient:
    def __init__(self, model_name: str = config.EMBEDDING_CLIENT):
        env_path = config.ENV_PATH
        load_dotenv(dotenv_path=env_path)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    def embed(self, text: str) -> list:
        response = self.client.embeddings.create(model = self.model_name, input=text)
        return response.data[0].embedding

    def embed_batch(self, texts: list) -> list:
        response = self.client.embeddings.create(model = self.model_name, input=texts)
        return [d.embedding for d in response.data]

