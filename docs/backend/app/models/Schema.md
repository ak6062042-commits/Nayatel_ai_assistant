# schema.py

## Path

`Nayatel.ai-assistant/backend/models/schema.py`

## Purpose

`schema.py` contains the **Pydantic data models** used to define and validate the structure of data sent to and returned from the backend.

These schemas are mainly used for the chatbot API, including:

* User chat requests
* Chat response sources
* Chat responses
* Basic health/status responses

Using schemas keeps the expected API data structure clear and allows invalid data to be detected before it reaches the main application logic.

---

## Technologies Used

### Pydantic

```python
from pydantic import BaseModel, Field
```

[Pydantic](https://docs.pydantic.dev/) is a Python library commonly used for **data validation, parsing, and serialization** using Python type hints.

#### `BaseModel`

`BaseModel` is the main Pydantic class that the schemas inherit from.

For example:

```python
class ChatRequest(BaseModel):
    ...
```

By inheriting from `BaseModel`, Pydantic automatically validates the fields defined inside the class.

More information:

[Pydantic BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

#### `Field`

`Field` is used to add additional rules or metadata to individual fields.

For example:

```python
message: str = Field(..., min_length=1, description="user's message")
```

This specifies that:

* `message` must be a string.
* `...` means the field is required.
* `min_length=1` prevents an empty string from being accepted.
* `description` provides information about what the field represents.

More information:

[Pydantic Fields](https://docs.pydantic.dev/latest/concepts/fields/)

---

### Python `typing`

```python
from typing import Optional
```

`typing` provides tools for adding type hints to Python code.

#### `Optional`

`Optional` indicates that a value can either be a specific type or `None`.

For example:

```python
page: Optional[int] = None
```

means that `page` can contain an integer, or it can be `None`.

More information:

[Python typing documentation](https://docs.python.org/3/library/typing.html)

---

# Models

## 1. `ChatRequest`

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="user's message")
    session_id: str = Field(..., min_length=1, description="unique id for chat session")
```

`ChatRequest` defines the structure of a request sent by the frontend when a user sends a message to the chatbot.

### Fields

| Field        | Type  | Required | Description                                    |
| ------------ | ----- | -------- | ---------------------------------------------- |
| `message`    | `str` | Yes      | The message sent by the user                   |
| `session_id` | `str` | Yes      | Unique identifier for the current chat session |

Both fields have `min_length=1`, so empty strings are not accepted.

### Example

```json
{
    "message": "What internet packages do you offer?",
    "session_id": "abc123"
}
```

---

## Why `session_id` is included

The `session_id` is used to identify a particular conversation.

The original workflow was going to send the conversation history directly from the frontend:

```json
{
    "message": "...",
    "history": [...]
}
```

The workflow was later changed so that **history is handled by the backend**.

The frontend now only needs to send:

```json
{
    "message": "What internet packages do you offer?",
    "session_id": "abc123"
}
```

The backend can use the `session_id` to find the correct conversation history through the `History` object.

This keeps the frontend request simpler and means the backend is responsible for managing conversation history.

---

# 2. `Source`

```python
class Source(BaseModel):
    title: str
    page: Optional[int] = None
```

`Source` represents a source used to generate the chatbot's answer.

This is useful for the RAG system because the chatbot can return information about where the retrieved content came from.

### Fields

| Field   | Type            | Required | Default | Description                                 |
| ------- | --------------- | -------- | ------- | ------------------------------------------- |
| `title` | `str`           | Yes      | -       | Title or name of the source document        |
| `page`  | `Optional[int]` | No       | `None`  | Page number where the information was found |

### Example

```json
{
    "title": "Nayatel Internet Packages",
    "page": 12
}
```

If the source does not have a specific page number, `page` can be `None`.

Example:

```json
{
    "title": "Nayatel FAQ",
    "page": null
}
```

---

# 3. `ChatResponse`

```python
class ChatResponse(BaseModel):
    answer: str
    source: list[Source] = Field(default_factory=list)
```

`ChatResponse` defines the data returned by the backend after processing a user's message.

It contains:

* The generated chatbot answer
* The sources used to generate the answer

### Fields

| Field    | Type           | Description                                     |
| -------- | -------------- | ----------------------------------------------- |
| `answer` | `str`          | The generated response from the chatbot         |
| `source` | `list[Source]` | List of sources related to the generated answer |

### Example

```json
{
    "answer": "Nayatel offers several internet packages depending on your required speed.",
    "source": [
        {
            "title": "Nayatel Internet Packages",
            "page": 12
        }
    ]
}
```

The `source` field can contain multiple `Source` objects.

For example:

```json
{
    "answer": "The available packages are...",
    "source": [
        {
            "title": "Internet Packages",
            "page": 12
        },
        {
            "title": "Nayatel Home Services",
            "page": 5
        }
    ]
}
```

---

## Why `default_factory=list` is used

The source field is defined as:

```python
source: list[Source] = Field(default_factory=list)
```

instead of:

```python
source: list[Source] = []
```

`default_factory=list` creates a **new empty list for each `ChatResponse` instance**.

This is preferable to using a mutable list directly as a default value because separate response objects should not accidentally share the same list.

When no sources are available, the response can therefore simply contain:

```json
{
    "answer": "I could not find relevant information.",
    "source": []
}
```

---

# 4. `Health`

```python
class Health(BaseModel):
    status: str
```

`Health` is a simple schema for returning the status of the backend.

It can be used by a health-check endpoint to confirm that the API is running.

### Example

```json
{
    "status": "ok"
}
```

The actual value of `status` is decided by the endpoint using this schema.

---

# Overall Data Flow

The schemas represent the basic API data flow:

```text
Frontend
   |
   | ChatRequest
   | message + session_id
   v
Backend
   |
   | Retrieve conversation history
   | Retrieve relevant RAG context
   | Generate answer
   v
ChatResponse
   |
   | answer + sources
   v
Frontend
```

The `session_id` allows the backend to connect the current request with the correct conversation history.

The `Source` model allows the RAG pipeline to return source information together with the generated answer.

---

# Summary

`schema.py` acts as the **data structure layer** for the chatbot API.

It currently defines four models:

* **`ChatRequest`** — validates incoming chatbot messages and their session IDs.
* **`Source`** — represents a document source and optional page number.
* **`ChatResponse`** — defines the chatbot's answer and its related sources.
* **`Health`** — defines the response format for a basic backend health check.

Keeping these models separate from the route and RAG logic makes the API structure easier to understand and gives FastAPI/Pydantic a clear definition of the expected request and response data.
