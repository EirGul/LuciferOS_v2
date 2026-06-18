const API_BASE_URL = "http://127.0.0.1:8787";

const healthButton = document.getElementById("healthButton");
const healthOutput = document.getElementById("healthOutput");
const chatButton = document.getElementById("chatButton");
const chatInput = document.getElementById("chatInput");
const chatOutput = document.getElementById("chatOutput");

function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

async function checkHealth() {
  healthOutput.textContent = "Checking API...";

  try {
    const response = await fetch(API_BASE_URL + "/health");
    const data = await response.json();
    healthOutput.textContent = formatJson(data);
  } catch (error) {
    healthOutput.textContent = "API health check failed: " + error;
  }
}

async function sendChat() {
  const text = chatInput.value.trim();

  if (!text) {
    chatOutput.textContent = "Write a message first.";
    return;
  }

  chatOutput.textContent = "Sending...";

  try {
    const response = await fetch(API_BASE_URL + "/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: text,
        metadata: {
          source: "static-hud"
        }
      })
    });

    const data = await response.json();
    chatOutput.textContent = formatJson(data);
  } catch (error) {
    chatOutput.textContent = "Chat request failed: " + error;
  }
}

healthButton.addEventListener("click", checkHealth);
chatButton.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    sendChat();
  }
});
