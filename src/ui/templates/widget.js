//src/ui/templates/widget.js
import logging 

const chatbox = document.getElementById("chatbox");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

// In production, inject this from tenant onboarding flow
// For now, hardcode or fetch from /chat/session
const sessionToken = "f2c8b6f0-1234-4abc-9def-567890abcdef";



function appendMessage(text, cls) {   
    const div = document.createElement("div");
    div.className = cls;
    div.textContent = text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

sendBtn.onclick = async () => {
    const message = input.value.trim();
    logging.info(f"logging inside sendBtn.onclick in widget.js with message: {message}")
    if (!message) return;
    logging.info(f"message is present")
    appendMessage("You: " + message, "user");
    input.value = "";

    // Create one agent div up front
    let agentMsg = "";
    let agentDiv = document.createElement("div");
    agentDiv.className = "agent";
    chatbox.appendChild(agentDiv);

    try {
        const response = await fetch("/chat/query/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_token: sessionToken, message })
        });

        if (!response.ok || !response.body) {
            agentDiv.textContent = "Agent: [Error: " + response.status + "]";
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            console.log("Received chunk:", chunk);

            chunk.split("\n").forEach(line => {
                if (line.startsWith("data: ")) {
                    const token = line.substring(6);
                    agentMsg += token;
                    agentDiv.textContent = "Agent: " + agentMsg; // ✅ update progressively
                }
            });
        }
    } catch (err) {
        console.error("Send error:", err);
        agentDiv.textContent = "Agent: [Error sending message]";
    }
};


// sendBtn.onclick = async () => {
//     const message = input.value.trim();
//     if (!message) return;
//     appendMessage("You: " + message, "user");
//     input.value = "";

// // Create one agent div up front 
//     let agentMsg = ""; 
//     let agentDiv = document.createElement("div"); 
//     agentDiv.className = "agent"; 
//     chatbox.appendChild(agentDiv);

// const response = await fetch("/chat/query/stream", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ session_token: sessionToken, message })
//     });

//     const reader = response.body.getReader();
//     const decoder = new TextDecoder("utf-8");
  

// while (true) {
//     const { done, value } = await reader.read();
//     console.log("Received chunk:", chunk);
//     if (done) break;
//     const chunk = decoder.decode(value, { stream: true });
//     chunk.split("\n").forEach(line => {
//         if (line.startsWith("data: ")) {
//             const token = line.substring(6); 
//             agentMsg += token; agentDiv.textContent = "Agent: " + agentMsg; // ✅ update progressively 
//         } 
//     });
//  }
//  };