const API_URL = "http://localhost:8000/api/chat/";

const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatMessages = document.getElementById("chat-messages");


// Generate a session ID for this browser session
let sessionId = sessionStorage.getItem("nayatel_session_id");

if (!sessionId) {
    sessionId = crypto.randomUUID();

    sessionStorage.setItem(
        "nayatel_session_id",
        sessionId
    );
}


// Add a message to the chat window
function addMessage(role, text) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("assistant-message");
    }


    const label = document.createElement("div");

    label.classList.add("message-label");

    label.textContent =
        role === "user"
            ? "You"
            : "NayaTel AI";


    const content = document.createElement("div");

    content.classList.add("message-content");

    content.textContent = text;


    messageDiv.appendChild(label);
    messageDiv.appendChild(content);

    chatMessages.appendChild(messageDiv);


    // Automatically scroll to latest message
    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


// Send message to FastAPI
async function sendMessage() {

    const message = messageInput.value.trim();


    // Don't send empty messages
    if (!message) {
        return;
    }


    // Display user's message
    addMessage("user", message);


    // Clear input
    messageInput.value = "";


    // Disable button while waiting
    sendButton.disabled = true;

    sendButton.textContent = "Sending...";


    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })

        });


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );

        }


        const data = await response.json();


        // Display AI response
        addMessage(
            "assistant",
            data.answer
        );


    } catch (error) {

        console.error(error);

        addMessage(
            "assistant",
            "Sorry, I couldn't connect to the NayaTel AI Assistant."
        );

    } finally {

        sendButton.disabled = false;

        sendButton.textContent = "Send";

        messageInput.focus();
    }
}


// Send when button is clicked
sendButton.addEventListener(
    "click",
    sendMessage
);


// Send when Enter is pressed
messageInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }

    }
);