// Utility: Scroll to bottom of chat
function scrollToBottom(scrollContainer) {
  scrollContainer.scrollTop = scrollContainer.scrollHeight;
}

// Utility: Create and append a user message
function appendUserMessage(message, chatHistory) {
  const newMsg = document.createElement("div");
  newMsg.className = "user-message";
  newMsg.innerHTML = message.replace(/\n/g, "<br>");
  chatHistory.appendChild(newMsg);
}
function appendServerMessage(markdownText, chatHistory) {
  const replyMsg = document.createElement("div");
  replyMsg.className = "server-message";

  // Step 1: Use marked to parse markdown
  let htmlContent = marked.parse(markdownText || "No response");

  // Step 3: Set HTML and highlight
  replyMsg.innerHTML = htmlContent;

    // Highlight any <pre><code> blocks after inserting HTML
   replyMsg.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });

  chatHistory.appendChild(replyMsg);
  scrollToBottom(scrollContainer);
}

async function sendMessageToBackend(message) {
  const formData = new FormData();
  formData.append("message", message);

  try {
    const response = await fetch(window.CHAT_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    return data; // ⬅️ just return the response
  } catch (err) {
    console.error("Send failed", err);
    return null;
  }
}

async function sendMessageToBackendStream(message, chatHistory) {
  const formData = new FormData();
  formData.append("message", message);

  try {
    const response = await fetch(window.CHAT_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok || !response.body) {
      throw new Error("Network or server error");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let replyMsg = document.createElement("div");
    replyMsg.className = "server-message";
    chatHistory.appendChild(replyMsg);

    let markdownBuffer = "";

    // Read streamed data
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      markdownBuffer += chunk;

      // Render and update innerHTML with parsed markdown
      const htmlContent = marked.parse(markdownBuffer);
      replyMsg.innerHTML = htmlContent;

      // Highlight newly added code blocks
      replyMsg.querySelectorAll("pre code:not(.hljs)").forEach((block) => {
        hljs.highlightElement(block);
      });
      renderMathInElement(replyMsg, {
          delimiters: [
              { left: "$$", right: "$$", display: true },
              { left: "$", right: "$", display: false },
          ],
      });
      scrollToBottom(scrollContainer);
    }


  } catch (err) {
    console.error("Streaming failed", err);
  }
}

async function handleUserInput(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();

    const message = inputDiv.innerText.trim();    
    inputDiv.innerText = "";
    if (!message) return;
    
    appendUserMessage(message, chatHistory);    
    await sendMessageToBackendStream(message, chatHistory);
    
  }
}

const inputDiv = document.getElementById("user-input-div");
const chatHistory = document.getElementById("chat-history");
const scrollContainer = document.getElementById("chat-history-container");

inputDiv.addEventListener("keydown", handleUserInput);