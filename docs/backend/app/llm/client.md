# client.py

## Path

`Nayatel.ai-assistant/backend/llm/client.py`

## Purpose

`client.py` contains two client classes used by the AI pipeline:

* `LLMClient` — communicates with the OpenAI API to generate chatbot responses.
* `EmbeddingClient` — converts text into numerical embeddings using a local Sentence Transformer model.

Keeping these two responsibilities in one file provides a simple interface for the rest of the RAG pipeline to interact with the language model and embedding model without needing to handle their setup directly.

---

# Technologies Used

```python
from sentence_transformers import SentenceTransformer
import config
from dotenv import load_dotenv
import os
from openai import OpenAI
```

## `SentenceTransformer`

`SentenceTransformer` comes from the `sentence-transformers` library.

It is used to convert text into **embeddings**.

An embedding represents text as a list of numerical values. Similar pieces of text should have embeddings that are relatively close to each other in vector space.

These embeddings are useful for the RAG retrieval process.

---

## `dotenv`

```python
from dotenv import load_dotenv
```

`load_dotenv()` loads variables from a `.env` file into the environment.

This is used here to load the OpenAI API key without hardcoding it directly into the Python code.

---

## `os`

```python
import os
```

The `os` module is used to read environment variables.

In this code:

```python
os.getenv("OPENAI_API_KEY")
```

retrieves the OpenAI API key from the environment.

---

## `OpenAI`

```python
from openai import OpenAI
```

`OpenAI` is the Python client used to communicate with the OpenAI API.

The `LLMClient` uses it to send prompts to the configured language model and receive generated responses.

---

# `LLMClient`

```python
class LLMClient:
```

`LLMClient` is responsible for interacting with the language model.

Its main job is to:

1. Load the API key.
2. Create an OpenAI client.
3. Store the selected model.
4. Send prompts to the model.
5. Return the generated text.

---

## `__init__`

```python
def __init__(self, model: str = config.MODEL_VERSION):
    env_path = config.ENV_PATH
    load_dotenv(dotenv_path=env_path)
    self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    self.model = model
```

The constructor prepares the LLM client.

### 1. Get `.env` path

```python
env_path = config.ENV_PATH
```

The location of the `.env` file is taken from `config.py`.

This keeps the environment file path in one central configuration file.

### 2. Load environment variables

```python
load_dotenv(dotenv_path=env_path)
```

Loads the variables stored in the `.env` file.

The expected environment variable is:

```text
OPENAI_API_KEY
```

### 3. Create OpenAI client

```python
self.client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
```

The API key is retrieved from the environment and passed to the OpenAI client.

The key itself is not written directly in the source code.

### 4. Store model name

```python
self.model = model
```

The model name is stored so that the `generate()` method knows which model to use.

By default:

```python
model = config.MODEL_VERSION
```

So the model configured in `config.py` is used unless another model is explicitly provided.

---

# `generate()`

```python
def generate(
    self,
    prompt: str,
    maxtoken: int = config.MAX_TOKEN,
    max_temperature: float = config.TEMPERATURE
):
```

`generate()` sends a prompt to the language model and returns the generated response.

### Parameters

| Parameter         | Type    | Default              | Purpose                             |
| ----------------- | ------- | -------------------- | ----------------------------------- |
| `prompt`          | `str`   | Required             | Text/instructions sent to the LLM   |
| `maxtoken`        | `int`   | `config.MAX_TOKEN`   | Maximum number of completion tokens |
| `max_temperature` | `float` | `config.TEMPERATURE` | Controls response randomness        |

---

## API Request

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_completion_tokens=maxtoken,
    temperature=max_temperature,
    reasoning_effort="low"
)
```

This sends the prompt to the configured OpenAI model.

### `model`

```python
model=self.model
```

Uses the model stored during initialization.

For this project, the default model comes from:

```python
config.MODEL_VERSION
```

---

### `messages`

```python
messages=[
    {
        "role": "user",
        "content": prompt
    }
]
```

The prompt is sent as a user message.

The current implementation uses a single user message rather than maintaining a full message list inside this class.

Conversation history is handled separately by the backend's history system.

---

### `max_completion_tokens`

```python
max_completion_tokens=maxtoken
```

Limits the number of tokens the model can generate.

The default value comes from:

```python
config.MAX_TOKEN
```

---

### `temperature`

```python
temperature=max_temperature
```

Controls the randomness of the generated response.

The default value comes from:

```python
config.TEMPERATURE
```

---

### `reasoning_effort`

```python
reasoning_effort="low"
```

Requests a low reasoning effort level for the model.

This is configured directly inside the API call rather than being stored in `config.py`.

---

## Returning the Answer

```python
return response.choices[0].message.content.strip()
```

The generated response is extracted from the API response.

The `.strip()` removes unnecessary whitespace from the beginning and end of the generated text.

The method therefore returns a simple Python string to the rest of the application.

---

# Error Handling

```python
except Exception as e:
    print(f"llm generation failed: {e}")
    raise
```

If the API request fails, the exception is caught and printed.

For example, an error could occur because of:

* Invalid API key
* Network problems
* API errors
* Invalid model configuration
* Invalid request parameters

After printing the error:

```python
raise
```

re-raises the original exception.

This is important because the failure is not silently ignored. The code calling `generate()` can still detect that the LLM request failed.

---

# `EmbeddingClient`

```python
class EmbeddingClient:
```

`EmbeddingClient` is responsible for converting text into vector representations.

Unlike `LLMClient`, it does not generate natural-language answers.

Its purpose is mainly related to the **RAG retrieval pipeline**.

A simplified process is:

```text
Document
   |
   v
Text Chunk
   |
   v
EmbeddingClient
   |
   v
Vector / Embedding
   |
   v
Vector Database
```

When a user sends a query, the same embedding process can be used to convert the query into a vector so that similar document chunks can be retrieved.

---

# `EmbeddingClient.__init__`

```python
def __init__(self, model_name: str = "all-mpnet-base-v2"):
    self.model = SentenceTransformer(model_name)
```

The constructor loads the Sentence Transformer model.

The default model is:

```text
all-mpnet-base-v2
```

The loaded model is stored in:

```python
self.model
```

This allows the same loaded model to be reused for multiple embedding operations.

---

# `embed()`

```python
def embed(self, text: str) -> list:
    return self.model.encode(text).tolist()
```

`embed()` converts one piece of text into an embedding.

### Input

```text
text: str
```

A single text string.

For example:

```python
text = "Nayatel provides fiber internet services."
```

### Processing

```python
self.model.encode(text)
```

The Sentence Transformer converts the text into a numerical vector.

Then:

```python
.tolist()
```

converts the result into a normal Python list.

### Output

The result is a list of numbers representing the text.

Conceptually:

```text
"some text"
      |
      v
Sentence Transformer
      |
      v
[0.12, -0.04, 0.31, ...]
```

The actual embedding contains many dimensions; the list is not meant to be manually interpreted.

---

# `embed_batch()`

```python
def embed_batch(self, texts: str) -> list:
    return self.model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    ).tolist()
```

`embed_batch()` is used to generate embeddings for multiple texts.

This is useful when processing many document chunks during the ingestion pipeline.

Instead of doing:

```text
chunk 1 -> encode
chunk 2 -> encode
chunk 3 -> encode
chunk 4 -> encode
...
```

individually, multiple chunks can be processed together.

---

## `batch_size=32`

```python
batch_size=32
```

The embedding model processes up to 32 items in a batch.

Batch processing can improve performance when generating embeddings for a large number of chunks.

The optimal batch size depends on the available hardware and the amount of data being processed.

The code currently has a note to test different batch sizes:

```python
# trying batch_size = 32
# TO DO: Try different batch sizes while testing to find optimal (figure out)
```

This means `32` is currently a testing/configuration choice rather than a permanently optimized value.

---

## `show_progress_bar=True`

```python
show_progress_bar=True
```

Displays progress while the model is generating embeddings.

This is useful during document ingestion because embedding many chunks can take some time.

---

# Difference Between the Two Clients

| Client            | Main Job                          | Output |
| ----------------- | --------------------------------- | ------ |
| `LLMClient`       | Generate natural-language answers | `str`  |
| `EmbeddingClient` | Convert text into vectors         | `list` |

They are used at different stages of the RAG pipeline.

```text
                RAG Pipeline

Documents
   |
   v
Chunking
   |
   v
EmbeddingClient
   |
   v
Vector Database
   |
   | Retrieval
   v
Relevant Chunks
   |
   v
Prompt Construction
   |
   v
LLMClient
   |
   v
Generated Answer
```

---

# Overall Role in the Project

`client.py` provides the interface between the backend and the two main AI components:

### `LLMClient`

Handles **generation**:

```text
Prompt -> OpenAI Model -> Answer
```

### `EmbeddingClient`

Handles **embedding**:

```text
Text -> Sentence Transformer -> Vector
```

This separation is useful because embedding and generation are different operations and may use different models.

The rest of the RAG pipeline can simply call:

```python
llm.generate(prompt)
```

or:

```python
embedding.embed(text)
```

without needing to know the details of API authentication, model initialization, or embedding conversion.
