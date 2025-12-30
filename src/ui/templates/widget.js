#src/ui/templates/widget.js
const chatbox = document.getElementById("chatbox");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

// In production, inject this from tenant onboarding flow
// For now, hardcode or fetch from /chat/session
const sessionToken = "e26f0fa7-e228-4acb-8391-757caaa99c5f";



function appendMessage(text, cls) {   
    const div = document.createElement("div");
    div.className = cls;
    div.textContent = text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

sendBtn.onclick = async () => {
    const message = input.value.trim();
    if (!message) return;
    appendMessage("You: " + message, "user");
    input.value = "";

// Create one agent div up front 
    let agentMsg = ""; 
    let agentDiv = document.createElement("div"); 
    agentDiv.className = "agent"; 
    chatbox.appendChild(agentDiv);

const response = await fetch("/chat/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_token: sessionToken, message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
  

while (true) {
    const { done, value } = await reader.read();
    console.log("Received chunk:", chunk);
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    chunk.split("\n").forEach(line => {
        if (line.startsWith("data: ")) {
            const token = line.substring(6); 
            agentMsg += token; agentDiv.textContent = "Agent: " + agentMsg; // ✅ update progressively 
        } 
    });
 }
 };