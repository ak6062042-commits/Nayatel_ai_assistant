# pipeline.py

## Path

`Nayatel.ai-assistant/backend/rag/pipeline.py`

## Purpose

`pipeline.py` contains the main processing logic for the Nayatel AI Assistant.

It contains two classes:

* `UtilityPipelines` — handles document ingestion, PDF extraction, text cleaning, chunking, and storing/loading processed data.
* `RagPipelines` — handles the chatbot's RAG workflow, including history, retrieval, relevance checking, prompt creation, LLM generation, and source formatting.

The file therefore covers most of the pipeline between the original PDF documents and the final chatbot response.

---

# Imports

```python
import pymupdf as fitz
from pathlib import Path
from glob import glob
from datetime import datetime
import re
import json
import config
```

It also imports project components:

```python
from rag.retriver import Retriver
from llm.client import LLMClient
from rag.prompt import buildPrompt
from rag.history import History
```

### Main external libraries

| Library        | Purpose                                                      |
| -------------- | ------------------------------------------------------------ |
| `pymupdf`      | Reading and extracting text from PDF files                   |
| `pathlib.Path` | Working with file and directory paths                        |
| `re`           | Regular expressions for text cleaning and sentence splitting |
| `json`         | Reading/writing JSONL data                                   |
| `config`       | Accessing project configuration values                       |

Some imported modules such as `glob` and `datetime` are currently not used in the shown implementation.

---

# Part 1 — `UtilityPipelines`

```python
class UtilityPipelines:
```

`UtilityPipelines` handles the document-processing side of the project.

Its general workflow is:

```text
PDF Files
   |
   v
loadFiles()
   |
   v
Extract Page Text
   |
   v
cleanText()
   |
   v
initCleaning()
   |
   v
cleaned.jsonl
   |
   v
make_chunks()
   |
   v
chunks.jsonl
```

The output of this stage can later be used by the embedding and vector database pipeline.

---

# `__init__`

```python
def __init__(self):
    self.loaded_files = []
    self.cleaned_text = []
```

Two lists are initialized:

### `loaded_files`

Stores information about loaded PDF files.

Each entry contains information such as:

```python
{
    "path": ...,
    "filename": ...,
    "document": ...,
    "total_pages": ...
}
```

### `cleaned_text`

Stores the cleaned text extracted from individual PDF pages.

---

# `loadFiles()`

```python
def loadFiles(self, root_dir: str) -> list:
```

Loads all PDF files under the provided directory.

## Directory validation

```python
pdf_dir = Path(root_dir)

if not pdf_dir.exists():
    raise FileNotFoundError(
        f"data directory does not exist in the passed path: {root_dir}"
    )
```

The path is converted into a `Path` object and checked before processing.

If the directory does not exist, a `FileNotFoundError` is raised.

---

## Finding PDFs

```python
pdf_paths = pdf_dir.glob("**/*.pdf")
```

`glob("**/*.pdf")` searches recursively through the directory.

For example:

```text
data/raw/
├── manuals/
│   ├── router.pdf
│   └── modem.pdf
└── packages/
    └── packages.pdf
```

All PDF files inside the subdirectories can be found.

---

## Opening PDFs

```python
docs = fitz.open(paths)
```

PyMuPDF opens each PDF and returns a document object.

Information about the document is stored:

```python
self.loaded_files.append({
    "path": paths,
    "filename": paths.name,
    "document": docs,
    "total_pages": len(docs)
})
```

This keeps both the PDF itself and some metadata about it.

---

## Error Handling

```python
except Exception as e:
    print(f"error opening file at {paths}, {e}")
```

If one PDF cannot be opened, the error is printed and processing continues instead of stopping the entire ingestion process.

---

# `inferCategory()`

```python
def inferCategory(self, path: Path) -> str:
    return path.parent.name.lower().strip()
```

This method determines a category from the parent directory name.

For example:

```text
data/raw/
├── packages/
│   └── internet.pdf
└── manuals/
    └── router.pdf
```

For:

```text
internet.pdf
```

the parent directory is:

```text
packages
```

So the category becomes:

```text
packages
```

The `.lower()` and `.strip()` calls normalize the category name.

---

# `cleanText()`

```python
def cleanText(self, text: str) -> str:
```

Cleans extracted PDF text before it is stored.

## Empty text

```python
if not text:
    return ""
```

If no text exists, an empty string is returned.

---

## Whitespace normalization

```python
text = re.sub(r"\s+", " ", text)
```

This replaces repeated whitespace, line breaks, tabs, etc. with a single space.

For example:

```text
Hello

This     is
some text.
```

becomes approximately:

```text
Hello This is some text.
```

---

## Bullet normalization

```python
text = re.sub(r"•|●|▪", "-", text)
```

Different bullet characters are converted into a standard `-`.

This gives the text a more consistent structure before chunking.

---

# `initCleaning()`

```python
def initCleaning(self, loaded_files: list) -> list:
```

This method extracts and cleans text from every page of every loaded PDF.

---

## Input Validation

```python
if not loaded_files:
    raise ValueError("missing filr data")
```

The method requires loaded PDF data.

If the list is empty, it raises an error.

---

## Processing Each PDF

```python
for entry in loaded_files:
    documents = entry["document"]
    path = entry["path"]
    category = self.inferCategory(path)
```

The method gets:

* PDF document
* File path
* Category

from each loaded file.

---

## Processing Each Page

```python
for page_num in range(len(documents)):
    text = self.cleanText(
        documents[page_num].get_text()
    )
```

Each PDF page is processed separately.

`get_text()` extracts the page's text.

The extracted text is then passed through `cleanText()`.

---

## Empty Pages

```python
if not text:
    continue
```

Pages with no usable text are skipped.

---

## Storing Cleaned Data

```python
self.cleaned_text.append({
    "text": text,
    "source": entry["filename"],
    "page": page_num + 1,
    "category": category
})
```

Each page becomes a dictionary containing:

* Extracted text
* Source filename
* Page number
* Category

Example:

```json
{
    "text": "Nayatel offers...",
    "source": "internet_packages.pdf",
    "page": 4,
    "category": "packages"
}
```

`page_num + 1` is used because PDF page indexes start at `0`, while users normally refer to pages starting at `1`.

---

# `storeCleaned()`

```python
def storeCleaned(
    self,
    cleaned_text: list,
    path: str = config.CLEANED_PATH
):
```

Stores cleaned documents in a JSONL file.

---

## Creating the Directory

```python
Path(path).parent.mkdir(
    parents=True,
    exist_ok=True
)
```

Creates the parent directory if it does not already exist.

This prevents the application from failing simply because the output directory has not been created yet.

---

## Writing JSONL

```python
with open(path, "w", encoding="utf-8") as f:
    for docs in cleaned_text:
        f.write(
            json.dumps(
                docs,
                ensure_ascii=False
            ) + "\n"
        )
```

Each dictionary is converted into JSON and written on its own line.

Example:

```text
{"text":"...","source":"manual.pdf","page":1,"category":"manuals"}
{"text":"...","source":"manual.pdf","page":2,"category":"manuals"}
```

This format is convenient for processing documents one record at a time.

---

# `loadCleaned()`

```python
def loadCleaned(
    self,
    path: str = config.CLEANED_PATH
) -> list:
```

Loads previously cleaned documents from the JSONL file.

It first checks whether the file exists:

```python
if not Path(path).exists():
    raise FileNotFoundError(...)
```

Then every line is converted back from JSON into a Python dictionary:

```python
for lines in f:
    docs.append(json.loads(lines))
```

The final result is a list of cleaned document records.

---

# `sentenceSplit()`

```python
def sentenceSplit(self, text: str) -> list:
    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]
```

Splits text into sentences using punctuation such as:

* `.`
* `!`
* `?`

The regular expression looks for whitespace immediately after one of these punctuation marks.

Example:

```text
This is sentence one. This is sentence two!
```

becomes:

```python
[
    "This is sentence one.",
    "This is sentence two!"
]
```

---

# `make_chunks()`

```python
def make_chunks(
    self,
    cleaned_docs: list,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.OVERLAP,
    sentences_per_chunk: int = config.SENTENCES_PER_CHUNK,
    by_sentences: bool = False,
    by_tokens: bool = False
) -> list:
```

This is the main chunking function.

It supports two chunking approaches:

1. Sentence-based chunking
2. Token-based chunking

Both options are controlled using flags.

---

# Sentence-Based Chunking

When:

```python
by_sentences=True
```

the function groups a configured number of sentences together.

The configured default is:

```python
config.SENTENCES_PER_CHUNK
```

which is currently `6`.

---

## Grouping by Source

```python
for source, pages in groupby(
    cleaned_docs,
    key=lambda d: d["source"]
):
```

Documents are grouped by their source filename.

This is important because chunks should remain associated with their original document.

---

## Creating Sentence Groups

```python
for i in range(
    0,
    len(sentences),
    sentences_per_chunk
):
```

The sentences are processed in groups.

If the configured value is `6`, the chunks are approximately:

```text
Sentences 1-6
Sentences 7-12
Sentences 13-18
...
```

---

## Chunk Metadata

Each generated chunk contains:

```python
{
    "text": " ".join(group),
    "source": source,
    "page": page_entry["page"],
    "category": page_entry["category"],
    "chunk_index": idx
}
```

The `chunk_index` identifies the chunk's position within the source.

---

# Token-Based Chunking

When:

```python
by_tokens=True
```

the code uses `tiktoken`.

```python
import tiktoken
encoder = tiktoken.get_encoding("cl100k_base")
```

The text is converted into tokens before being divided into chunks.

This is useful because language models work with tokens rather than simply characters or words.

---

## Building Full Document Text

```python
full_text = ""
page_boundaries = []

for p in pages:
    page_boundaries.append(
        (len(full_text), p["page"])
    )

    full_text += p["text"] + " "
```

The pages from the same source are combined into one text string.

At the same time, the code records where each page starts.

These boundaries are later used to determine which page a generated chunk belongs to.

---

## Encoding

```python
tokens = encoder.encode(full_text)
```

The complete document text is converted into tokens.

---

## Chunk Creation

```python
start = 0

while start < len(tokens):
    end = min(
        start + chunk_size,
        len(tokens)
    )

    chunk_tokens = tokens[start:end]
```

The code creates chunks containing approximately `chunk_size` tokens.

The default value comes from:

```python
config.CHUNK_SIZE
```

which is currently `650`.

---

# Chunk Overlap

After creating a chunk:

```python
start += chunk_size - overlap
```

The next chunk starts before the previous chunk completely ends.

With:

```text
chunk_size = 650
overlap = 80
```

approximately 80 tokens are shared between neighboring chunks.

Conceptually:

```text
Chunk 1:
[--------------------650 tokens--------------------]

                         [80 overlap]

Chunk 2:
                         [--------------------650 tokens--------------------]
```

The overlap helps preserve context across chunk boundaries.

---

# Finding the Page Number

After creating a token chunk, the code calculates its character offset:

```python
char_offset = len(
    encoder.decode(tokens[:start])
)
```

This represents approximately where the chunk begins in the original text.

The offset is then passed to:

```python
page_num = self._page_for_offset(
    char_offset,
    page_boundaries
)
```

This allows the chunk to retain a page reference even though multiple pages were combined before tokenization.

---

# `_page_for_offset()`

```python
def _page_for_offset(
    self,
    char_offset: int,
    page_boundaries: list
) -> int:
```

Determines which page contains a particular character offset.

It starts with the first page:

```python
page = page_boundaries[0][1]
```

Then checks the recorded page boundaries.

```python
for offset, pnum in page_boundaries:
    if offset <= char_offset:
        page = pnum
    else:
        break
```

The latest page boundary before the chunk's offset is used as the page number.

This is an approximate mapping between the generated chunk and its original PDF page.

---

# `initAndStoreChunks()`

```python
def initAndStoreChunks(
    self,
    cleaned_docs: list,
    path: str = config.CHUNKS_PATH
):
```

Creates chunks from cleaned documents and stores them in JSONL format.

The current implementation specifically uses token-based chunking:

```python
chunks = self.make_chunks(
    cleaned_docs,
    by_tokens=True
)
```

Each chunk is then written as one JSON object per line.

---

# `loadChunks()`

```python
def loadChunks(
    self,
    path: str = config.CHUNKS_PATH
):
```

Loads previously generated chunks from the JSONL file.

Each line is parsed with:

```python
json.loads(line)
```

and appended to the `chunk` list.

The result is a Python list containing all stored chunks.

---

# Part 2 — `RagPipelines`

```python
class RagPipelines:
```

`RagPipelines` handles the chatbot side of the project.

Its job is to take a user query, retrieve relevant information, use conversation history, send the resulting context to the LLM, and return an answer with sources.

The basic workflow is:

```text
User Query
    |
    v
Query Parsing
    |
    v
Conversation History
    |
    v
Retrieval Query
    |
    v
Retriever
    |
    v
Relevant Chunks
    |
    v
Relevance Check
    |
    v
Context
    |
    v
Prompt
    |
    v
LLM
    |
    v
Answer + Sources
```

---

# `RagPipelines.__init__`

```python
def __init__(
    self,
    retriver: Retriver,
    llm_client: LLMClient,
    history: History,
    similarity_threshold: float = config.SIMILARITY_THRESHOLD,
    top_k: int = config.TOP_K
):
```

The constructor receives the main components required by the RAG workflow.

### Parameters

| Parameter              | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `retriver`             | Retrieves relevant chunks                              |
| `llm_client`           | Generates the final response                           |
| `history`              | Manages conversation history                           |
| `similarity_threshold` | Controls whether retrieved results are relevant enough |
| `top_k`                | Configures the number of retrieval results             |

The objects are stored on the instance for later use.

---

# `buildContext()`

```python
def buildContext(self, found: list) -> list:
    return "\n\n".join(
        f'{f["text"]}'
        for f in found
    )
```

Converts retrieved chunks into one context string.

If multiple chunks are retrieved:

```text
Chunk 1
Chunk 2
Chunk 3
```

they are combined with blank lines between them.

This context is later passed into the prompt.

Although the type hint says `-> list`, the method actually returns a **string**.

The more accurate annotation would be:

```python
def buildContext(self, found: list) -> str:
```

---

# `isRelevant()`

```python
def isRelevant(self, found: list) -> bool:
    best_score = min(
        f["score"]
        for f in found
    )

    return best_score <= self.similarity_threshold
```

Checks whether the retrieved results are relevant enough to answer the query.

The function finds the smallest score:

```python
best_score = min(...)
```

and compares it against:

```python
self.similarity_threshold
```

The current project configuration uses:

```text
SIMILARITY_THRESHOLD = 1.15
```

The comparison assumes that a **lower score represents a better match**, which is common when the retriever is returning a distance rather than a similarity value.

This behavior depends on the scoring method used by the vector database.

---

# `formatSource()`

```python
def formatSource(self, found: list) -> list:
```

Converts retrieved chunk metadata into the source format expected by the API response.

It also removes duplicate source/page combinations.

---

## Duplicate Detection

```python
key = (f["source"], f["page"])
```

A source is identified using:

```text
source + page
```

If the same source/page combination appears more than once, it is only included once.

---

## Output

The method produces:

```python
{
    "title": f["source"],
    "page": f["page"]
}
```

This matches the `Source` schema used by `ChatResponse`.

---

# `recordTurn()`

```python
def recordTurn(
    self,
    session_id: str,
    user_msg: str,
    assistant_msg: str
):
```

Stores both sides of a conversation turn.

First:

```python
self.history.addMessage(
    session_id,
    "user",
    user_msg
)
```

Then:

```python
self.history.addMessage(
    session_id,
    "assistant",
    assistant_msg
)
```

This allows future requests using the same `session_id` to access previous conversation messages.

---

# `buildRetrivalQuery()`

```python
def buildRetrivalQuery(
    self,
    query: str,
    session_id: str
) -> str:
```

Builds the query that will be sent to the retriever.

It gets the current session's history:

```python
history = self.history.getHistory(session_id)
```

Then searches backwards for the most recent user message:

```python
last_user_msg = next(
    (
        h["content"]
        for h in reversed(history)
        if h["role"] == "user"
    ),
    ""
)
```

If a previous user message exists, it combines it with the current query:

```python
return f"{last_user_msg} {query}".strip()
```

Otherwise, it simply returns the current query.

---

## Why This Is Used

This provides some conversational context during retrieval.

For example:

```text
User:
What internet packages do you offer?

User:
What is the price of the second one?
```

The second query alone may not provide enough information.

The retrieval query becomes approximately:

```text
What internet packages do you offer? What is the price of the second one?
```

This can give the retriever more context when searching the vector database.

---

# `queryParsing()`

```python
def queryParsing(self, query: str) -> str:
```

Performs basic cleanup on the user's query.

It uses the same general normalization approach as `cleanText()`:

```python
query = re.sub(r"\s+", " ", query)
query = re.sub(r"•|●|▪", "-", query)
```

Finally:

```python
return query.strip()
```

This removes unnecessary whitespace and normalizes bullet characters.

---

# `answer()`

```python
def answer(
    self,
    query: str,
    session_id: str
) -> dict:
```

This is the main method of `RagPipelines`.

It coordinates the entire chatbot process.

---

# Step 1 — Validate Query

```python
if not query:
    return {
        "answer": "please enter a question!!!",
        "source": []
    }
```

If the user sends an empty query, the pipeline immediately returns a basic response.

No retrieval or LLM call is made.

---

# Step 2 — Clean Query

```python
query = self.queryParsing(query)
```

The user's message is normalized before further processing.

---

# Step 3 — Get Conversation

```python
conversation = self.history.buildConversationString(
    session_id
)
```

The conversation history is converted into a string that can be included in the prompt.

This allows the LLM to have conversational context when generating its answer.

---

# Step 4 — Build Retrieval Query

```python
retrival_query = self.buildRetrivalQuery(
    query,
    session_id
)
```

The current query may be combined with the previous user message to improve retrieval for follow-up questions.

---

# Step 5 — Retrieve Relevant Chunks

```python
found = self.retriver.retrive(
    retrival_query
)
```

The retriever searches the vector database and returns relevant chunks.

A simplified example:

```text
User Query
    |
    v
Embedding
    |
    v
Vector Search
    |
    v
Top Relevant Chunks
```

Each result is expected to contain information such as:

```python
{
    "text": "...",
    "source": "...",
    "page": 12,
    "score": ...
}
```

---

# Step 6 — Relevance Check

```python
if not found or not self.isRelevant(found):
```

The pipeline checks two things:

1. Were any results retrieved?
2. Are the results relevant enough?

If not, the LLM is not called.

Instead, the system returns:

```text
I don't have enough information to answer that. Please contact NayaTel support.
```

The turn is still recorded in history.

```python
self.recordTurn(
    session_id,
    query,
    answer_text
)
```

The response contains no sources:

```python
{
    "answer": answer_text,
    "source": []
}
```

This is an important part of the RAG design because it prevents the model from being given unrelated retrieved context.

---

# Step 7 — Build Context

If the retrieved information is considered relevant:

```python
context = self.buildContext(found)
```

The text from all retrieved chunks is combined into one context string.

---

# Step 8 — Build Prompt

```python
prompt = buildPrompt(
    query,
    context,
    conversation
)
```

The prompt builder combines:

* User query
* Retrieved context
* Conversation history

into the final prompt sent to the LLM.

This keeps prompt construction separate from the main RAG workflow.

---

# Step 9 — Generate Answer

```python
try:
    raw_answer = self.llm_client.generate(prompt)
```

The generated prompt is passed to `LLMClient`.

`LLMClient` then communicates with the configured language model and returns the generated answer.

---

# LLM Error Handling

```python
except Exception as e:
    generation_failed = (
        f"llm client error: {e}"
        + "sorry unable to processes prompt at this moment"
    )

    return {
        "answer": generation_failed,
        "source": []
    }
```

If the LLM call fails, the exception is caught and an error response is returned.

No source information is returned in this case.

One improvement that can be made later is to return a cleaner user-facing message while logging the technical exception separately. Exposing the raw exception to the user can reveal internal implementation details.

---

# Step 10 — Record Conversation

```python
self.recordTurn(
    session_id,
    query,
    raw_answer
)
```

After a successful generation, both the user message and assistant response are added to the session history.

---

# Step 11 — Return Final Result

```python
return {
    "answer": raw_answer,
    "source": self.formatSource(found)
}
```

The final result contains:

* Generated answer
* Formatted sources

Example:

```json
{
    "answer": "Nayatel offers several internet packages...",
    "source": [
        {
            "title": "packages.pdf",
            "page": 5
        }
    ]
}
```

---

# Complete RAG Flow

The complete `answer()` workflow can be summarized as:

```text
                    User Query
                        |
                        v
                  Query Parsing
                        |
                        v
                 Get Conversation
                        |
                        v
               Build Retrieval Query
                        |
                        v
                    Retriever
                        |
                        v
               Retrieved Chunks
                        |
                +-------+-------+
                |               |
           Not Relevant       Relevant
                |               |
                v               v
        Fallback Response    Build Context
                                |
                                v
                           Build Prompt
                                |
                                v
                              LLM
                                |
                         +------+------+
                         |             |
                       Error         Success
                         |             |
                         v             v
                    Error Result   Record Turn
                                       |
                                       v
                                Format Sources
                                       |
                                       v
                                  Final Result
```

---

# Data Processing Flow

The document ingestion portion works separately from the chatbot request flow.

```text
Raw PDFs
   |
   v
loadFiles()
   |
   v
PyMuPDF Extraction
   |
   v
cleanText()
   |
   v
initCleaning()
   |
   v
cleaned.jsonl
   |
   v
make_chunks()
   |
   v
Token Chunks
   |
   v
chunks.jsonl
   |
   v
Embedding Pipeline
   |
   v
Vector Database
```

The chatbot then uses the processed vector data:

```text
User Query
   |
   v
Retriever
   |
   v
Relevant Chunks
   |
   v
RagPipelines
   |
   v
LLM
   |
   v
Answer + Sources
```

---

# Important Design Choices

## 1. Backend Handles Conversation History

The frontend only needs to provide:

```json
{
    "message": "...",
    "session_id": "abc123"
}
```

The backend uses the session ID to retrieve and update the conversation history.

This avoids sending the entire conversation history from the frontend on every request.

---

## 2. Retrieval Happens Before Generation

The system does not immediately send every user question to the LLM.

Instead:

```text
Query
  |
  v
Retriever
  |
  v
Relevant?
  |
  +---- No ---> Fallback
  |
  +---- Yes --> LLM
```

This is important for a RAG chatbot because the LLM should be given relevant project data rather than relying only on its general knowledge.

---

## 3. Source Information Is Preserved

The chunking pipeline stores:

```text
source
page
category
```

The RAG pipeline later uses `source` and `page` to return references with the generated answer.

This allows the chatbot response to show where the retrieved information came from.

---

# Notes and Possible Improvements

The current implementation is functional, but there are a few areas that can be improved later.

### Type annotation in `buildContext()`

Currently:

```python
def buildContext(self, found: list) -> list:
```

but the method returns a string.

It would be more accurate to use:

```python
def buildContext(self, found: list) -> str:
```

---

### `make_chunks()` has two independent `if` statements

Currently:

```python
if by_sentences:
    ...

if by_tokens:
    ...
```

If both values are set to `True`, both chunking strategies will run.

If the intention is to select only one strategy, `if/elif` or explicit validation could be used.

---

### Token chunking depends on `tiktoken`

The token-based branch imports:

```python
import tiktoken
```

inside the function.

This is acceptable because the dependency is only needed when token-based chunking is actually used.

---

### Page mapping is approximate

The `_page_for_offset()` approach maps a token chunk back to a page using character offsets.

Because text is reconstructed from multiple pages before tokenization, the page assignment can be approximate, especially around page boundaries.

This should be tested with real documents if exact source-page accuracy is important.

---

### Error message exposure

The LLM exception is currently included in the returned answer:

```python
f"llm client error: {e}"
```

For a development environment this can be useful, but for a user-facing application it would be better to log the technical error internally and return a simpler message to the user.

---

### Naming

Some names could be cleaned up later, for example:

```text
Retriver     -> Retriever
retrival     -> retrieval
maxtoken     -> max_tokens
```

However, changing names should be done carefully because these names may already be referenced by other files.

---

# Overall Role of `pipeline.py`

`pipeline.py` is one of the main files in the project.

It connects the document-processing side and chatbot-processing side of the system.

### Document side

```text
PDF
 ↓
Extraction
 ↓
Cleaning
 ↓
Chunking
 ↓
Stored Chunks
```

### Chatbot side

```text
User Query
 ↓
History
 ↓
Retrieval
 ↓
Relevance Check
 ↓
Context + Prompt
 ↓
LLM
 ↓
Answer + Sources
```

The main idea is to keep the individual responsibilities separated into methods while using `RagPipelines.answer()` as the main entry point for generating a chatbot response.
