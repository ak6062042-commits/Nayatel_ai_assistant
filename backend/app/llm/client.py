from sentence_transformers import SentenceTransformer
import config
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
                max_tokens = maxtoken , temperature = max_temperature )
            return response.choices[0].messaage.content.strip()
    
        except Exception as e:
            print(f"llm generation failed: {e}")
            raise
        
        
class EmbeddingClient:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed(self, text: str) -> list:
        return self.model.encode(text).tolist()
        
    
    def embed_batch(self, texts: str) -> list:
        return self.model.encode(texts, batch_size = 32 , show_progress_bar = True).tolist()
        # trying batch_size = 32
        # TO DO: Try different batch sizes while testing to find optimal

