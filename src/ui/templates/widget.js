(function () {
  const chatbox = document.getElementById("chatbox");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("send");

  // Parse org_id from widget URL
  const urlParams = new URLSearchParams(window.location.search);
  const orgId = parseInt(urlParams.get("org_id"), 10);


  let API_BASE = null;
  let SESSION_TTL = null;
  let sessionToken = null;
  let threadId = null;   // <-- NEW: track thread_id

  // Load tenant-specific config from backend
  async function loadConfig() {
    try {
      const res = await fetch("/config.json");
      if (!res.ok) throw new Error(`Config fetch failed: ${res.status}`);
      const cfg = await res.json();
      API_BASE = cfg.API_BASE;
      SESSION_TTL = cfg.SESSION_TTL;
      console.log("✅ Config loaded:", API_BASE, SESSION_TTL);
    } catch (err) {
      console.error("Failed to load config.json, fallback to default", err);
      API_BASE = "https://chat.zenai.co.in";
      SESSION_TTL = 30;
    }
  }

  // Create or renew a short-lived session
  async function createSession() {
    try {
      const res = await fetch(`${API_BASE}/chat/session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ org_id: orgId })
      });
      if (!res.ok) throw new Error(`Session creation failed: ${res.status}`);
      const data = await res.json();
      sessionToken = data.session_token;
      threadId = data.thread_id;   // <-- capture thread_id
      console.log("🔑 New session:", sessionToken, "🧵 Thread:", threadId);
    } catch (err) {
      console.error("Failed to create session", err);
    }
  }

  function appendMessage(text, cls) {
    const div = document.createElement("div");
    div.className = cls;
    div.textContent = text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;
    appendMessage("You: " + message, "user");
    input.value = "";

    let agentMsg = "";
    let agentDiv = document.createElement("div");
    agentDiv.className = "agent";
    chatbox.appendChild(agentDiv);

    try {
      let response = await fetch(`${API_BASE}/chat/query/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_token: sessionToken,
          org_id: orgId,
          thread_id: threadId,   // <-- send thread_id
          message
        })
      });

      // Auto-renew if session expired
      if (response.status === 404) {
        await createSession();
        response = await fetch(`${API_BASE}/chat/query/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_token: sessionToken,
            org_id: orgId,
            thread_id: threadId,
            message
          })
        });
      }

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

        chunk.split("\n").forEach(line => {
          if (line.startsWith("data: ")) {
            try {
              const payload = JSON.parse(line.substring(6));
              agentMsg += payload.response;
              agentDiv.textContent = "Agent: " + agentMsg;
              console.log("Thread:", payload.thread_id, "Status:", payload.status);
            } catch {
              const token = line.substring(6);
              agentMsg += token;
              agentDiv.textContent = "Agent: " + agentMsg;
            }
          }
        });
      }
    } catch (err) {
      console.error("Send error:", err);
      agentDiv.textContent = "Agent: [Error sending message]";
    }
  }

  sendBtn.onclick = sendMessage;

  // Initialize config and session before use
  (async () => {
    await loadConfig();
    await createSession();
  })();
})();

//Working memory less agent

// // src/ui/templates/widget.js
// (function () {
//   const chatbox = document.getElementById("chatbox");
//   const input = document.getElementById("input");
//   const sendBtn = document.getElementById("send");

//   // Parse org_id from widget URL
//   const urlParams = new URLSearchParams(window.location.search);
//   const orgId = urlParams.get("org_id");

//   let API_BASE = null;
//   let SESSION_TTL = null;
//   let sessionToken = null;

//   // Load tenant-specific config from backend
//   async function loadConfig() {
//     try {
//       const res = await fetch("/config.json");
//       const cfg = await res.json();
//       API_BASE = cfg.API_BASE;
//       SESSION_TTL = cfg.SESSION_TTL;
//       console.log("✅ Config loaded:", API_BASE, SESSION_TTL);
//     } catch (err) {
//       console.error("Failed to load config.json, fallback to default", err);
//       API_BASE = "https://chat.zenai.co.in";
//       SESSION_TTL = 30;
//     }
//   }

//   // Create or renew a short-lived session
//   async function createSession() {
//     try {
//       const res = await fetch(`${API_BASE}/chat/session`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ org_id: orgId })
//       });
//       const data = await res.json();
//       sessionToken = data.session_token;
//       console.log("🔑 New session token:", sessionToken);
//     } catch (err) {
//       console.error("Failed to create session", err);
//     }
//   }

//   function appendMessage(text, cls) {
//     const div = document.createElement("div");
//     div.className = cls;
//     div.textContent = text;
//     chatbox.appendChild(div);
//     chatbox.scrollTop = chatbox.scrollHeight;
//   }

//   async function sendMessage() {
//     const message = input.value.trim();
//     if (!message) return;
//     appendMessage("You: " + message, "user");
//     input.value = "";

//     let agentMsg = "";
//     let agentDiv = document.createElement("div");
//     agentDiv.className = "agent";
//     chatbox.appendChild(agentDiv);

//     try {
//       let response = await fetch(`${API_BASE}/chat/query/stream`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ session_token: sessionToken, org_id: orgId, message })
//       });

//       // Auto-renew if session expired
//       if (response.status === 404) {
//         await createSession();
//         response = await fetch(`${API_BASE}/chat/query/stream`, {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ session_token: sessionToken, org_id: orgId, message })
//         });
//       }

//       if (!response.ok || !response.body) {
//         agentDiv.textContent = "Agent: [Error: " + response.status + "]";
//         return;
//       }

//       const reader = response.body.getReader();
//       const decoder = new TextDecoder("utf-8");

//       while (true) {
//         const { done, value } = await reader.read();
//         if (done) break;
//         const chunk = decoder.decode(value, { stream: true });

//         chunk.split("\n").forEach(line => {
//           if (line.startsWith("data: ")) {
//             try {
//               const payload = JSON.parse(line.substring(6));
//               agentMsg += payload.response;
//               agentDiv.textContent = "Agent: " + agentMsg;
//               console.log("Thread:", payload.thread_id, "Status:", payload.status);
//             } catch {
//               const token = line.substring(6);
//               agentMsg += token;
//               agentDiv.textContent = "Agent: " + agentMsg;
//             }
//           }
//         });
//       }
//     } catch (err) {
//       console.error("Send error:", err);
//       agentDiv.textContent = "Agent: [Error sending message]";
//     }
//   }

//   sendBtn.onclick = sendMessage;

//   // Initialize config and session before use
//   (async () => {
//     await loadConfig();
//     await createSession();
//   })();
// })();



// (function () {
//   const chatbox = document.getElementById("chatbox");
//   const input = document.getElementById("input");
//   const sendBtn = document.getElementById("send");

//   // Parse org_id from widget URL
//   const urlParams = new URLSearchParams(window.location.search);
//   const orgId = urlParams.get("org_id");

//   let API_BASE = null;
//   let SESSION_TTL = null;
//   let sessionToken = null;

//   // Load tenant-specific config from backend
//   async function loadConfig() {
//     try {
//       const res = await fetch("/config.json");
//       const cfg = await res.json();
//       API_BASE = cfg.API_BASE;
//       SESSION_TTL = cfg.SESSION_TTL;
//       console.log("✅ Config loaded:", API_BASE, SESSION_TTL);
//     } catch (err) {
//       console.error("Failed to load config.json, fallback to default", err);
//       API_BASE = "https://chat.zenai.co.in";
//       SESSION_TTL = 30;
//     }
//   }

//   // Create or renew a short-lived session
//   async function createSession() {
//     try {
//       const res = await fetch(`${API_BASE}/chat/session`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ org_id: orgId })
//       });
//       const data = await res.json();
//       sessionToken = data.session_token;
//       console.log("🔑 New session token:", sessionToken);
//     } catch (err) {
//       console.error("Failed to create session", err);
//     }
//   }

//   function appendMessage(text, cls) {
//     const div = document.createElement("div");
//     div.className = cls;
//     div.textContent = text;
//     chatbox.appendChild(div);
//     chatbox.scrollTop = chatbox.scrollHeight;
//   }

//   async function sendMessage() {
//     const message = input.value.trim();
//     if (!message) return;
//     appendMessage("You: " + message, "user");
//     input.value = "";

//     let agentMsg = "";
//     let agentDiv = document.createElement("div");
//     agentDiv.className = "agent";
//     chatbox.appendChild(agentDiv);

//     try {
//       let response = await fetch(`${API_BASE}/chat/query/stream`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ session_token: sessionToken, org_id: orgId, message })
//       });

//       // Auto-renew if session expired
//       if (response.status === 404) {
//         await createSession();
//         response = await fetch(`${API_BASE}/chat/query/stream`, {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ session_token: sessionToken, org_id: orgId, message })
//         });
//       }

//       if (!response.ok || !response.body) {
//         agentDiv.textContent = "Agent: [Error: " + response.status + "]";
//         return;
//       }

//       const reader = response.body.getReader();
//       const decoder = new TextDecoder("utf-8");

//       while (true) {
//         const { done, value } = await reader.read();
//         if (done) break;
//         const chunk = decoder.decode(value, { stream: true });

//         chunk.split("\n").forEach(line => {
//           if (line.startsWith("data: ")) {
//             try {
//               const payload = JSON.parse(line.substring(6));
//               agentMsg += payload.response;
//               agentDiv.textContent = "Agent: " + agentMsg;
//               console.log("Thread:", payload.thread_id, "Status:", payload.status);
//             } catch {
//               const token = line.substring(6);
//               agentMsg += token;
//               agentDiv.textContent = "Agent: " + agentMsg;
//             }
//           }
//         });
//       }
//     } catch (err) {
//       console.error("Send error:", err);
//       agentDiv.textContent = "Agent: [Error sending message]";
//     }
//   }

//   sendBtn.onclick = sendMessage;

//   // Initialize config and session before use
//   (async () => {
//     await loadConfig();
//     await createSession();
//   })();
// })();





// //src/ui/templates/widget.js
// const chatbox = document.getElementById("chatbox");
// const input = document.getElementById("input");
// const sendBtn = document.getElementById("send");

// // In production, inject this from tenant onboarding flow
// // For now, hardcode or fetch from /chat/session
// const sessionToken = "a8f63327-3a75-4c3b-a44f-e6f67edbd872";
// console.log("✅ widget.js loaded");


// function appendMessage(text, cls) {   
//     const div = document.createElement("div");
//     div.className = cls;
//     div.textContent = text;
//     chatbox.appendChild(div);
//     chatbox.scrollTop = chatbox.scrollHeight;
// }

// sendBtn.onclick = async () => {
//     const message = input.value.trim();
//     console.log("Binding send button:", sendBtn);
//     if (!message) return;
//     console.log("post Send click:", message);
//     appendMessage("You: " + message, "user");
//     input.value = "";

//     // Create one agent div up front
//     let agentMsg = "";
//     let agentDiv = document.createElement("div");
//     agentDiv.className = "agent";
//     chatbox.appendChild(agentDiv);

//     try {
//         const response = await fetch("/chat/query/stream", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ session_token: sessionToken, message })
//         });
//         console.log("Response status:", response.status);
//         if (!response.ok || !response.body) {
//             agentDiv.textContent = "Agent: [Error: " + response.status + "]";
//             return;
//         }

//         const reader = response.body.getReader();
//         const decoder = new TextDecoder("utf-8");   
//         console.log("widget before while loop:");
//         while (true) {
//             const { done, value } = await reader.read();
//             if (done) break;

//             const chunk = decoder.decode(value, { stream: true });
//             console.log("Received chunk:", chunk);

//             chunk.split("\n").forEach(line => {
//                 if (line.startsWith("data: ")) {
//                     const token = line.substring(6);
//                     agentMsg += token;
//                     agentDiv.textContent = "Agent: " + agentMsg; // ✅ update progressively
//                 }
//             });
//         }
//     } catch (err) {
//         console.error("Send error:", err);
//         agentDiv.textContent = "Agent: [Error sending message]";
//     }
// };


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