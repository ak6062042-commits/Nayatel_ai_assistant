# ingestion.py

## Path

`Nayatel.ai-assistant/backend/rag/ingestion.py`

## Purpose

`ingestion.py` manages the **document ingestion process** for the RAG system.

Its main responsibility is to take the raw PDF documents, process them into clean text, split that text into chunks, generate embeddings for those chunks, and store the embeddings in a persistent ChromaDB vector database.

The overall process is:

```text
Raw PDF Files
     |
     v
Cleaning
     |
     v
cleaned.jsonl
     |
     v
Chunking
     |
     v
chunks.jsonl
     |
     v
Embeddings
     |
     v
ChromaDB
```

The file is designed so that the ingestion process does not need to repeat expensive work every time the application starts. Existing cleaned data, chunks, and vector database collections are checked before processing again.

---

# Technologies Used

```python
from llm.client import EmbeddingClient
import json
from chromadb import PersistentClient
from pathlib import Path
import config
from rag.pipeline import UtilityPipelines
```

### `EmbeddingClient`

Used to convert the generated document chunks into numerical embeddings.

The embedding model is defined in `client.py`.

---

### `chromadb`

```python
from chromadb import PersistentClient
```

ChromaDB is used as the project's vector database.

The embeddings and their related metadata are stored so that the retriever can later perform similarity searches.

`PersistentClient` allows the database to be stored on disk instead of existing only in memory.

---

### `Path`

```python
from pathlib import Path
```

Used for checking whether directories and files exist and for creating required directories.

---

### `config`

Provides the paths and settings defined in `config.py`, such as:

* Raw data directory
* Cleaned document path
* Chunk path
* Vector database path
* Collection name

---

### `UtilityPipelines`

```python
from rag.pipeline import UtilityPipelines
```

Provides the document-processing functionality used during ingestion.

It handles:

* PDF loading
* Text extraction
* Text cleaning
* Chunking
* Saving/loading processed documents

---

# `Ingenstion`

```python
class Ingenstion:
```

`Ingenstion` is the main class responsible for coordinating the ingestion process.

> Note: The class is currently named `Ingenstion`. The conventional spelling would be `Ingestion`. If this name is changed later, all imports/usages of the class should also be updated.

---

# `__init__`

```python
def __init__(self):
    self.cleaned = []
    self.chunks = []
    self.loaded_files = []
    self.retrived_cleaned_docs = []
```

The constructor initializes storage for the different stages of ingestion.

### `loaded_files`

Contains the PDFs loaded from the raw data directory.

### `cleaned`

Contains cleaned page-level document data.

### `retrived_cleaned_docs`

Contains cleaned documents loaded back from `cleaned.jsonl`.

The spelling `retrived` is kept as it currently appears in the code.

### `chunks`

Contains the processed document chunks loaded from `chunks.jsonl`.

---

# `runCleaning()`

```python
def runCleaning(self, force: bool = False):
```

Runs the document cleaning stage.

The `force` parameter determines whether the cleaning process should run even when a cleaned data file already exists.

---

## Creating the Utility Pipeline

```python
pipeline = UtilityPipelines()
```

A `UtilityPipelines` object is created to perform the actual PDF loading and text processing.

---

## Checking for Existing Cleaned Data

```python
if not Path(config.CLEANED_PATH).exists() or force:
```

Cleaning runs when:

1. The cleaned JSONL file does not exist.
2. `force=True`.

This prevents unnecessary re-processing of the PDFs.

---

## Loading Raw Files

```python
self.loaded_files = pipeline.loadFiles(
    config.RAW_DATA_ROOT_DIR
)
```

The raw PDF directory is taken from `config.py`.

`loadFiles()` searches for PDFs recursively and opens them with PyMuPDF.

---

## Cleaning the Documents

```python
self.cleaned = pipeline.initCleaning(
    self.loaded_files
)
```

The extracted page text is cleaned and stored with metadata such as:

```text
source
page
category
text
```

---

## Saving Cleaned Data

```python
pipeline.storeCleaned(self.cleaned)
```

The cleaned documents are written to the configured JSONL file.

---

## Loading the Stored Data

```python
self.retrived_cleaned_docs = pipeline.loadCleaned()
```

The saved cleaned data is loaded back into memory.

This means the next ingestion stage works from the stored cleaned representation rather than directly from the PDFs.

---

## Existing Cleaned Data

If the cleaned file already exists and `force=False`, the existing file is loaded:

```python
self.retrived_cleaned_docs = pipeline.loadCleaned()
```

This avoids running PDF extraction and cleaning again.

---

# `runChunking()`

```python
def runChunking(self, force: bool = False):
```

Runs the chunking stage.

It converts cleaned documents into smaller chunks that can later be embedded.

---

## Creating Utility Pipeline

```python
pipeline = UtilityPipelines()
```

Creates the utility pipeline used for chunk processing.

---

## Checking Existing Chunks

```python
if not Path(config.CHUNKS_PATH).exists() or force:
```

Chunking runs if:

* The chunk file does not exist.
* `force=True`.

Otherwise, existing chunks are reused.

---

## Creating and Storing Chunks

```python
pipeline.initAndStoreChunks(
    self.retrived_cleaned_docs
)
```

This calls the chunking functionality from `UtilityPipelines`.

The current implementation uses token-based chunking.

The resulting chunks are stored in the configured JSONL file.

---

## Loading Chunks

```python
self.chunks = pipeline.loadChunks()
```

After chunking, the stored chunks are loaded into:

```python
self.chunks
```

These chunks are required for the embedding/vector database stage.

---

# `__initVectordb()`

```python
def __initVectordb(self, client):
```

This method creates/populates the ChromaDB collection.

The method name starts with double underscores because it is intended to be used internally by the class.

---

# Creating the Collection

```python
collection = client.get_or_create_collection(
    name=config.COLLECTION_NAME
)
```

The method gets the configured ChromaDB collection.

If the collection does not exist, ChromaDB creates it.

The collection name comes from:

```python
config.COLLECTION_NAME
```

Currently:

```text
nayatel_docs
```

---

# Creating the Embedder

```python
embedder = EmbeddingClient()
```

Creates an embedding client.

This loads the Sentence Transformer model used to convert document chunks into vectors.

---

# Extracting Chunk Text

```python
text = [
    c["text"]
    for c in self.chunks
]
```

Creates a list containing only the text from each chunk.

For example:

```text
[
    "Nayatel provides...",
    "Internet packages include...",
    "Customers can..."
]
```

---

# Creating Unique IDs

```python
ids = [
    f'{c["source"]}_{c["page"]}_{c["chunk_index"]}'
    for c in self.chunks
]
```

Each chunk gets a unique ID based on:

* Source document
* Page number
* Chunk index

Example:

```text
internet_packages.pdf_5_3
```

This helps identify individual chunks inside the vector database.

---

# Creating Metadata

```python
metadatas = [
    {
        "source": c["source"],
        "page": c["page"],
        "category": c["category"],
        "chunk_index": c["chunk_index"]
    }
    for c in self.chunks
]
```

Metadata is stored alongside each embedding.

This information is later useful when the retriever returns results.

For example, the RAG system can know:

```text
Source: internet_packages.pdf
Page: 5
Category: packages
Chunk: 3
```

The source and page information can then be returned to the frontend as part of the chatbot response.

---

# Generating Embeddings

```python
embeddings = embedder.embed_batch(text)
```

All chunk texts are passed to `EmbeddingClient`.

The embedding model converts the text into vectors.

Conceptually:

```text
Chunk Text
    |
    v
Sentence Transformer
    |
    v
Embedding Vector
```

Because `embed_batch()` is used, the chunks are processed in batches rather than individually.

---

# Adding Data to ChromaDB

```python
collection.add(
    ids=ids,
    embeddings=embeddings,
    metadatas=metadatas,
    documents=text
)
```

The following information is stored in ChromaDB:

| Data         | Purpose                               |
| ------------ | ------------------------------------- |
| `ids`        | Unique identifier for each chunk      |
| `embeddings` | Numerical representation of the chunk |
| `metadatas`  | Source/page/category information      |
| `documents`  | Original chunk text                   |

This gives the retriever everything it needs to search the documents later.

---

# `VerifyVectordb()`

```python
def VerifyVectordb(self, force: bool = False):
```

Checks whether the vector database already exists and whether its collection contains the expected number of chunks.

The purpose is to avoid generating embeddings again when they are already available.

---

# Creating the Vector DB Directory

```python
if not Path(config.VECTOR_DB_PATH).exists():
    Path(config.VECTOR_DB_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )
```

If the configured vector database path does not exist, the parent directory is created.

---

# Creating Persistent Chroma Client

```python
client = PersistentClient(
    path=config.VECTOR_DB_PATH
)
```

Creates a ChromaDB client that stores its data at the configured path.

Because it is persistent, the database remains available after the Python process exits.

---

# Checking Existing Collections

```python
existing = [
    c.name
    for c in client.list_collections()
]
```

The code gets the names of the existing ChromaDB collections.

It then checks whether the configured collection exists.

---

# Existing Collection + `force=True`

```python
if config.COLLECTION_NAME in existing:
    if force:
        client.delete_collection(
            config.COLLECTION_NAME
        )

        self.__initVectordb(client)
        return
```

If the collection already exists but forced ingestion is requested:

1. Delete the existing collection.
2. Create/populate it again.
3. Stop the method.

This is useful when the source documents or chunking configuration have changed and the vector database needs to be rebuilt.

---

# Existing Collection Without Force

If the collection already exists and `force=False`, the code checks its size:

```python
collection = client.get_collection(
    config.COLLECTION_NAME
)
```

Then:

```python
if collection.count() == len(self.chunks):
```

The number of vectors in the database is compared against the number of currently generated chunks.

---

## Matching Chunk Count

If the numbers match:

```python
print(
    f"vector db already has {collection.count()} "
    "matching chunk count, skipping embed"
)
```

The embedding step is skipped.

This saves time because generating embeddings can be relatively expensive.

---

## Different Chunk Count

If the numbers do not match:

```python
client.delete_collection(
    config.COLLECTION_NAME
)

self.__initVectordb(client)
```

The existing collection is deleted and rebuilt.

This handles situations where:

* New documents were added.
* Documents were removed.
* Chunking settings changed.
* The number of generated chunks changed.

---

# New Collection

If the configured collection does not exist:

```python
else:
    self.__initVectordb(client)
```

The vector database is initialized from the current chunks.

---

# `runIngestion()`

```python
def runIngestion(self, forced: bool = False):
    self.runCleaning(force=forced)
    self.runChunking(force=forced)
    self.VerifyVectordb(force=forced)
```

This is the main entry point for the entire ingestion process.

It runs the three stages in order:

```text
1. Cleaning
      |
      v
2. Chunking
      |
      v
3. Vector DB
```

The order is important because each stage depends on the output of the previous stage.

---

# Main Execution Block

```python
if __name__ == "__main__":
    ingest = Ingenstion()
    ingest.runIngestion(forced=False)
```

This allows the file to be run directly from the command line.

When executed directly:

1. An `Ingenstion` object is created.
2. The full ingestion pipeline runs.
3. Existing processed data is reused when possible.

The default is:

```python
forced=False
```

so the pipeline tries to avoid unnecessary processing.

---

# Forced Ingestion

If the ingestion process needs to be rebuilt from scratch, the method can be called with:

```python
ingest.runIngestion(forced=True)
```

This causes the pipeline to:

```text
Re-clean documents
       |
       v
Re-create chunks
       |
       v
Delete existing vector collection
       |
       v
Generate new embeddings
       |
       v
Store new vectors
```

This is useful after changing:

* Raw documents
* Cleaning logic
* Chunk size
* Chunk overlap
* Embedding model
* Other ingestion-related settings

---

# Complete Ingestion Flow

The entire process can be represented as:

```text
                    Raw PDF Files
                          |
                          v
                 UtilityPipelines
                          |
                          v
                    loadFiles()
                          |
                          v
                   initCleaning()
                          |
                          v
                   Cleaned Pages
                          |
                          v
                  storeCleaned()
                          |
                          v
                    cleaned.jsonl
                          |
                          v
                  loadCleaned()
                          |
                          v
                   make_chunks()
                          |
                          v
                     Chunks
                          |
                          v
                 chunks.jsonl
                          |
                          v
                 EmbeddingClient
                          |
                          v
                    Embeddings
                          |
                          v
                     ChromaDB
                          |
                          v
                   nayatel_docs
```

---

# Why the Pipeline Checks Existing Data

The ingestion process contains checks before performing expensive work.

For example:

```text
Does cleaned.jsonl exist?
        |
   +----+----+
   |         |
  Yes       No
   |         |
 Load      Clean PDFs
   |
   v
Continue
```

The same idea is used for chunks and the vector database.

This prevents the application from:

* Re-reading every PDF unnecessarily.
* Recreating every chunk unnecessarily.
* Re-generating embeddings unnecessarily.

This is especially useful once the project contains a larger number of documents.

---

# Important Design Choice: `force`

The `force`/`forced` parameter provides a simple way to rebuild the ingestion data.

### Normal run

```python
ingest.runIngestion(forced=False)
```

Attempts to reuse existing processed data.

### Forced run

```python
ingest.runIngestion(forced=True)
```

Rebuilds the processing stages.

This is useful during development when the ingestion logic or source documents are changed.

---

# Relationship With the RAG System

The ingestion pipeline prepares the data that the retriever later uses.

The overall system can be viewed as two major stages:

## Offline/Data Preparation

```text
PDF
 ↓
Cleaning
 ↓
Chunking
 ↓
Embedding
 ↓
ChromaDB
```

## Runtime Chat

```text
User Question
 ↓
Query Embedding
 ↓
ChromaDB Search
 ↓
Relevant Chunks
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

The ingestion code therefore normally runs when the document data needs to be prepared or updated, while the chatbot can use the already-created vector database during normal operation.

---

# Current Limitations / Things to Improve Later

## 1. Vector DB validation only checks chunk count

Currently, the database is considered valid if:

```python
collection.count() == len(self.chunks)
```

Matching counts do not guarantee that the actual content is identical.

For example, a document could be changed while the total number of chunks remains the same.

A future improvement could use a document/version hash or another form of dataset fingerprinting.

---

## 2. Embedding model changes are not detected automatically

If the embedding model changes but the number of chunks stays the same, the current verification logic may still consider the database valid.

For example:

```text
Old embeddings -> Model A
New configuration -> Model B
Same chunk count
```

The current count check alone would not detect this.

A future version could store the embedding model name as part of the vector database metadata.

---

## 3. `json` import is not used directly in this file

```python
import json
```

The shown ingestion code does not directly use `json`.

The JSONL operations are handled inside `UtilityPipelines`.

The import can therefore be removed unless it is planned for future use.

---

## 4. Naming improvements

There are a few naming inconsistencies that can be cleaned up later:

```text
Ingenstion          -> Ingestion
retrived_cleaned_docs -> retrieved_cleaned_docs
```

These are not functional problems, but correcting them would make the code easier to read.

---

# Overall Role

`ingestion.py` is responsible for preparing the knowledge base used by the chatbot.

Its main responsibilities are:

1. Load raw PDF documents.
2. Clean extracted text.
3. Store cleaned data.
4. Create document chunks.
5. Store chunks.
6. Generate embeddings.
7. Store embeddings and metadata in ChromaDB.
8. Avoid repeating expensive processing when the existing data is still usable.

In simple terms:

```text
Raw Documents
      ↓
Clean
      ↓
Chunk
      ↓
Embed
      ↓
Store in Vector DB
      ↓
Ready for RAG Retrieval
```

The output of this file is the **vectorized knowledge base** that the runtime RAG pipeline can search when answering user questions.
