function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    appendMessage(userInput, "user");
    document.getElementById("user-input").value = "";

    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.response, "bot");
    })
    .catch(error => console.error('Error:', error));
}

function appendMessage(message, type) {
    var chatWindow = document.getElementById("chat-window");
    var chatBubble = document.createElement("div");
    chatBubble.textContent = message;
    chatBubble.classList.add("chat-bubble");
    chatBubble.classList.add(type);
    chatWindow.appendChild(chatBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
