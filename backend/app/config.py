from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent         
BACKEND_DIR = BASE_DIR.parent                          

SENTENCES_PER_CHUNK = 6

RAW_DIR = BACKEND_DIR / "data" / "raw"
CLEANED_PATH = BACKEND_DIR / "data" / "processed" / "cleaned" / "cleaned.jsonl"
CHUNKS_PATH = BACKEND_DIR / "data" / "processed" / "chunks" / "chunks.jsonl"
VECTOR_DB_PATH = BACKEND_DIR / "data" / "processed" / "vector_db"
COLLECTION_NAME = "nayatel_docs"

TEMPERATURE = 1
MAX_TOKEN = 1200
MODEL_VERSION = "gpt-5-mini"

ENV_PATH = BACKEND_DIR / ".env"

RETRIVE_NEIGHBORS = 0
RAW_DATA_ROOT_DIR = RAW_DIR
TOP_K = 5
SIMILARITY_THRESHOLD = 1.15
KEEP_CHAT_SESSIONS = 10
CHUNK_SIZE = 650
OVERLAP = 80