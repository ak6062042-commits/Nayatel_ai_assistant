# FastAPI Application Entry Point

## Overview

This file is the main entry point for the backend API of the Nayatel AI Assistant.

It creates the FastAPI application, configures CORS, registers the chat routes, and provides a simple root endpoint for checking whether the backend is running.

The basic flow is:

```text
Client / Frontend
       │
       ▼
   FastAPI App
       │
       ├── CORS Middleware
       │
       ├── Chat Router
       │
       └── Root Endpoint
```

---

# Imports

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router
```

## `FastAPI`

Used to create the main FastAPI application.

## `CORSMiddleware`

Used to configure Cross-Origin Resource Sharing (CORS).

CORS is important when the frontend and backend are running on different origins, such as different ports during development.

## `router`

The `router` is imported from:

```text
routes.chat
```

It contains the chatbot-related API routes.

Importing the router here allows the main application to register those endpoints.

---

# FastAPI Application

```python
app = FastAPI(
    title=" NAYATEL AI ASSISTANT",
    description="Internship Chat Bot POC project",
    version="1.0"
)
```

This creates the FastAPI application instance.

### Application Metadata

| Property      | Value                             | Purpose                                  |
| ------------- | --------------------------------- | ---------------------------------------- |
| `title`       | `NAYATEL AI ASSISTANT`            | Name displayed in the API documentation. |
| `description` | `Internship Chat Bot POC project` | Short description of the project.        |
| `version`     | `1.0`                             | Current API version.                     |

FastAPI uses this metadata when generating its automatic API documentation.

---

# CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*']
)
```

The CORS middleware allows requests from frontend applications running on a different origin.

This is commonly needed during development when, for example, the frontend and backend are running on different ports.

## Configuration

### `allow_origins`

```python
allow_origins=['*']
```

Allows requests from any origin.

For a proof-of-concept project, this makes frontend-backend communication easier.

For a production application, it would generally be better to restrict this to the actual frontend domain.

### `allow_credentials`

```python
allow_credentials=False
```

Disables credentials such as cookies or authentication credentials for cross-origin requests.

### `allow_methods`

```python
allow_methods=['*']
```

Allows all HTTP methods, such as:

* `GET`
* `POST`
* `PUT`
* `DELETE`
* `PATCH`

### `allow_headers`

```python
allow_headers=['*']
```

Allows requests to include different HTTP headers.

This is useful when the frontend needs to send headers along with API requests.

---

# Registering the Chat Router

```python
app.include_router(router)
```

This adds all routes defined inside the imported `router` to the main FastAPI application.

Instead of defining all chatbot endpoints directly in this file, the project separates them into:

```text
routes/
└── chat.py
```

This keeps the application entry point relatively simple.

The structure is therefore:

```text
main.py
   │
   └── include_router()
           │
           ▼
       chat.py
           │
           └── Chat API endpoints
```

This is useful for keeping different parts of the backend organized.

---

# Root Endpoint

```python
@app.get("/")
def root() -> dict:
    return {"messag": "Running Sucessfully (Finally)"}
```

This creates a `GET` endpoint at:

```text
/
```

When the backend is running, requesting the root endpoint returns:

```json
{
    "messag": "Running Sucessfully (Finally)"
}
```

The endpoint can be used as a simple health check to confirm that the FastAPI application has started successfully.

---

# Endpoint Details

| Method      | Endpoint                    | Purpose                                |
| ----------- | --------------------------- | -------------------------------------- |
| `GET`       | `/`                         | Checks whether the backend is running. |
| Chat routes | Defined in `routes/chat.py` | Handles chatbot functionality.         |

The exact chatbot endpoints depend on the routes defined in `routes/chat.py`.

---

# Application Structure

This file acts as the starting point of the backend:

```text
FastAPI Application
        │
        ├── CORS Middleware
        │
        ├── Root Endpoint (/)
        │
        └── Chat Router
                │
                ▼
          Chat Processing
                │
                ├── History
                ├── Retriever
                ├── Prompt Builder
                └── LLM
```

The `main.py` file itself does not contain the RAG logic. Its main responsibility is to **initialize the web application and connect the API routes to the rest of the backend**.

---

# Running the Application

If this file is named `main.py`, the FastAPI application can typically be started using Uvicorn:

```bash
uvicorn main:app --reload
```

Here:

* `main` refers to `main.py`.
* `app` refers to the `FastAPI` instance.
* `--reload` automatically restarts the server when code changes during development.

Once the server starts, the root endpoint can be used to check whether the backend is running.

---

# Automatic API Documentation

FastAPI automatically provides interactive API documentation for the registered routes.

The documentation is generated from the FastAPI application and its route definitions.

This is useful during development because the available API endpoints can be tested without needing to build a separate frontend first.

---

# Important Implementation Notes

## 1. CORS Is Open for the POC

The current configuration:

```python
allow_origins=['*']
```

is convenient for development but is intentionally broad.

For a production deployment, the allowed origins should normally be restricted to the actual frontend application.

## 2. Router-Based Structure

The chatbot endpoints are kept in `routes/chat.py` instead of being placed directly inside `main.py`.

This makes the backend easier to organize as more routes are added.

## 3. Root Endpoint Is Not the Chat API

The `/` endpoint only confirms that the application is running.

The actual chatbot functionality is handled through the imported `router`.

## 4. Small Typo in Response Key

The root endpoint currently returns:

```python
return {"message": "Running Successfully"}
```
