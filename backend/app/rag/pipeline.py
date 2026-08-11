import fitz
from pathlib import Path
from glob import glob
from datetime import datetime
import re
import json
from config import SENTENCES_PER_CHUNK


class Pipelines:
    
    def __init__(self):
        self.loaded_files = []
        self.cleaned_text = []
    
    def loadFiles(self, root_dir: str) -> list:
        pdf_dir = Path(root_dir)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"data directory does not exist in the passed path: {root_dir}")
        
        pdf_paths = pdf_dir.glob("**/*.pdf")
        
        for paths in pdf_paths:
            try:
                docs = fitz.open(paths)
                self.loaded_files.append({"path": paths,
                                "filename": paths.name,
                                "document": docs,
                                "total_pages": len(docs)})
            
            except Exception as e:
                print(f"error opening file at {paths}, {e}")
        
        return self.loaded_files
                
    def inferCategory(self, path: Path) -> str:
        return path.parent.name.lower().strip()
    
    def cleanText(self, text: str) -> str:
        if not text:
            return ""
        
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"•|●|▪", "-", text)

        return text.strip()
    
    def cleaning(self, loaded_files: list) -> list:
        if not loaded_files:
            raise ValueError("missing filr data")
        
        for entry in loaded_files:
            documents = entry["document"]
            path = entry["path"]
            category = self.inferCategory(path)
            
            for page_num in range(len(documents)):
                text = self.cleanText(documents[page_num].get_text())
                
                if not text:
                    continue
                
                self.cleaned_text.append({"text": text,
                                        "source": entry["filename"], 
                                        "page": page_num + 1, 
                                        "category": category})
        return self.cleaned_text
    
    def storeCleaned(self, cleaned_text: list, path: str = "../data/processed/cleaned/cleaned_docs.jsonl"):
        Path(path).parent.mkdir(parents = True, exist_ok = True)
        with open(path, "w", encoding = "utf-8") as f:
            for docs in cleaned_text:
                f.write(json.dumps(docs, ensure_ascii = False) + "\n")
        f.close()

    def loadCleaned(self, path: str = "../data/processed/cleaned/cleaned_docs.jsonl")-> list:
        if not Path(path).exists():
            raise FileNotFoundError(f"cleaned_text directory not found at: {path}") 
        docs = []
        with open(path, "r", encoding = "utf-8") as f:
            for lines in f:
                docs.append(json.loads(lines))
        f.close()
        return docs
    
    def sentenceSplit(self, text: str) -> list:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def make_micro_chunks(self, cleaned_docs: list, sentences_per_chunk: int = SENTENCES_PER_CHUNK) -> list:
        from itertools import groupby
        micro_chunks = []

        for source, pages in groupby(cleaned_docs, key = lambda d: d["source"]):
            idx = 0
            for page_entry in pages:
                sentences = self.sentenceSplit(page_entry["text"])
                for i in range(0, len(sentences), sentences_per_chunk):
                    group = sentences[i:i + sentences_per_chunk]
                    micro_chunks.append({
                        "text": " ".join(group),
                        "source": source,
                        "page": page_entry["page"],
                        "category": page_entry["category"],
                        "chunk_index": idx,
                    })
                    idx += 1
        return micro_chunks
    
    def initAndStoreChunks(self , cleaned_text: list, path: str = "../data/processed/chunks/chunks.jsonl"):
        Path(path).parent.mkdir(parents = True, exist_ok = True)
        with open(path, "w", encoding = "utf-8") as f:
            chunks = self.make_micro_chunks(cleaned_text)
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii = False) + "\n")
        f.close()
    
    def loadChunks(self, path: str = "../data/processed/chunks/chunks.jsonl"):
        if not Path(path).exists():
            raise FileNotFoundError(f"chunk directory not found at: {path}")
        chunk = []
        with open(path, "r", encoding = "utf-8") as f:
            for line in f:
                chunk.append(json.loads(line))
        f.close()
        return chunk


# TO DO: Document and test thoroughly for Bugs
    
        
                
        