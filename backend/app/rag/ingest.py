from llm.client import EmbeddingClient
import json
from chromadb import PersistentClient
from pathlib import Path
import config
from rag.pipeline import UtilityPipelines



class Ingenstion:
    def __init__(self):
        self.cleaned = []
        self.chunks = []
        self.loaded_files = []
        self.retrived_cleaned_docs = []
    
    def runCleaning(self, force: bool = False):
        pipeline = UtilityPipelines()
        if not Path(config.CLEANED_PATH).exists() or force:
            print(f"cleaned-docs do-not exist at: {config.CLEANED_PATH}\n Cleaning and storing...")
            
            self.loaded_files = pipeline.loadFiles(config.RAW_DATA_ROOT_DIR)
            self.cleaned = pipeline.initCleaning(self.loaded_files)
            pipeline.storeCleaned(self.cleaned)
            self.retrived_cleaned_docs = pipeline.loadCleaned()
        
        self.retrived_cleaned_docs = pipeline.loadCleaned()
    
    def runChunking(self, force: bool = False):
        pipeline = UtilityPipelines()
        
        if not Path(config.CHUNKS_PATH).exists() or force:
            print(f"chunk-docs do-not exist at: {config.CHUNKS_PATH}\n Chunking and storing...")
            pipeline.initAndStoreChunks(self.retrived_cleaned_docs)
            self.chunks = pipeline.loadChunks()
        
        self.chunks = pipeline.loadChunks()
        
    def __initVectordb(self, client):
        collection = client.get_or_create_collection(name = config.COLLECTION_NAME)
        embedder = EmbeddingClient()
        text = [c["text"] for c in self.chunks]
        ids = [f'{c["source"]}_{c["page"]}_{c["chunk_index"]}' for c in self.chunks]
        metadatas = [
            {"source": c["source"], "page": c["page"], "category": c["category"], "chunk_index": c["chunk_index"]}
            for c in self.chunks
            ]
        embeddings = embedder.embed_batch(text)
        collection.add(ids = ids, embeddings = embeddings, metadatas = metadatas, documents = text)
        
    def VerifyVectordb(self, force: bool = False):
        
        if not Path(config.VECTOR_DB_PATH).exists():
            Path(config.VECTOR_DB_PATH).parent.mkdir(parents = True, exist_ok = True)
            
        client = PersistentClient(path = config.VECTOR_DB_PATH)
        existing = [c.name for c in client.list_collections()]
        
        if config.COLLECTION_NAME in existing:
            if force:
                client.delete_collection(config.COLLECTION_NAME)
                self.__initVectordb(client)
                return
            else:
                collection = client.get_collection(config.COLLECTION_NAME)
                if collection.count() == len(self.chunks):
                    print(f"vector db already has {collection.count()} matching chunk count, skipping embed")
                    return
                else:
                    print(f"Vectordb has {collection.count()}, expected {len(self.chunks)},")
                    client.delete_collection(config.COLLECTION_NAME)
                    self.__initVectordb(client)
                    return
        else:
            self.__initVectordb(client)
        
    def runIngestion(self, forced: bool = False):
        self.runCleaning(force = forced)
        self.runChunking(force = forced)
        self.VerifyVectordb(force = forced)

if __name__ == "__main__":
    ingest = Ingenstion()
    ingest.runIngestion(forced = False)