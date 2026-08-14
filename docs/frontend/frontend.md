# Frontend Documentation

## Overview

The frontend is a simple web-based chat interface for the Nayatel AI Assistant.

It provides a way to interact with the FastAPI backend without requiring API tools such as Postman.

The frontend consists of three files:

```text
frontend/
├── index.html
├── style.css
└── script.js
```

Each file has a separate responsibility:

| File         | Responsibility                                               |
| ------------ | ------------------------------------------------------------ |
| `index.html` | Defines the structure of the chat interface.                 |
| `style.css`  | Controls the appearance and layout.                          |
| `script.js`  | Handles user interaction and communication with the backend. |

---

# Frontend Scope

The frontend was built primarily for **using and testing the chatbot**, not as a dedicated frontend-development project.

I am **not a frontend developer**, and I do not currently plan to specialize in frontend development. The main focus of this project was the backend, RAG pipeline, retrieval system, prompt construction, LLM integration, and overall chatbot functionality.

The frontend exists to provide a usable interface for the working system.

> **[I do not care if the frontend doesn't look good.I am a Backend, AL, ML, AUTOMOATION, AUTONOMUS SYSTEMS, ROBOTIC DEV most importantly  It's my project, my continuous effort, and the result of non-stop 2–3 days of learning and coding.]**

The priority for this project was:

```text
Working RAG System
       ↓
Working Backend
       ↓
Working Chatbot
       ↓
Basic Usable Frontend
```

rather than spending significant time on visual design or frontend architecture.

This documentation therefore focuses on **how the frontend works technically and how it communicates with the backend**, rather than presenting it as a professional frontend application.

---

# Frontend Architecture

The frontend uses basic:

* HTML
* CSS
* JavaScript
* Browser `fetch()` API
* Browser `sessionStorage`
* Browser `crypto.randomUUID()`

There is no frontend framework such as React, Vue, or Angular.

The overall communication flow is:

```text
User
 │
 ▼
index.html
 │
 ▼
script.js
 │
 ├── Generate / retrieve session ID
 │
 ├── Collect user message
 │
 ├── Send HTTP POST request
 │
 ▼
FastAPI Backend
 │
 ▼
RAG Pipeline
 │
 ▼
LLM
 │
 ▼
JSON Response
 │
 ▼
script.js
 │
 ▼
Chat Interface
```

---

# `index.html`

## Purpose

`index.html` defines the basic structure of the chatbot interface.

It contains:

* Chat application container
* Header
* Online status indicator
* Chat message area
* User input area
* Send button
* JavaScript reference

The HTML does not contain the chatbot logic. That functionality is handled by `script.js`.

---

# HTML Document Setup

```html
<!DOCTYPE html>
<html lang="en">
```

The document uses standard HTML5 and specifies English as the page language.

---

# Metadata

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Character Encoding

`UTF-8` allows the page to correctly handle normal text and a wide range of characters.

### Viewport

The viewport configuration makes the layout adapt better to different screen sizes.

---

# Page Title

```html
<title>NayaTel AI Assistant</title>
```

Sets the browser tab title.

---

# CSS Import

```html
<link rel="stylesheet" href="style.css">
```

Loads the styling rules from `style.css`.

This keeps the HTML structure separate from the visual styling.

---

# Chat Container

```html
<div class="chat-container">
```

This is the main container for the chatbot interface.

Everything visible in the application is placed inside this container.

---

# Chat Header

```html
<header class="chat-header">
```

The header contains the chatbot name, description, and status.

```html
<h1>NayaTel AI Assistant</h1>
<p>Customer Support Assistant</p>
```

The title identifies the application while the paragraph describes its purpose.

---

# Online Status

```html
<div class="status">
    <span class="status-dot"></span>
    Online
</div>
```

This displays a simple visual indicator showing that the assistant is online.

The green dot is created through CSS.

It is currently a **static UI indicator** and does not actually check whether the backend server is available.

---

# Chat Messages Area

```html
<main id="chat-messages" class="chat-messages">
```

This element acts as the container where messages are displayed.

It initially contains one assistant message:

```html
<div class="message assistant-message">
```

The JavaScript later adds additional messages dynamically.

The `id`:

```text
chat-messages
```

allows JavaScript to find this element.

---

# Input Area

```html
<div class="input-area">
```

Contains the user's text input and send button.

## Textarea

```html
<textarea
    id="message-input"
    placeholder="Ask something about NayaTel..."
    rows="1"
></textarea>
```

The textarea allows the user to enter a question.

The JavaScript accesses it using:

```javascript
document.getElementById("message-input")
```

## Send Button

```html
<button id="send-button">
    Send
</button>
```

The button triggers the message-sending process.

---

# JavaScript Import

```html
<script src="script.js"></script>
```

Loads the frontend logic after the HTML elements have been defined.

This allows the JavaScript to find the required DOM elements.

---

# `style.css`

## Purpose

`style.css` controls the visual appearance and layout of the chatbot.

It handles:

* Page layout
* Chat container
* Header
* Messages
* User messages
* Assistant messages
* Input field
* Send button
* Button states
* Basic responsive sizing

The CSS is intentionally simple because the frontend was built mainly for functionality and usability.

---

# Global Reset

```css
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
```

Applies basic reset rules to all elements.

`box-sizing: border-box` makes width and height calculations easier to manage.

The default browser margins and padding are also removed.

---

# Body Layout

```css
body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;

    height: 100vh;

    display: flex;
    justify-content: center;
    align-items: center;
}
```

The body uses Flexbox to center the chat interface vertically and horizontally.

`100vh` makes the body take the full viewport height.

---

# Chat Container

```css
.chat-container {
    width: 90%;
    max-width: 900px;
    height: 90vh;
```

The chat interface occupies 90% of the available width and height while limiting its maximum width to 900px.

```css
display: flex;
flex-direction: column;
```

This creates a vertical layout:

```text
Header
   ↓
Messages
   ↓
Input
```

---

# Chat Header Styling

The header uses:

```css
display: flex;
justify-content: space-between;
align-items: center;
```

This places the chatbot information on one side and the online status on the other.

---

# Message Layout

```css
.chat-messages {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 18px;
}
```

The message area takes the remaining available space.

`overflow-y: auto` allows the user to scroll when the conversation becomes longer than the available space.

---

# Message Types

There are two main message styles.

## Assistant Message

```css
.assistant-message {
    align-self: flex-start;
    background: #f1f5f9;
    color: #1f2937;
}
```

Assistant messages appear on the left.

## User Message

```css
.user-message {
    align-self: flex-end;
    background: #2563eb;
    color: white;
}
```

User messages appear on the right.

This creates the familiar chat layout:

```text
NayaTel AI
────────────
Assistant response

                         You
                         ────────────
                         User message
```

---

# Input Area

```css
.input-area {
    padding: 15px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    gap: 10px;
}
```

The input and send button are placed next to each other.

The textarea uses:

```css
flex: 1;
```

so it takes the available horizontal space.

---

# Send Button States

The button has three basic states.

### Normal

```css
#send-button {
    background: #2563eb;
}
```

### Hover

```css
#send-button:hover {
    background: #1d4ed8;
}
```

### Disabled

```css
#send-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
}
```

The button is disabled while a request is being sent to prevent multiple requests from being submitted at the same time.

---

# `script.js`

## Purpose

`script.js` contains the main frontend logic.

It is responsible for:

1. Connecting to the backend API.
2. Getting references to the HTML elements.
3. Creating or retrieving a session ID.
4. Displaying messages.
5. Sending user messages.
6. Receiving the backend response.
7. Displaying the assistant response.
8. Handling API errors.
9. Supporting Enter-to-send behavior.

---

# Backend API URL

```javascript
const API_URL = "http://localhost:8000/api/chat/";
```

This defines the FastAPI endpoint used by the frontend.

The frontend sends chat requests to:

```text
POST http://localhost:8000/api/chat/
```

The backend must therefore be running locally on port `8000`.

---

# DOM Element References

```javascript
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatMessages = document.getElementById("chat-messages");
```

These variables store references to the HTML elements that JavaScript needs to interact with.

| Variable       | HTML Element     | Purpose                         |
| -------------- | ---------------- | ------------------------------- |
| `messageInput` | `#message-input` | User's message input.           |
| `sendButton`   | `#send-button`   | Sends the message.              |
| `chatMessages` | `#chat-messages` | Displays conversation messages. |

---

# Session Management

The frontend creates a session ID so that the backend can associate multiple messages with the same conversation.

```javascript
let sessionId = sessionStorage.getItem("nayatel_session_id");
```

First, it checks whether a session ID already exists in the browser's `sessionStorage`.

If one does not exist:

```javascript
if (!sessionId) {
    sessionId = crypto.randomUUID();
```

A new UUID is generated.

The ID is then stored:

```javascript
sessionStorage.setItem(
    "nayatel_session_id",
    sessionId
);
```

The basic flow is:

```text
Open Chat
    ↓
Check sessionStorage
    ↓
Session exists?
   /       \
 Yes       No
  ↓         ↓
Use ID   Generate UUID
            ↓
       Store session ID
```

This session ID is later sent to the backend with every message.

---

# `addMessage()`

```javascript
function addMessage(role, text) {
```

This function adds a message to the chat interface.

### Parameters

| Parameter | Description                   |
| --------- | ----------------------------- |
| `role`    | Either the user or assistant. |
| `text`    | Message content to display.   |

---

# Creating the Message Element

```javascript
const messageDiv = document.createElement("div");
messageDiv.classList.add("message");
```

A new `<div>` is created dynamically.

The base `message` CSS class is then applied.

---

# Selecting User or Assistant Style

```javascript
if (role === "user") {
    messageDiv.classList.add("user-message");
} else {
    messageDiv.classList.add("assistant-message");
}
```

The role determines how the message is displayed.

```text
user      → user-message
assistant → assistant-message
```

This connects the JavaScript logic with the CSS styles.

---

# Creating the Message Label

```javascript
const label = document.createElement("div");
label.classList.add("message-label");
```

The label displays who sent the message.

```javascript
label.textContent =
    role === "user"
        ? "You"
        : "NayaTel AI";
```

The output is:

```text
You
```

for user messages and:

```text
NayaTel AI
```

for assistant messages.

---

# Creating Message Content

```javascript
const content = document.createElement("div");
content.classList.add("message-content");
content.textContent = text;
```

The actual message text is placed inside the content element.

`textContent` is used rather than inserting HTML directly.

This means returned content is treated as text instead of being interpreted as HTML.

---

# Adding the Message to the Chat

```javascript
messageDiv.appendChild(label);
messageDiv.appendChild(content);

chatMessages.appendChild(messageDiv);
```

The structure becomes approximately:

```html
<div class="message user-message">
    <div class="message-label">You</div>
    <div class="message-content">
        User question
    </div>
</div>
```

---

# Automatic Scrolling

```javascript
chatMessages.scrollTop =
    chatMessages.scrollHeight;
```

After a new message is added, the chat area automatically scrolls to the bottom.

This keeps the newest message visible.

---

# `sendMessage()`

```javascript
async function sendMessage() {
```

This is the main function responsible for sending a user message to the backend.

It is asynchronous because it performs an HTTP request.

---

# Reading the User Message

```javascript
const message = messageInput.value.trim();
```

The input is read and leading/trailing whitespace is removed.

If the message is empty:

```javascript
if (!message) {
    return;
}
```

the function stops without sending a request.

---

# Displaying the User Message

```javascript
addMessage("user", message);
```

The user's message is immediately displayed in the interface.

The input is then cleared:

```javascript
messageInput.value = "";
```

---

# Disabling the Send Button

```javascript
sendButton.disabled = true;
sendButton.textContent = "Sending...";
```

The button is temporarily disabled while the API request is running.

This helps prevent accidental duplicate requests.

---

# Sending the API Request

The frontend uses the browser's `fetch()` API:

```javascript
const response = await fetch(API_URL, {
    method: "POST",
```

The request uses HTTP `POST` because the frontend is sending data to the backend.

---

# Request Headers

```javascript
headers: {
    "Content-Type": "application/json"
}
```

This tells the backend that the request body contains JSON.

---

# Request Body

```javascript
body: JSON.stringify({
    message: message,
    session_id: sessionId
})
```

The frontend sends two values:

```json
{
    "message": "User question",
    "session_id": "generated-session-id"
}
```

The `message` contains the current question.

The `session_id` allows the backend's history system to associate the message with the correct conversation.

---

# Backend Response Validation

```javascript
if (!response.ok) {
    throw new Error(
        `Server returned ${response.status}`
    );
}
```

`response.ok` checks whether the HTTP response was successful.

If the server returns an error status, an exception is raised and handled by the `catch` block.

---

# Reading the JSON Response

```javascript
const data = await response.json();
```

The response body is converted from JSON into a JavaScript object.

The frontend expects the backend response to contain an `answer` field.

```javascript
addMessage(
    "assistant",
    data.answer
);
```

The answer is then displayed as an assistant message.

---

# Error Handling

```javascript
catch (error) {
    console.error(error);

    addMessage(
        "assistant",
        "Sorry, I couldn't connect to the NayaTel AI Assistant."
    );
}
```

If the request fails, the error is printed to the browser console and a user-friendly message is displayed in the chat.

Possible causes include:

* FastAPI server is not running.
* Wrong API URL.
* Backend returned an error.
* Network connection problem.
* CORS configuration issue.

---

# `finally` Block

```javascript
finally {
    sendButton.disabled = false;
    sendButton.textContent = "Send";
    messageInput.focus();
}
```

The `finally` block runs whether the request succeeds or fails.

It:

1. Re-enables the send button.
2. Changes the button text back to `Send`.
3. Returns focus to the input field.

---

# Send Button Event

```javascript
sendButton.addEventListener(
    "click",
    sendMessage
);
```

When the user clicks the Send button, `sendMessage()` is executed.

---

# Enter Key Support

```javascript
messageInput.addEventListener(
    "keydown",
    function (event) {
```

The frontend also allows the user to press Enter to send a message.

```javascript
if (
    event.key === "Enter" &&
    !event.shiftKey
) {
```

The message is sent when:

```text
Enter
```

is pressed without Shift.

The default newline behavior is prevented:

```javascript
event.preventDefault();
```

and then:

```javascript
sendMessage();
```

is called.

If the user presses:

```text
Shift + Enter
```

the message is not sent, allowing a newline to be entered.

---

# Frontend-to-Backend Request Flow

The complete interaction is:

```text
User enters message
        │
        ▼
sendMessage()
        │
        ▼
Add user message to UI
        │
        ▼
Create JSON request
        │
        ├── message
        └── session_id
        │
        ▼
POST /api/chat/
        │
        ▼
FastAPI Backend
        │
        ▼
Chat / RAG Pipeline
        │
        ▼
LLM Response
        │
        ▼
JSON Response
        │
        ▼
data.answer
        │
        ▼
addMessage("assistant", ...)
        │
        ▼
Display response
```

---

# Session and Backend History

The frontend's session ID connects directly to the backend conversation history.

The relationship is:

```text
Browser
│
├── sessionStorage
│      └── session_id
│
└── script.js
       │
       │ sends session_id
       ▼
FastAPI
       │
       ▼
History
       │
       └── chat_sessions[session_id]
```

This allows multiple messages from the same browser session to be associated with the same conversation.

---

# Error Flow

If the backend cannot be reached:

```text
User Message
     ↓
fetch()
     ↓
Request Fails
     ↓
catch()
     ↓
Console Error
     ↓
Display Friendly Error
```

The frontend does not expose the technical error directly to the user.

---

# Running the Frontend

The frontend expects the backend to be running at:

```text
http://localhost:8000
```

and specifically sends chat requests to:

```text
http://localhost:8000/api/chat/
```

The frontend files can be opened/served using a simple local web server.

The backend should be started first so that the API endpoint is available.

---

# Current Frontend Limitations

The frontend intentionally remains simple.

It currently does not include:

* React or another frontend framework
* Component architecture
* Authentication
* Persistent conversation storage
* Message editing
* Message deletion
* Markdown rendering
* Streaming LLM responses
* File uploads
* Advanced loading animations
* Production-level responsive design
* Real backend health checking
* A dedicated frontend build system

These are outside the main scope of this project.

The frontend's purpose is simply to provide a usable interface for interacting with the chatbot backend.

---

# Development Focus

The majority of the development effort in this project was focused on the backend and AI pipeline:

```text
PDF Processing
      ↓
Cleaning
      ↓
Chunking
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Retriever
      ↓
Context Expansion
      ↓
Conversation History
      ↓
Prompt Construction
      ↓
LLM
      ↓
FastAPI
      ↓
Basic Frontend
```

The frontend is therefore considered the **interface layer**, while the main technical work of the project is concentrated in the data pipeline, RAG system, backend API, and LLM integration.

---

# Final Note

This frontend should be judged based on what it was intended to accomplish: **providing a working interface for the AI assistant**.

It was built during a short 2–3 day development period alongside learning and implementing the backend, RAG pipeline, vector database, retrieval logic, conversation history, prompt engineering, and API integration.

I am **not a frontend developer and do not plan to become one**. The frontend was intentionally kept simple because the primary goal of this project was to learn and implement the AI/backend side of the system.

The important result is that the complete system can be used end-to-end:

```text
User
 ↓
Frontend
 ↓
FastAPI
 ↓
Conversation History + RAG
 ↓
ChromaDB
 ↓
Retrieved Context
 ↓
Prompt
 ↓
LLM
 ↓
Response
 ↓
Frontend
```

For this project, **functionality and learning were prioritized over frontend polish**.
