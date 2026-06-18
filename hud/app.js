const API_BASE_URL = "http://127.0.0.1:8787";
const SPEAKING_RETURN_DELAY_MS = 1400;

const faceCore = document.getElementById("faceCore");
const healthButton = document.getElementById("healthButton");
const healthBadge = document.getElementById("healthBadge");
const healthStatus = document.getElementById("healthStatus");
const healthProvider = document.getElementById("healthProvider");
const healthAdapter = document.getElementById("healthAdapter");
const healthMessage = document.getElementById("healthMessage");
const chatButton = document.getElementById("chatButton");
const chatInput = document.getElementById("chatInput");
const voiceOutput = document.getElementById("voiceOutput");
const visualOutput = document.getElementById("visualOutput");
const traceOutput = document.getElementById("traceOutput");

function setFaceState(state) {
  const allowedStates = ["idle", "online", "offline", "thinking", "speaking", "error"];
  const nextState = allowedStates.includes(state) ? state : "idle";
  faceCore.className = "face-core face-" + nextState;
}

function returnFaceToOnlineAfterSpeaking() {
  window.setTimeout(function() {
    setFaceState("online");
  }, SPEAKING_RETURN_DELAY_MS);
}

function setHealthBadge(online) {
  healthBadge.textContent = online ? "online" : "offline";
  healthBadge.className = online ? "badge badge-online" : "badge badge-offline";
}

function renderHealth(data) {
  const online = Boolean(data.app_ready);

  setHealthBadge(online);
  setFaceState(online ? "online" : "offline");
  healthStatus.textContent = online ? "Online" : "Offline";
  healthProvider.textContent = data.provider_name || "None";
  healthAdapter.textContent = data.adapter_name || "Unknown";
  healthMessage.textContent = "LuciferOS API responded successfully.";
}

function renderHealthError(error) {
  setHealthBadge(false);
  setFaceState("error");
  healthStatus.textContent = "Offline";
  healthProvider.textContent = "Unknown";
  healthAdapter.textContent = "Unknown";
  healthMessage.textContent = "API health check failed: " + error;
}

function renderChat(data) {
  setFaceState("speaking");
  voiceOutput.textContent = data.voice_summary || "No voice summary returned.";
  visualOutput.textContent = data.visual_text || "No visual response returned.";
  traceOutput.textContent = "trace_id: " + (data.trace_id || "none");
  returnFaceToOnlineAfterSpeaking();
}

function renderChatError(error) {
  setFaceState("error");
  voiceOutput.textContent = "Chat request failed.";
  visualOutput.textContent = String(error);
  traceOutput.textContent = "trace_id: none";
}

async function checkHealth() {
  healthMessage.textContent = "Checking API...";

  try {
    const response = await fetch(API_BASE_URL + "/health");
    const data = await response.json();
    renderHealth(data);
  } catch (error) {
    renderHealthError(error);
  }
}

async function sendChat() {
  const text = chatInput.value.trim();

  if (!text) {
    voiceOutput.textContent = "Write a message first.";
    visualOutput.textContent = "No request sent.";
    traceOutput.textContent = "trace_id: none";
    return;
  }

  setFaceState("thinking");
  voiceOutput.textContent = "Thinking...";
  visualOutput.textContent = "Waiting for LuciferOS API...";
  traceOutput.textContent = "trace_id: pending";

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
    renderChat(data);
  } catch (error) {
    renderChatError(error);
  }
}

healthButton.addEventListener("click", checkHealth);
chatButton.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    sendChat();
  }
});
