# Retriever

## Path

`Nayatel.ai-assistant/backend/rag/pipeline.py`

## Overview

The `Retriver` class is responsible for retrieving relevant information from the ChromaDB vector database.

It takes a user query, converts it into an embedding using the `EmbeddingClient`, searches the stored document embeddings, and returns the most relevant chunks.

The class also supports **context expansion**, where nearby chunks from the same source document are included with the retrieved chunk. This helps provide more complete context to the LLM instead of relying on only one small chunk.

## Imports

```python
from chromadb import PersistentClient
from llm.client import EmbeddingClient
import config as config
```

### `PersistentClient`

Used to connect to the locally persisted ChromaDB database.

### `EmbeddingClient`

Custom class used to convert text queries into embeddings.

### `config`

Contains project-level configuration values such as:

* `VECTOR_DB_PATH` — location of the vector database
* `COLLECTION_NAME` — name of the ChromaDB collection
* `TOP_K` — number of results to retrieve
* `RETRIVE_NEIGHBORS` — number of neighboring chunks to include

---

# `Retriver` Class

```python
class Retriver:
```

The `Retriver` class handles the retrieval stage of the RAG pipeline.

Its main responsibilities are:

1. Connect to the existing ChromaDB collection.
2. Create an embedding for the user's query.
3. Search the vector database for similar chunks.
4. Convert ChromaDB's response into a simpler format.
5. Optionally expand the retrieved chunks with neighboring chunks.

> Note: The class name is currently written as `Retriver`. A more standard spelling would be `Retriever`, but changing it would require updating the places where the class is imported and used.

---

# `__init__()`

```python
def __init__(
    self,
    db_path: str = config.VECTOR_DB_PATH,
    collection_name: str = config.COLLECTION_NAME
):
```

Initializes the retriever and connects it to the existing ChromaDB collection.

### Parameters

| Parameter         | Type  | Description                                                 |
| ----------------- | ----- | ----------------------------------------------------------- |
| `db_path`         | `str` | Path where the persistent ChromaDB database is stored.      |
| `collection_name` | `str` | Name of the ChromaDB collection to retrieve documents from. |

Both parameters use values from `config.py` by default.

### ChromaDB Connection

```python
client = PersistentClient(path=db_path)
```

Creates a persistent ChromaDB client using the configured database path.

The collection is then loaded:

```python
self.collection = client.get_collection(name=collection_name)
```

The code expects the collection to already exist. This class does not create or populate the collection.

### Error Handling

```python
except Exception as e:
    raise RuntimeError(
        f"Collection '{collection_name}' not found at {db_path}. "
    )
```

If the collection cannot be loaded, a `RuntimeError` is raised.

This is useful because the retrieval system depends on the vector database being available before the chatbot can answer questions.

### Embedding Client

```python
self.embedder = EmbeddingClient()
```

Creates an embedding client that will later convert the user's query into a vector representation.

---

# `unpackResults()`

```python
def unpackResults(self, results_found) -> list:
```

Converts the raw result returned by ChromaDB into a simpler list of dictionaries.

ChromaDB returns multiple fields such as:

* IDs
* documents
* metadata
* distances

The method extracts these values and combines them into a more convenient structure.

### Extracting Results

```python
ids = results_found["ids"][0]
docs = results_found["documents"][0]
meta = results_found["metadatas"][0]
dis = results_found["distances"][0]
```

The `[0]` is used because ChromaDB returns results grouped by query.

For a single query, the first element contains the actual result list.

### Result Structure

Each retrieved document is converted into:

```python
{
    "ids": ids[i],
    "text": docs[i],
    "source": meta[i]["source"],
    "page": meta[i]["page"],
    "category": meta[i]["category"],
    "chunk_index": meta[i].get("chunk_index"),
    "score": dis[i]
}
```

The returned fields contain:

| Field         | Description                                                                                         |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `ids`         | Unique ID of the stored chunk.                                                                      |
| `text`        | Actual text content of the retrieved chunk.                                                         |
| `source`      | Source document from which the chunk came.                                                          |
| `page`        | Page number associated with the chunk.                                                              |
| `category`    | Category assigned during document processing.                                                       |
| `chunk_index` | Position of the chunk within the source document.                                                   |
| `score`       | Distance returned by ChromaDB representing similarity/distance between the query and stored vector. |

The result is returned as a list of dictionaries.

---

# `expandContext()`

```python
def expandContext(self, found: dict, expansion: int) -> dict:
```

Expands a retrieved chunk by including nearby chunks from the same source document.

This is useful because a single retrieved chunk may not contain enough information to answer a question completely.

For example, if chunk `10` is retrieved and `expansion=2`, the method attempts to include:

```text
Chunk 8
Chunk 9
Chunk 10
Chunk 11
Chunk 12
```

This gives the LLM a larger section of the original document.

## Checking `chunk_index`

```python
if found["chunk_index"] is None:
    return found
```

If the retrieved chunk does not contain a `chunk_index`, context expansion cannot be performed.

The original result is therefore returned unchanged.

## Finding the Neighbor Range

```python
origin = found["chunk_index"]
upper_origin, below_origin = origin - expansion, origin + expansion
```

The original chunk index is used as the center of the expansion range.

For example:

```text
origin = 10
expansion = 2

range = 8 → 12
```

## Getting Documents From the Same Source

```python
same_category_docs = self.collection.get(
    where={"source": found["source"]},
    include=["metadatas", "documents"]
)
```

The code retrieves documents whose `source` metadata matches the source of the original result.

This prevents the expansion from accidentally including chunks from another document.

## Selecting Neighbor Chunks

```python
for doc_text, meta in zip(
    same_category_docs["documents"],
    same_category_docs["metadatas"]
):
```

The method goes through the documents and their metadata together.

It checks their chunk indexes:

```python
index = meta.get("chunk_index")
```

Only chunks inside the required range are added:

```python
if index is not None and upper_origin <= index <= below_origin:
    neighbors.append((index, doc_text))
```

## Sorting the Chunks

```python
neighbors.sort(key=lambda x: x[0])
```

The chunks are sorted according to their `chunk_index`.

This is important because the chunks should be combined in their original document order.

## Combining the Context

```python
expand_text = " ".join(text for _, text in neighbors)
```

The neighboring chunks are combined into a single text string.

The original result is copied:

```python
expand_found = dict(found)
```

Then the expanded text replaces the original text:

```python
expand_found["text"] = expand_text
expand_found["expanded"] = True
```

The `expanded` field indicates that context expansion was applied.

---

# `retrive()`

```python
def retrive(
    self,
    query: str,
    top_k: int = config.TOP_K,
    expansion: int = config.RETRIVE_NEIGHBORS
) -> list:
```

This is the main retrieval method.

It performs the complete retrieval process:

```text
User Query
    ↓
Query Validation
    ↓
Generate Query Embedding
    ↓
ChromaDB Vector Search
    ↓
Unpack Results
    ↓
Expand Context
    ↓
Return Results
```

### Parameters

| Parameter   | Type  | Description                                                          |
| ----------- | ----- | -------------------------------------------------------------------- |
| `query`     | `str` | User's question or search query.                                     |
| `top_k`     | `int` | Number of similar chunks to retrieve.                                |
| `expansion` | `int` | Number of neighboring chunks to include around each retrieved chunk. |

### Empty Query Handling

```python
if not query or not query.strip():
    return []
```

The method checks whether the query is empty or contains only whitespace.

Instead of performing a database search, it returns an empty list.

### Creating the Query Embedding

```python
query_embed = self.embedder.embed(query)
```

The user's text is converted into an embedding vector.

The embedding represents the semantic meaning of the query and allows it to be compared with the embeddings stored in ChromaDB.

### Vector Search

```python
result = self.collection.query(
    query_embeddings=[query_embed],
    n_results=top_k
)
```

The generated query embedding is sent to ChromaDB.

`top_k` controls how many similar chunks are returned.

For example:

```text
top_k = 3
```

means the system requests the three most relevant stored vectors.

### Unpacking Results

```python
found = self.unpackResults(result)
```

The raw ChromaDB response is converted into the simplified result format described earlier.

### Context Expansion

```python
if expansion > 0:
    found = [self.expandContext(f, expansion) for f in found]
```

If neighbor expansion is enabled, every retrieved result is passed through `expandContext()`.

For example:

```text
Retrieved:
    Chunk 25

Expansion:
    ±2 chunks

Final context:
    Chunk 23
    Chunk 24
    Chunk 25
    Chunk 26
    Chunk 27
```

### Return Value

```python
return found
```

The method returns a list containing the retrieved and optionally expanded documents.

---

# Overall Retrieval Flow

The class works as part of the RAG pipeline in the following way:

```text
                    User Question
                         │
                         ▼
                  Retriver.retrive()
                         │
                         ▼
                 Generate Embedding
                         │
                         ▼
                    ChromaDB
                         │
                         ▼
                 Top-K Similar Chunks
                         │
                         ▼
                  unpackResults()
                         │
                         ▼
                Context Expansion
                         │
                         ▼
              Retrieved Context
                         │
                         ▼
                       LLM
```

The retriever therefore acts as the connection between the **user's question** and the **knowledge stored in the vector database**.

---

# Example Returned Result

A result may look similar to:

```python
[
    {
        "ids": "chunk_25",
        "text": "Nayatel provides ...",
        "source": "packages.pdf",
        "page": 4,
        "category": "packages",
        "chunk_index": 25,
        "score": 0.32,
        "expanded": True
    }
]
```

The LLM can then use the `text` field as context when generating the final response.

---

# Important Implementation Details

## 1. Query and Document Embeddings Must Be Compatible

The query embedding generated by:

```python
self.embedder.embed(query)
```

must use the same embedding approach/model used when the documents were originally stored in ChromaDB.

Otherwise, similarity search may produce poor results.

## 2. `score` Is Actually a Distance

The variable is named `score`:

```python
"score": dis[i]
```

but ChromaDB's `distances` field represents a distance measure.

Depending on the configured distance metric, a lower distance generally means the vectors are more similar.

Therefore, this value should not automatically be interpreted as a percentage or confidence score.

## 3. Context Expansion Depends on Metadata

The expansion logic depends on:

```python
source
chunk_index
```

being correctly stored in each chunk's metadata.

If `chunk_index` is missing, the chunk cannot be expanded.

## 4. Expansion Is Performed After Vector Search

The vector search determines which chunks are semantically relevant first.

The neighboring chunks are then added based on their position in the original document.

This separates:

* **semantic retrieval** — finding relevant content
* **sequential context expansion** — adding surrounding content

## 5. Current Expansion Query

The following operation:

```python
self.collection.get(
    where={"source": found["source"]},
    include=["metadatas", "documents"]
)
```

loads all matching chunks from the source before selecting the neighbors.

This is simple and works well for a smaller project, but for a very large collection it could become less efficient because more documents may be loaded than are actually required.

---

# Role in the RAG System

The `Retriver` is part of the **retrieval stage** of the RAG architecture.

```text
Documents
   ↓
Text Extraction
   ↓
Cleaning
   ↓
Chunking
   ↓
Embedding
   ↓
ChromaDB
   │
   │
   │ User Query
   ▼
Retriever
   ↓
Relevant Context
   ↓
LLM
   ↓
Final Answer
```

Its main purpose is to make sure that the LLM receives information from the project's stored knowledge base that is relevant to the user's question.
