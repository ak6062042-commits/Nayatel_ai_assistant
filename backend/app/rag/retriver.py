from chromadb import PersistentClient
from llm.client import EmbeddingClient
import config as config

class Retriver:
    def __init__(self, db_path: str = config.VECTOR_DB_PATH, collection_name: str = config.COLLECTION_NAME):
        client = PersistentClient(path = db_path)
        try:
            self.collection = client.get_collection(name = collection_name)
        except Exception as e:
            raise RuntimeError(f"Collection '{collection_name}' not found at {db_path}. ")
        self.embedder = EmbeddingClient()
    
    def unpackResults(self, results_found) -> list:
        found = []
        ids = results_found["ids"][0]
        docs = results_found["documents"][0]
        meta = results_found["metadatas"][0] 
        dis = results_found["distances"][0]
        
        for i in range(len(ids)):
            found.append({"ids":ids[i],
                            "text": docs[i],
                            "source": meta[i]["source"],
                            "page":meta[i]["page"],
                            "category": meta[i]["category"],
                            "chunk_index": meta[i].get("chunk_index"),
                            "score": dis[i]})
        return found
    
    def expandContext(self, found: dict, expansion: int ) -> dict:
        if found["chunk_index"] is None:
            return found
        
        origin = found["chunk_index"]
        upper_origin, below_origin = origin - expansion, origin + expansion
        same_category_docs = self.collection.get(where = {"source": found["source"]}, include = ["metadatas", "documents"])
        
        neighbors = []
        for doc_text, meta in zip(same_category_docs["documents"], same_category_docs["metadatas"]):
            index = meta.get("chunk_index")
            if index is not None and upper_origin <= index <= below_origin:
                neighbors.append((index, doc_text))
        
        neighbors.sort(key= lambda x: x[0])
        expand_text = " ".join(text for _, text in neighbors)
        
        expand_found = dict(found)
        expand_found["text"] = expand_text
        expand_found["expanded"] = True
        
        return expand_found
    
    def retrive(self, query: str, top_k: int = config.TOP_K, expansion: int = config.RETRIVE_NEIGHBORS) -> list:
        if not query or not query.strip():
            return []
        
        query_embed = self.embedder.embed(query)
        result = self.collection.query(query_embeddings = [query_embed], n_results = top_k)
        found = self.unpackResults(result)
        
        if expansion > 0:
            found = [self.expandContext(f, expansion) for f in found]
        return found
        
        
        
        
    
    