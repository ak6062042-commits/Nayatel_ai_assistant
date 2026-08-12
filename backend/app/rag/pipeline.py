import pymupdf as fitz
from pathlib import Path
from glob import glob
from datetime import datetime
import re
import json
import config
from rag.retriver import Retriver
from llm.client import LLMClient
from rag.prompt import buildPrompt
from rag.history import History


class UtilityPipelines:
    
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
    
    def initCleaning(self, loaded_files: list) -> list:
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
    
    def storeCleaned(self, cleaned_text: list, path: str = config.CLEANED_PATH):
        Path(path).parent.mkdir(parents = True, exist_ok = True)
        with open(path, "w", encoding = "utf-8") as f:
            for docs in cleaned_text:
                f.write(json.dumps(docs, ensure_ascii = False) + "\n")
        f.close()

    def loadCleaned(self, path: str = config.CLEANED_PATH)-> list:
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
    
    def make_chunks(self, cleaned_docs: list, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.OVERLAP, sentences_per_chunk: int = config.SENTENCES_PER_CHUNK, by_sentences: bool = False, by_tokens: bool = False) -> list:
        from itertools import groupby
        _chunks = []
        if by_sentences:
            for source, pages in groupby(cleaned_docs, key = lambda d: d["source"]):
                idx = 0
                for page_entry in pages:
                    sentences = self.sentenceSplit(page_entry["text"])
                    for i in range(0, len(sentences), sentences_per_chunk):
                        group = sentences[i:i + sentences_per_chunk]
                        _chunks.append({
                            "text": " ".join(group),
                            "source": source,
                            "page": page_entry["page"],
                            "category": page_entry["category"],
                            "chunk_index": idx,
                        })
                        idx += 1
        if by_tokens:
            import tiktoken
            encoder = tiktoken.get_encoding("cl100k_base")
            for source, pages in groupby(cleaned_docs, key=lambda d: d["source"]):
                pages = list(pages)
                full_text = ""
                page_boundaries = []  
                for p in pages:
                    page_boundaries.append((len(full_text), p["page"]))
                    full_text += p["text"] + " "

                category = pages[0]["category"]
                tokens = encoder.encode(full_text)

                idx = 0
                start = 0
                while start < len(tokens):
                    end = min(start + chunk_size, len(tokens))
                    chunk_tokens = tokens[start:end]
                    chunk_text = encoder.decode(chunk_tokens)

                    char_offset = len(encoder.decode(tokens[:start]))
                    page_num = self._page_for_offset(char_offset, page_boundaries)

                    _chunks.append({
                        "text": chunk_text.strip(),
                        "source": source,
                        "page": page_num,
                        "category": category,
                        "chunk_index": idx,})
                    idx += 1
                    start += chunk_size - overlap  
        return _chunks
    
    def _page_for_offset(self, char_offset: int, page_boundaries: list) -> int:
        page = page_boundaries[0][1]
        for offset, pnum in page_boundaries:
            if offset <= char_offset:
                page = pnum
            else:
                break
        return page
    
    def initAndStoreChunks(self , cleaned_docs: list, path: str = config.CHUNKS_PATH):
        Path(path).parent.mkdir(parents = True, exist_ok = True)
        with open(path, "w", encoding = "utf-8") as f:
            chunks = self.make_chunks(cleaned_docs, by_tokens = True)
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii = False) + "\n")
        f.close()
    
    def loadChunks(self, path: str = config.CHUNKS_PATH):
        if not Path(path).exists():
            raise FileNotFoundError(f"chunk directory not found at: {path}")
        chunk = []
        with open(path, "r", encoding = "utf-8") as f:
            for line in f:
                chunk.append(json.loads(line))
        f.close()
        return chunk


# TO DO: Document and test thoroughly for Bugs (done(the bug part[there were quite a few]))
    
class RagPipelines:
    def __init__(self, retriver: Retriver, llm_client: LLMClient, history: History, similarity_threshold: float = config.SIMILARITY_THRESHOLD, top_k: int = config.TOP_K):
        self.retriver = retriver
        self.llm_client = llm_client
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.history = history
    
    def buildContext(self, found: list) -> list:
        return "\n\n".join(f'{f["text"]}' for f in found)
    
    def isRelevant(self, found: list) -> bool:
        best_score = min(f["score"] for f in found)
        return best_score <= self.similarity_threshold
    
    def formatSource(self, found: list) -> list:
        seen = set()
        sources = []
        for f in found:
            key = (f["source"], f["page"])
            
            if key not in seen:
                seen.add(key)
                sources.append({"title": f["source"], "page": f["page"]})
        return sources
    
    def recordTurn(self, session_id: str, user_msg: str, assistant_msg: str):
        self.history.addMessage(session_id, "user", user_msg)
        self.history.addMessage(session_id, "assistant", assistant_msg)
    
    def buildRetrivalQuery(self, query: str, session_id: str) -> str:
        history = self.history.getHistory(session_id)
        last_user_msg = next((h["content"] for h in reversed(history) if h["role"] == "user" ), "")
        return f"{last_user_msg} {query}".strip() if last_user_msg else query
    
    def queryParsing(self, query: str) -> str:
        query = re.sub(r"\s+", " ", query)
        query = re.sub(r"•|●|▪", "-", query)
        return query.strip()
    
    def answer(self, query: str, session_id: str) -> dict:
        if not query:
            return {"answer": "please enter a question!!!", "source": []}
        query = self.queryParsing(query)
        conversation = self.history.buildConversationString(session_id)
        retrival_query = self.buildRetrivalQuery(query, session_id)
        
        found = self.retriver.retrive(retrival_query)
        if not found or not self.isRelevant(found):
            answer_text = "I don't have enough information to answer that. Please contact NayaTel support."
            self.recordTurn(session_id, query, answer_text)
            return {"answer": answer_text, "source": []}
        
        context = self.buildContext(found)
        prompt = buildPrompt(query, context, conversation)
        
        try:
            raw_answer = self.llm_client.generate(prompt)
        except Exception as e:
            generation_failed = f"llm client error: {e}" + "sorry unable to processes prompt at this moment"
            return {"answer": generation_failed, "source": []}
        self.recordTurn(session_id, query, raw_answer)
        
        return {"answer": raw_answer, "source" : self.formatSource(found)}
            
        