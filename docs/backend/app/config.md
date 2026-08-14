# config.py

## Path

`Nayatel.ai-assistant/backend/config.py`

## Purpose

`config.py` contains the main **configuration values** used throughout the Nayatel AI Assistant backend.

Instead of writing paths, model settings, RAG settings, and other fixed values directly inside different Python files, they are stored here so they can be changed from one place.

This makes the project easier to manage and avoids repeating the same values in multiple files.

---

## Technologies Used

### `os.path`

```python
from os.path import dirname, join
```

The `os.path` module provides functions for working with file and directory paths.

#### `dirname()`

`dirname()` returns the directory part of a given path.

Here:

```python
BASE_DIR = dirname(__file__)
```

`__file__` represents the current Python file, so `BASE_DIR` becomes the directory where `config.py` is located.

#### `join()`

`join()` is used to combine directory and file names into a path.

For example:

```python
RAW_DIR = join(BASE_DIR, "..\\data\\raw")
```

This creates a path relative to the location of `config.py`.

---

# Configuration Values

## `BASE_DIR`

```python
BASE_DIR = dirname(__file__)
```

Stores the directory containing `config.py`.

Other paths are built relative to this directory instead of depending on where the program is executed from.

This helps prevent path-related problems when running the application from different directories.

---

# Data Directories and Files

## `RAW_DIR`

```python
RAW_DIR = join(BASE_DIR, "..\\data\\raw")
```

Points to the directory containing the original/raw data used by the RAG pipeline.

This can include files such as:

* PDF documents
* Manuals
* Website data
* Other source documents

---

## `CLEANED_PATH`

```python
CLEANED_PATH = join(
    BASE_DIR,
    "..\\data\\processed\\cleaned\\cleaned.jsonl"
)
```

Defines the location where cleaned document data is stored.

The cleaned data is saved as a `.jsonl` file.

JSONL means **JSON Lines**, where each line contains a separate JSON object.

---

## `CHUNKS_PATH`

```python
CHUNKS_PATH = join(
    BASE_DIR,
    "..\\data\\processed\\chunks\\chunks.jsonl"
)
```

Defines where the processed document chunks are stored.

The RAG pipeline uses these chunks later when creating embeddings and retrieving relevant information.

---

## `VECTOR_DB_PATH`

```python
VECTOR_DB_PATH = join(
    BASE_DIR,
    "..\\data\\processed\\vector_db"
)
```

Defines the directory where the vector database data is stored.

The vector database is used to store embeddings of document chunks so that relevant chunks can be retrieved when a user asks a question.

---

## `RAW_DATA_ROOT_DIR`

```python
RAW_DATA_ROOT_DIR = join(BASE_DIR, "..\\data\\raw")
```

Points to the root directory of the raw data.

Currently, this is effectively the same location as `RAW_DIR`.

It may be kept separately because different parts of the pipeline may use the raw-data root for different purposes.

---

# Vector Database Configuration

## `COLLECTION_NAME`

```python
COLLECTION_NAME = "nayatel_docs"
```

Defines the name of the collection used in the vector database.

The collection represents the group of Nayatel document embeddings stored for retrieval.

Using a fixed name allows the application to consistently access the same collection.

---

# RAG Configuration

## `SENTENCES_PER_CHUNK`

```python
SENTENCES_PER_CHUNK = 6
```

Defines the target number of sentences used when creating a document chunk.

A document is split into smaller pieces before being embedded and stored in the vector database.

Using chunks instead of entire documents makes it easier for the retriever to find the specific information needed for a user query.

---

## `CHUNK_SIZE`

```python
CHUNK_SIZE = 650
```

Defines the configured chunk size used by the chunking process.

The exact meaning of this value depends on how the chunking code uses it, such as whether it represents characters or another unit.

It should therefore be kept consistent with the implementation of the chunking pipeline.

---

## `OVERLAP`

```python
OVERLAP = 80
```

Defines the amount of overlap between neighboring chunks.

Chunk overlap helps prevent useful information from being lost when a sentence or piece of context is split between two chunks.

For example:

```text
Chunk 1: A B C D E F
Chunk 2:       E F G H I J
```

The overlapping portion helps preserve context between chunks.

---

## `TOP_K`

```python
TOP_K = 5
```

Defines how many top results the retriever should return for a query.

For example, with:

```python
TOP_K = 5
```

the retriever attempts to return the five most relevant document chunks.

A higher value can provide more context but may also introduce less relevant information.

---

## `SIMILARITY_THRESHOLD`

```python
SIMILARITY_THRESHOLD = 1.15
```

Defines the similarity/distance threshold used when filtering retrieved results.

The exact interpretation depends on the vector database and similarity metric being used.

The value should therefore be understood together with the retriever implementation.

---

## `RETRIVE_NEIGHBORS`

```python
RETRIVE_NEIGHBORS = 0
```

Controls whether neighboring chunks around a retrieved chunk should also be retrieved.

With the current value:

```python
RETRIVE_NEIGHBORS = 0
```

no additional neighboring chunks are requested.

If this value is increased, the retriever can potentially include chunks surrounding the original result to provide additional context.

> Note: `RETRIVE_NEIGHBORS` is currently spelled `RETRIVE` rather than `RETRIEVE`. If this name is already used throughout the project, changing it would require updating those references as well.

---

# LLM Configuration

## `TEMPERATURE`

```python
TEMPERATURE = 1
```

Controls the randomness of the language model's generated responses.

Generally:

* Lower values produce more predictable responses.
* Higher values allow more variation.

The appropriate value depends on the type of response expected from the chatbot.

---

## `MAX_TOKEN`

```python
MAX_TOKEN = 1200
```

Defines the configured maximum number of tokens for the model's generated response.

This helps limit how long the generated answer can become.

The exact parameter name used when calling the model may differ depending on the API/client implementation.

---

## `MODEL_VERSION`

```python
MODEL_VERSION = "gpt-5-mini"
```

Defines the language model used by the chatbot.

Keeping the model name in `config.py` means it can be changed without modifying the main LLM/client implementation.

For example, switching models can be done by changing:

```python
MODEL_VERSION = "gpt-5-mini"
```

instead of searching through the rest of the project for the model name.

---

# Environment Configuration

## `ENV_PATH`

```python
ENV_PATH = join(BASE_DIR, "../.env")
```

Defines the location of the `.env` file.

The `.env` file can contain environment-specific configuration such as API keys and other secrets.

Sensitive values should **not** be hardcoded directly into `config.py`.

For example, an API key should generally be stored in `.env` rather than:

```python
API_KEY = "actual-secret-key"
```

---

# Chat Session Configuration

## `KEEP_CHAT_SESSIONS`

```python
KEEP_CHAT_SESSIONS = 10
```

Defines the configured number of chat sessions/history entries that the backend should keep.

The actual behavior depends on how the `History` class uses this value.

This is related to the backend-managed chat history system, where the frontend sends a `session_id` and the backend manages the conversation history.

---

# Configuration Summary

| Variable               | Purpose                                         |
| ---------------------- | ----------------------------------------------- |
| `BASE_DIR`             | Base directory of `config.py`                   |
| `SENTENCES_PER_CHUNK`  | Target sentences per chunk                      |
| `RAW_DIR`              | Location of raw documents                       |
| `CLEANED_PATH`         | Location of cleaned JSONL data                  |
| `CHUNKS_PATH`          | Location of chunked JSONL data                  |
| `VECTOR_DB_PATH`       | Location of vector database                     |
| `COLLECTION_NAME`      | Vector database collection name                 |
| `TEMPERATURE`          | LLM response randomness                         |
| `MAX_TOKEN`            | Maximum configured generated tokens             |
| `MODEL_VERSION`        | LLM model name                                  |
| `ENV_PATH`             | Location of `.env`                              |
| `RETRIVE_NEIGHBORS`    | Number of neighboring chunks to retrieve        |
| `RAW_DATA_ROOT_DIR`    | Root directory for raw data                     |
| `TOP_K`                | Number of top retrieval results                 |
| `SIMILARITY_THRESHOLD` | Retrieval filtering threshold                   |
| `KEEP_CHAT_SESSIONS`   | Number of chat sessions/history entries to keep |
| `CHUNK_SIZE`           | Configured chunk size                           |
| `OVERLAP`              | Overlap between chunks                          |

---

# How `config.py` Fits Into the Project

The configuration values are used by different parts of the backend rather than performing the actual processing themselves.

A simplified flow is:

```text
config.py
   |
   +---- Data Pipeline
   |       |
   |       +---- RAW_DIR
   |       +---- CLEANED_PATH
   |       +---- CHUNKS_PATH
   |
   +---- RAG / Retriever
   |       |
   |       +---- VECTOR_DB_PATH
   |       +---- COLLECTION_NAME
   |       +---- TOP_K
   |       +---- SIMILARITY_THRESHOLD
   |       +---- RETRIVE_NEIGHBORS
   |
   +---- LLM Client
   |       |
   |       +---- MODEL_VERSION
   |       +---- TEMPERATURE
   |       +---- MAX_TOKEN
   |
   +---- Chat History
           |
           +---- KEEP_CHAT_SESSIONS
```

The main idea is to keep **configuration separate from application logic**.

If a value needs to be changed during development, it can usually be changed here instead of modifying multiple files.

---

# Overall Purpose

`config.py` acts as the central configuration file for the backend.

It currently manages four main areas:

1. **File paths** — where raw, cleaned, chunked, and vector data is stored.
2. **RAG settings** — chunking, retrieval count, similarity threshold, and neighboring chunks.
3. **LLM settings** — model version, temperature, and token limit.
4. **Chat settings** — environment file location and chat session configuration.

This keeps the rest of the project focused on its actual logic while the important configurable values remain in one place.
