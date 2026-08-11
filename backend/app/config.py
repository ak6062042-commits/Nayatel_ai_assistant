from os.path import dirname, join

BASE_DIR = dirname(__file__)
SENTENCES_PER_CHUNK = 2
RAW_DIR = join(BASE_DIR, "..\\data\\raw")
CLEANED_PATH = join(BASE_DIR, "..\\data\\processed\\cleaned\\cleaned.jsonl")
CHUNKS_PATH = join(BASE_DIR,"..\\data\\processed\\chunks\\chunks.jsonl")
VECTOR_DB_PATH = join(BASE_DIR,"..\\data\\processed\\vector_db")
COLLECTION_NAME = "nayatel_docs"
TEMPERATURE = 0.3
MAX_TOKEN = 300
MODEL_VERSION = "gpt-5-mini"
ENV_PATH = "../.env"
RETRIVE_NEIGHBORS = 4
RAW_DATA_ROOT_DIR = join(BASE_DIR, "..\\data\\raw")
TOP_K = 5
SIMILARITY_THRESHOLD = 0.7
KEEP_CHAT_SESSIONS = 10

