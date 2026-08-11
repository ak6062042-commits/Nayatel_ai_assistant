#from llm.client import EmbeddingClient
#import json
#import chromadb
from pathlib import Path
import config
from rag.pipeline import Pipelines



class Ingenstion:
    def __init__(self):
        self.cleaned = []
        self.chunks = []
        self.loaded_files = []
    
    def runCleaning(self, force: bool = False) -> list:
        pipeline = Pipelines()
        if not Path(config.CLEANED_PATH).exists() or force:
            print(f"cleaned docs exists at: {config.CLEANED_PATH}\n Cleaning again...")
            
            self.loaded_files = pipeline.loadFiles(config.RAW_DATA_ROOT_DIR)
            self.cleaned = pipeline.cleaning(self.loaded_files)
            pipeline.storeCleaned(self.cleaned)
            print("cleaned data stored as .jsonl files")
            return self.cleaned
        
        self.cleaned = pipeline.loadCleaned()
        return self.cleaned
    
    def runChunking(self, force: bool = False) -> list:
        pipeline = Pipelines()
        
        if not Path(config.CHUNKS_PATH).exists() or force:
            print(f"chunk docs not exists at: {config.CHUNKS_PATH}\n Chunking again...")
            self.chunks = pipeline.loadCleaned()
            pipeline.initAndStoreChunks(self.chunks)
            return self.chunks
        
        self.chunks = pipeline.loadChunks()
        return self.chunks
    
    def runEmbedding(self, force: bool = False):
        return 