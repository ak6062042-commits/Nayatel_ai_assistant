# Prompt Builder

## Path

`Nayatel_ai_assistant/backend/rag/prompt.py`

## Overview

This module is responsible for creating the final prompt that is sent to the Large Language Model (LLM).

It contains two main parts:

1. `DEFAULT_PROMPT` — defines the chatbot's behavior and restrictions.
2. `buildPrompt()` — combines the chatbot instructions, conversation history, user query, and retrieved RAG context into one prompt.

The main purpose is to make sure the LLM answers as a **Nayatel customer service assistant** while relying only on the information retrieved from the project's knowledge base.

---

# `DEFAULT_PROMPT`

```python
DEFAULT_PROMPT = """..."""
```

`DEFAULT_PROMPT` contains the main instructions given to the LLM.

It defines the chatbot's:

* Role
* Tone
* Information restrictions
* Fallback behavior
* Off-topic behavior

The prompt is designed for a RAG-based customer support chatbot.

---

## Assistant Role

The prompt starts by defining the assistant as:

```text
You are an empathetic, natural customer service assistant for Nayatel Pakistan.
```

This establishes the chatbot's role and helps guide how the LLM should respond.

The goal is for responses to sound like customer support rather than a generic AI assistant.

---

# Critical Constraints

The prompt contains three mandatory constraints.

## 1. Use Only Provided Context

```text
Rely EXCLUSIVELY on the provided Context to answer.
```

This is an important RAG restriction.

The chatbot should use the retrieved context from the knowledge base instead of relying on general knowledge stored in the LLM.

The intended flow is:

```text
User Query
    ↓
Retriever
    ↓
Relevant Context
    ↓
Prompt
    ↓
LLM
```

This reduces the chance of the model providing information that is not present in the project's data.

---

## 2. Prevent Hallucination

```text
Never invent or hallucinate prices, contact info, services, products, policies, or technical steps.
```

The chatbot is explicitly instructed not to make up information.

This is especially important for a customer support system because incorrect information about things such as:

* Prices
* Packages
* Contact information
* Services
* Policies
* Technical instructions

could result in incorrect customer guidance.

---

## 3. Response Style

```text
Keep answers highly concise, direct, and conversational.
Speak like a helpful human peer, never robotic.
```

This controls the style of the generated response.

The chatbot should avoid unnecessarily long explanations and should respond in a natural customer-service tone.

---

# Fallback Handlers

The prompt also defines what the chatbot should do when the retrieved context does not contain enough information.

```text
If the supplied context does not contain sufficient evidence:
- Do not guess.
- Do not infer unsupported facts.
- Clearly state that the information is unavailable.
- Direct the customer to NayaTel support when appropriate.
```

This is important because retrieval does not always guarantee that the required information exists in the knowledge base.

Instead of generating a potentially incorrect answer, the LLM is instructed to acknowledge that the information is unavailable.

---

# Off-Topic Handling

The prompt contains a specific instruction for questions that are completely unrelated to Nayatel:

```text
If the user's question is completely off-topic:
Reply exactly with:
"I am unable to help with this as I am a Nayatel service representative and can only answer in that context regarding [insert the off-topic subject here]."
```

This attempts to keep the chatbot focused on its intended customer-service role.

For example, if a user asks an unrelated question about programming, the assistant should not switch into a general programming assistant.

---

# `buildPrompt()`

```python
def buildPrompt(query: str, context: str, history: str) -> str:
```

The `buildPrompt()` function creates the final prompt used by the LLM.

### Parameters

| Parameter | Type  | Description                                            |
| --------- | ----- | ------------------------------------------------------ |
| `query`   | `str` | The user's current question.                           |
| `context` | `str` | Relevant information retrieved from the RAG pipeline.  |
| `history` | `str` | Previous conversation history for the current session. |

### Return Value

The function returns a single formatted string containing all the information needed by the LLM.

---

# Handling Conversation History

```python
history_text = history if history else ""
```

This checks whether conversation history was provided.

If `history` contains data, it is used directly.

If it is empty or evaluates to false, an empty string is used instead.

This prevents the prompt from receiving a `None` value when no previous conversation exists.

---

# Building the Final Prompt

The function returns:

```python
return f"""Extremely strict instructions: {DEFAULT_PROMPT}
conversation so far: {history_text}
My query: {query}
context: {context}
ANSWER:"""
```

This combines four important pieces of information.

## 1. System Instructions

```text
Extremely strict instructions:
```

followed by `DEFAULT_PROMPT`.

This tells the LLM how it should behave.

## 2. Conversation History

```text
conversation so far:
```

The previous messages are included so the LLM can understand the current conversation.

This is useful for follow-up questions.

Example:

```text
USER: What is your 100 Mbps package?
ASSISTANT: ...
USER: What about installation?
```

The history helps the model understand what "installation" refers to.

## 3. Current Query

```text
My query:
```

This contains the user's current question.

## 4. Retrieved Context

```text
context:
```

This contains the information retrieved from ChromaDB by the retriever.

The LLM uses this section as the primary source of information for answering the question.

## 5. Answer Marker

```text
ANSWER:
```

This provides a clear point where the model should begin generating its response.

---

# Final Prompt Structure

The final prompt approximately follows this structure:

```text
Extremely strict instructions:
[DEFAULT_PROMPT]

conversation so far:
[previous conversation]

My query:
[current user question]

context:
[retrieved documents]

ANSWER:
[LLM generates response here]
```

---

# Role in the RAG Pipeline

The prompt builder connects the **retrieval system**, **conversation history**, and **LLM**.

```text
                 User Query
                     │
             ┌───────┴────────┐
             ▼                ▼
          History          Retriever
             │                │
             │                ▼
             │          Retrieved Context
             │                │
             └───────┬────────┘
                     ▼
                buildPrompt()
                     │
                     ▼
              Final LLM Prompt
                     │
                     ▼
                    LLM
                     │
                     ▼
              Customer Response
```

This means the prompt is not responsible for retrieving information itself. It simply **organizes the retrieved information and conversation history into a format that the LLM can use**.

---

# Example

Suppose the user asks:

```text
What internet packages do you offer?
```

The retriever may provide context such as:

```text
Nayatel offers the following packages...
```

The history may contain:

```text
USER: I am looking for an internet package.
ASSISTANT: Sure, I can help you with that.
```

`buildPrompt()` combines them into:

```text
Extremely strict instructions:
[DEFAULT_PROMPT]

conversation so far:
USER: I am looking for an internet package.
ASSISTANT: Sure, I can help you with that.

My query:
What internet packages do you offer?

context:
Nayatel offers the following packages...

ANSWER:
```

The LLM then generates the final customer-facing response.

---

# Important Implementation Details

## RAG Context Is Explicitly Provided

The `context` argument is directly inserted into the prompt.

This means the quality of the final answer depends partly on the quality of the retrieval results.

If the retriever returns irrelevant or incomplete information, the LLM may not have enough useful context to answer the question.

## Conversation History Is Separate From RAG Context

The prompt keeps these two types of information separate:

```text
conversation so far:
[chat history]

context:
[RAG results]
```

This is useful because they serve different purposes:

* **History** provides conversational context.
* **Context** provides factual information from the knowledge base.

## Prompt Is Generated Per Request

`buildPrompt()` does not store any state.

Every time it is called, it creates a new prompt from:

```text
DEFAULT_PROMPT
+
history
+
query
+
context
```

This makes the function simple and reusable for each chatbot request.

---

# Overall Responsibility

This module acts as the **prompt construction layer** of the chatbot.

It does not:

* Retrieve documents
* Generate embeddings
* Query ChromaDB
* Store conversation history
* Generate the final answer

Instead, it prepares all the required information and instructions for the LLM.

```text
Retriever
    ↓
Context ───────┐
               │
History ───────┼──→ buildPrompt() → LLM
               │
User Query ────┘
```

This separation keeps the RAG pipeline modular and makes it easier to modify the chatbot's behavior without changing the retrieval or history components.
