# History

## Path

`Nayatel_ai_assistant/backend/rag/history.py`

## Overview

The `History` class is responsible for storing and managing conversation history for the chatbot.

It keeps messages grouped by a `session_id`, allowing different users or conversations to have separate chat histories.

The class also limits the number of stored messages using the `KEEP_CHAT_SESSIONS` configuration value. This prevents the conversation history from continuously growing.

The main responsibilities are:

* Create and manage chat sessions.
* Store user and assistant messages.
* Limit the number of messages kept for each session.
* Retrieve history for a specific session.
* Convert the history into a formatted string that can be passed to the LLM.

---

# Import

```python
from config import KEEP_CHAT_SESSIONS
```

`KEEP_CHAT_SESSIONS` is a configuration value that controls how many recent messages are kept for each conversation.

For example, if:

```python
KEEP_CHAT_SESSIONS = 10
```

only the latest 10 messages for each session will be stored.

---

# `History` Class

```python
class History:
```

The `History` class manages the conversation state of the chatbot.

It uses an in-memory Python dictionary to store conversations.

The basic structure is:

```text
chat_sessions
│
├── session_1
│   ├── message
│   ├── message
│   └── message
│
├── session_2
│   ├── message
│   └── message
│
└── session_3
    └── message
```

Each session has its own list of messages.

---

# `__init__()`

```python
def __init__(self):
    self.chat_sessions = {}
```

Initializes an empty dictionary for storing chat sessions.

The dictionary uses the `session_id` as the key.

Example:

```python
{
    "user123": [
        {"role": "user", "content": "What packages do you offer?"},
        {"role": "assistant", "content": "We offer several internet packages..."}
    ]
}
```

Since this dictionary is stored in memory, the history exists only while the application process is running.

---

# `addMessage()`

```python
def addMessage(self, session_id: str, role: str, content: str):
```

Adds a new message to a specific chat session.

### Parameters

| Parameter    | Type  | Description                                                |
| ------------ | ----- | ---------------------------------------------------------- |
| `session_id` | `str` | Identifier used to separate one conversation from another. |
| `role`       | `str` | Role of the message, such as `user` or `assistant`.        |
| `content`    | `str` | Actual message text.                                       |

---

## Creating a New Session

```python
if session_id not in self.chat_sessions:
    self.chat_sessions[session_id] = []
```

If the provided `session_id` does not already exist, a new empty list is created.

For example:

```python
session_id = "abc123"
```

creates:

```python
{
    "abc123": []
}
```

---

## Adding the Message

```python
self.chat_sessions[session_id].append({
    "role": role,
    "content": content
})
```

The message is stored as a dictionary containing the role and content.

Example:

```python
{
    "role": "user",
    "content": "What internet packages are available?"
}
```

A conversation can therefore contain messages such as:

```python
[
    {
        "role": "user",
        "content": "What packages do you offer?"
    },
    {
        "role": "assistant",
        "content": "We offer several packages..."
    }
]
```

---

## Limiting Chat History

```python
self.chat_sessions[session_id] = (
    self.chat_sessions[session_id][-KEEP_CHAT_SESSIONS:]
)
```

After adding a message, the code keeps only the most recent messages.

For example, if:

```python
KEEP_CHAT_SESSIONS = 5
```

and the session contains 8 messages, only messages 4–8 remain.

This uses Python list slicing:

```python
[-KEEP_CHAT_SESSIONS:]
```

The purpose is to prevent the history from growing indefinitely.

It can also help control how much conversation context is later sent to the LLM.

---

# `getHistory()`

```python
def getHistory(self, session_id: str):
```

Returns the stored messages for a particular session.

```python
return self.chat_sessions.get(session_id, [])
```

The `.get()` method is used so that a missing session does not cause a `KeyError`.

If the session exists:

```python
getHistory("abc123")
```

returns its message list.

If it does not exist:

```python
getHistory("unknown")
```

returns:

```python
[]
```

---

# `buildConversationString()`

```python
def buildConversationString(self, session_id: str):
```

Converts the stored conversation history into a formatted string.

This is useful when the conversation history needs to be included in an LLM prompt.

---

## Getting the History

```python
history = self.getHistory(session_id)
```

The method first retrieves the messages associated with the session.

If there are no messages:

```python
if not history:
    return ""
```

An empty string is returned.

---

## Creating Formatted Lines

```python
lines = []
```

A list is created to store the formatted messages.

The method then loops through every message:

```python
for msg in history:
```

The role is converted to uppercase:

```python
role = msg["role"].upper()
```

For example:

```text
user → USER
assistant → ASSISTANT
```

Each message is then formatted:

```python
lines.append(f"{role}: {msg['content']}")
```

For example:

```text
USER: What packages do you offer?
ASSISTANT: We offer several internet packages.
USER: Which one is suitable for gaming?
```

---

## Combining the Messages

```python
return "\n".join(lines)
```

The individual lines are combined into one string separated by newline characters.

The final result can look like:

```text
USER: What packages do you offer?
ASSISTANT: We offer several internet packages.
USER: Which one is suitable for gaming?
```

This string can then be included in the prompt sent to the LLM.

---

# Overall Flow

The class follows a simple flow:

```text
User Message
     ↓
addMessage()
     ↓
Store in session
     ↓
Keep only recent messages
     ↓
getHistory()
     ↓
buildConversationString()
     ↓
Conversation Context
     ↓
LLM
```

---

# Example Usage

```python
history = History()

history.addMessage(
    "session_1",
    "user",
    "What internet packages do you offer?"
)

history.addMessage(
    "session_1",
    "assistant",
    "We offer several internet packages."
)

conversation = history.buildConversationString("session_1")

print(conversation)
```

Output:

```text
USER: What internet packages do you offer?
ASSISTANT: We offer several internet packages.
```

---

# Role in the RAG Chatbot

The `History` class is responsible for the **conversation memory** part of the chatbot.

It works alongside the retriever and LLM:

```text
                    User Query
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
          History              Retriever
             │                     │
             │              Relevant Context
             │                     │
             └──────────┬──────────┘
                        ▼
                     Prompt
                        │
                        ▼
                       LLM
                        │
                        ▼
                 Assistant Response
                        │
                        ▼
                  Store in History
```

The retriever provides **knowledge from the documents**, while `History` provides **previous conversation context**.

This allows the chatbot to handle follow-up questions more naturally.

For example:

```text
USER: What is your 100 Mbps package?
ASSISTANT: The package costs ...

USER: What about its installation?
```

The second question may depend on the previous conversation. The history allows the LLM to see what the user was previously asking about.

---

# Important Implementation Details

## In-Memory Storage

The history is stored in:

```python
self.chat_sessions = {}
```

This means the data is not stored in a database or file.

If the application restarts, the stored history is lost.

This approach is simple and suitable for a basic chatbot prototype.

## Session Separation

Using `session_id` allows multiple conversations to exist independently.

For example:

```text
session_1 → User A's conversation
session_2 → User B's conversation
session_3 → Another conversation
```

Messages from one session are not mixed with another session.

## History Size Control

The `KEEP_CHAT_SESSIONS` setting limits the amount of conversation retained.

This is useful because sending an unlimited conversation history to an LLM can increase the prompt size and potentially increase processing cost.

## Current Limitation

Because the history is stored only in memory, it is tied to the running application instance.

For a larger or production system, the history could eventually be moved to persistent storage such as a database or another session-storage system.
