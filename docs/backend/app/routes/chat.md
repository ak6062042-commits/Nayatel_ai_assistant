# chat.py

## Path

`Nayatel.ai-assistant/backend/routes/chat.py` 

## Purpose

`chat.py` contains the main **FastAPI routes** for the chatbot backend.

It connects the API layer with the main RAG components:

* `Retriver` — retrieves relevant document chunks.
* `History` — manages conversation history.
* `LLMClient` — communicates with the language model.
* `RagPipelines` — coordinates the overall RAG workflow.
* `schema` — defines the request and response structures.

The frontend communicates with these endpoints rather than directly interacting with the RAG pipeline.

---

## Imports

```python
from fastapi import APIRouter
from client import LLMClient
from history import History
from retriver import Retriver
from pipeline import RagPipelines
import schema
```

### `APIRouter`

```python
from fastapi import APIRouter
```

`APIRouter` is used to create a group of related API routes.

Instead of defining every endpoint directly in `main.py`, the chatbot routes can be kept inside their own module.

---

### `LLMClient`

```python
from client import LLMClient
```

Provides access to the language model used to generate the final chatbot response.

---

### `History`

```python
from history import History
```

Handles the conversation history.

The backend uses the `session_id` sent by the frontend to identify the user's conversation.

---

### `Retriver`

```python
from retriver import Retriver
```

Responsible for retrieving relevant information from the vector database.

The spelling `Retriver` is kept as it appears in the current project code.

---

### `RagPipelines`

```python
from pipeline import RagPipelines
```

Contains the main RAG workflow.

The route does not manually perform retrieval, history handling, prompt construction, and generation. Instead, these responsibilities are handled by the `RagPipelines` object.

---

### `schema`

```python
import schema
```

Contains the Pydantic models used by the API.

In this file, the following schemas are used:

* `schema.ChatRequest`
* `schema.ChatResponse`
* `schema.Health`

---

# Router

```python
router = APIRouter()
```

Creates the FastAPI router.

The endpoints defined below are registered on this router.

The router can then be included in the main FastAPI application.

---

# Component Initialization

```python
retriver = Retriver()
history = History()
llmclient = LLMClient()
```

The main RAG components are initialized when this module is loaded.

### Retriever

```python
retriver = Retriver()
```

Creates the retriever used to search for relevant document chunks.

### History

```python
history = History()
```

Creates the history manager responsible for storing/retrieving conversation history.

### LLM Client

```python
llmclient = LLMClient()
```

Creates the language model client.

The model configuration is taken from the project configuration through `LLMClient`.

---

# RAG Pipeline Initialization

```python
pipeline = RagPipelines(retriver, llmclient, history)
```

The three previously created components are passed into `RagPipelines`.

Conceptually:

```text
Retriver
    |
    |
History ---> RagPipelines ---> Final Answer
    |
    |
LLMClient
```

This allows the pipeline to coordinate the different parts of the chatbot.

The route itself therefore stays relatively simple.

---

# Chat Endpoint

```python
@router.post(
    "/api/chat/",
    response_model=schema.ChatResponse
)
def chat(request: schema.ChatRequest) -> schema.ChatResponse:
    result = pipeline.answer(
        request.message,
        request.session_id
    )

    return schema.ChatResponse(
        answer=result["answer"],
        source=result.get("source", [])
    )
```

This is the main endpoint used to send messages to the chatbot.

## HTTP Method

```text
POST
```

POST is used because the client is sending data to the backend.

## Endpoint

```text
/api/chat/
```

---

# Request Validation

```python
request: schema.ChatRequest
```

The request body must follow the structure defined by `ChatRequest`.

The expected data is:

```json
{
    "message": "What internet packages do you offer?",
    "session_id": "abc123"
}
```

Pydantic/FastAPI validates the request before the function processes it.

---

# Calling the RAG Pipeline

```python
result = pipeline.answer(
    request.message,
    request.session_id
)
```

The user's message and session ID are passed to the RAG pipeline.

The pipeline is responsible for the actual chatbot workflow.

Conceptually:

```text
Frontend
   |
   | message + session_id
   v
/api/chat/
   |
   v
pipeline.answer()
   |
   +---- History
   |
   +---- Retrieval
   |
   +---- Prompt
   |
   +---- LLM
   |
   v
Result
```

The route does not need to know the internal details of each step.

---

# Creating the Response

```python
return schema.ChatResponse(
    answer=result["answer"],
    source=result.get("source", [])
)
```

The result returned by the pipeline is converted into the `ChatResponse` schema.

The answer is taken using:

```python
result["answer"]
```

The source is retrieved using:

```python
result.get("source", [])
```

Using `.get()` means that if the pipeline does not include a `"source"` key, an empty list is used instead.

This prevents the endpoint from failing just because no sources were returned.

---

# Response Example

A successful response could look like:

```json
{
    "answer": "Nayatel offers several internet packages...",
    "source": [
        {
            "title": "Nayatel Internet Packages",
            "page": 12
        }
    ]
}
```

If there are no sources:

```json
{
    "answer": "I could not find relevant information.",
    "source": []
}
```

---

# Response Model

```python
response_model=schema.ChatResponse
```

The response model tells FastAPI what structure the endpoint should return.

It also allows FastAPI to generate API documentation based on the defined Pydantic schema.

The expected response contains:

* `answer`
* `source`

---

# Health Endpoint

```python
@router.get(
    "/api/health",
    response_model=schema.Health
)
def health() -> schema.Health:
    return schema.Health(status="Healthy")
```

The health endpoint is used to check whether the backend is running.

## HTTP Method

```text
GET
```

## Endpoint

```text
/api/health
```

Since this endpoint only checks the current service status, it does not need a request body.

---

# Health Response

The endpoint returns:

```json
{
    "status": "Healthy"
}
```

The response follows the `Health` Pydantic schema.

This can be useful for:

* Checking if the API is running
* Testing the backend during development
* Allowing a frontend or monitoring system to perform a basic health check

---

# Overall API Flow

The main chatbot flow can be represented as:

```text
Frontend
   |
   | POST /api/chat/
   | message + session_id
   v
chat()
   |
   v
RagPipelines.answer()
   |
   +-------------------+
   |                   |
   v                   v
History            Retriever
   |                   |
   +--------+----------+
            |
            v
         LLMClient
            |
            v
       Generated Answer
            |
            v
       ChatResponse
            |
            v
         Frontend
```

The important point is that `chat.py` acts mainly as the **API layer**.

It receives validated input, passes it to the RAG pipeline, and converts the result into the expected API response.

---

# Why the Route Is Kept Simple

Most of the actual processing is intentionally not written inside the route.

For example, the route does not directly perform:

```text
Retrieve chunks
Build prompt
Load history
Call LLM
Store conversation
```

Instead, it calls:

```python
pipeline.answer(request.message, request.session_id)
```

This keeps the API route focused on handling HTTP requests and responses while `RagPipelines` handles the application logic.

This separation makes the code easier to modify later because changes to the RAG workflow can be made in `pipeline.py` without heavily changing the API endpoint.

---

# Endpoints Summary

| Method | Endpoint      | Request       | Response       | Purpose                       |
| ------ | ------------- | ------------- | -------------- | ----------------------------- |
| `POST` | `/api/chat/`  | `ChatRequest` | `ChatResponse` | Send a message to the chatbot |
| `GET`  | `/api/health` | None          | `Health`       | Check backend status          |

---

# Overall Role in the Project

`chat.py` is the connection between the **frontend/API layer** and the **RAG pipeline**.

Its responsibilities are mainly:

1. Define the chatbot API routes.
2. Validate incoming chat requests using Pydantic schemas.
3. Pass the message and `session_id` to the RAG pipeline.
4. Return the generated answer and sources.
5. Provide a basic health-check endpoint.

The main architecture is therefore:

```text
Frontend
   |
   v
FastAPI Routes (chat.py)
   |
   v
RagPipelines
   |
   +---- History
   +---- Retriever
   +---- LLMClient
   |
   v
ChatResponse
   |
   v
Frontend
```
