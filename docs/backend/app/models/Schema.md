# Schema.py

## Path
- Nayatel.ai-assistant/backend/models/schema.py

## Technologies used
- from pydantic BaseModel, Field
- from typing Optional

## Technolgies Description(basic)
- pydantic is a python module used for run time data validation, parsing and serilization
    - `` BaseModel from pydantic  it is the functional class from which you inhert from to create data schemas``
            `` (For more READ: https://pydantic.dev/docs/validation/dev/api/pydantic/base_model/)``

    - `` Field is a function used add customization rules to individual properties inside BaseModel``
         `` For more READ: https://pydantic.dev/docs/validation/dev/concepts/fields/``
- typing is a python module used which provides support for getting runtime hints for types
    - ``Optional is a type hint helper which indicates that a variable or argument can be a specific type or None ``
        `` For more Read: https://docs.python.org/3/library/typing.html``
        
## Description
Contains Basic fields for main functionalities

### Features
- A field for ChatRequest (takes a user message and a session id for history)
- A field for Source (for generated text source this is passed to ChatResponse)
- A field for chat response (for a generated message and Source field inhereted)
- A field for Health

## Why this version?
- The frontend will send only:
`` { 
    "message": "What internet packages do you offer?",
    "session_id": "abc123"
} ``
Because i changed the workflow for history mid way and decided that backend should handel history

Previously it was going to be:
``{
    "message": "...",
    "history": [...]
}``
Now as said earlier the backend's History object handles that.

- Also, using:

``Field(default_factory=list)``
is preferable to:
``sources: list[Source] = []``
to avoid a mutable default.
