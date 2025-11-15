// Main function
async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const msg = inputField.value;

    if (!msg.trim()) return;

    const chatbox = document.getElementById("chatbox");

    // Show user message
    chatbox.innerHTML += `<p class="user-msg"><strong>You:</strong> ${msg}</p>`;
    chatbox.scrollTop = chatbox.scrollHeight;

    inputField.value = "";

    const response = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
    });

    const data = await response.json();

    // Show bot message
        chatbox.innerHTML += `<p class="bot-msg"><strong>Jason bot:</strong> ${data.reply}</p>`;
        chatbox.scrollTop = chatbox.scrollHeight;
}

// Click Send
// When it is clicked, call sendMessage function
document.getElementById("send-btn").onclick = sendMessage; // this is not sendMessage(); so not calling function, it is passing the function.
// the difference between calling function with () and running function without () is that calling is immediate.
// without (), just telling it to hold the function for now, not running it immediately.

// Press Enter
// When enter is pressed, call sendMessage function
document.getElementById("user-input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();   // prevents newline. Safe to keep it. If using <form> or <textarea>, this does a job.
        sendMessage();
    }
});