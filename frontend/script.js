const API_URL = "https://nayatel-ai-backend-copy-production.up.railway.app/api/chat";

const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatMessages = document.getElementById("chat-messages");


let sessionId = sessionStorage.getItem("nayatel_session_id");

if (!sessionId) {
    sessionId = crypto.randomUUID();

    sessionStorage.setItem(
        "nayatel_session_id",
        sessionId
    );
}

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


    
    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


async function sendMessage() {

    const message = messageInput.value.trim();


    if (!message) {
        return;
    }

    addMessage("user", message);

    messageInput.value = "";

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


sendButton.addEventListener(
    "click",
    sendMessage
);


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