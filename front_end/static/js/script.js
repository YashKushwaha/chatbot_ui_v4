// Utility: Scroll to bottom of chat
function scrollToBottom(scrollContainer) {
  scrollContainer.scrollTop = scrollContainer.scrollHeight;
}

// Utility: Create and append a user message
function appendUserMessage(message, chatHistory, imageFile = null) {
  // --- Text Message ---
  if (message && message.trim() !== "") {
    const textDiv = document.createElement("div");
    textDiv.className = "user-message";
    textDiv.innerHTML = message.replace(/\n/g, "<br>");
    chatHistory.appendChild(textDiv);
  }
  if (imageFile) {
    const imageDiv = document.createElement("div");
    imageDiv.className = "user-message";

    const img = document.createElement("img");
    img.src = URL.createObjectURL(imageFile);
    img.style.maxWidth = "200px";  // adjust as needed
    img.style.borderRadius = "8px";
    img.alt = "User uploaded image";

    imageDiv.appendChild(img);
    chatHistory.appendChild(imageDiv);
  }

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

async function sendMessageToBackendStream(message, pastedImageFile, chatHistory) {
  const formData = new FormData();
  formData.append("message", message);

  if (pastedImageFile) {
    console.log('Image added to form data');
    formData.append("image", pastedImageFile);
  }

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
    
    appendUserMessage(message, chatHistory, pastedImageFile);  
    const previewContainer = document.getElementById("imagePreviewContainer");
    previewContainer.innerHTML = ""; // clear previous  
    await sendMessageToBackendStream(message, pastedImageFile, chatHistory);
    pastedImageFile = null;

  }
}

function showImagePreview(file) {
  const previewContainer = document.getElementById("imagePreviewContainer");
  console.log('Image preview container selected')
  previewContainer.innerHTML = ""; // clear previous

  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  img.style.maxWidth = "120px";
  img.style.borderRadius = "6px";
  img.style.marginTop = "8px";

  const removeBtn = document.createElement("span");
  removeBtn.innerHTML = "&times;";
  removeBtn.className = "remove-btn";
  removeBtn.onclick = () => {
    pastedImageFile = null;
    previewContainer.innerHTML = "";
  };

  previewContainer.appendChild(img);
  previewContainer.appendChild(removeBtn);
}

async function handleImagePaste(e) {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      e.preventDefault(); 
      const blob = item.getAsFile();
      if (blob) {
        pastedImageFile = blob;
        // Optional: Show a preview of the pasted image
        showImagePreview(blob);

      }
    }
  }
};
const inputDiv = document.getElementById("user-input-div");
const chatHistory = document.getElementById("chat-history");
const scrollContainer = document.getElementById("chat-history-container");
let pastedImageFile = null;  // global reference

inputDiv.addEventListener("keydown", handleUserInput);
inputDiv.addEventListener("paste", handleImagePaste);