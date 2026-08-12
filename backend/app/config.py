from os.path import dirname, join

BASE_DIR = dirname(__file__)
SENTENCES_PER_CHUNK = 6
RAW_DIR = join(BASE_DIR, "..\\data\\raw")
CLEANED_PATH = join(BASE_DIR, "..\\data\\processed\\cleaned\\cleaned.jsonl")
CHUNKS_PATH = join(BASE_DIR,"..\\data\\processed\\chunks\\chunks.jsonl")
VECTOR_DB_PATH = join(BASE_DIR,"..\\data\\processed\\vector_db")
COLLECTION_NAME = "nayatel_docs"
TEMPERATURE = 1
MAX_TOKEN = 1200
MODEL_VERSION = "gpt-5-mini"
ENV_PATH = join(BASE_DIR, "../.env")
RETRIVE_NEIGHBORS = 0
RAW_DATA_ROOT_DIR = join(BASE_DIR, "..\\data\\raw")
TOP_K = 5
SIMILARITY_THRESHOLD = 1.15
KEEP_CHAT_SESSIONS = 10
CHUNK_SIZE = 650
OVERLAP = 80

