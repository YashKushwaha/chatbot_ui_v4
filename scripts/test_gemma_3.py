import base64
import json
import requests

# === Config ===
image_path = "local_only/data/images/36979.jpg"  # Change this to your actual image file
model_name = "gemma3:12b"
prompt = "Describe this image"
ollama_url = "http://localhost:11434/api/generate"

# === Step 1: Encode the image to base64 ===
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

# === Step 2: Prepare the JSON payload ===
payload = {
    "model": model_name,
    "prompt": prompt,
    "images": [encoded_image]
}

headers = {
    "Content-Type": "application/json"
}

# === Step 3: Send the POST request (with streaming enabled) ===
response = requests.post(ollama_url, headers=headers, data=json.dumps(payload), stream=True)

# === Step 4: Handle streaming response (JSON per line) ===
print("Response:")
for line in response.iter_lines():
    if line:
        try:
            chunk = json.loads(line.decode("utf-8"))
            print(chunk.get("response", ""), end="", flush=True)
        except json.JSONDecodeError:
            print(f"\n[Warning] Could not decode line: {line.decode('utf-8')}")
