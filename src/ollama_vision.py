from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
import json
import os
import requests
import base64

from urllib.parse import urlparse

class OllamaVisionLLM(CustomLLM):
    model_name: str
    ollama_url: str = "http://localhost:11434/api/generate"

    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=4096,
            num_output=1024,
            is_chat_model=False,
            is_function_calling_model=False,
        )
    """
    def _encode_image(self, image_source):
        # Determine if it's a URL
        if self._is_url(image_source):
            response = requests.get(image_source)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode("utf-8")
            else:
                raise Exception(f"Failed to fetch image from URL: {image_source} — {response.status_code}")
        elif isinstance(image_source, bytes):
            return base64.b64encode(image_source).decode("utf-8")
        else:
            # Assume it's a local file path
            if not os.path.exists(image_source):
                raise FileNotFoundError(f"Local image not found: {image_source}")
            with open(image_source, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    """
    def stream_complete(self, prompt: str, image_source: str, **kwargs) -> CompletionResponseGen:
        encoded_image = self._encode_image(image_source)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [encoded_image]
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.ollama_url,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        )

        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                delta = chunk.get("response", "")
                full_response += delta
                yield CompletionResponse(text=full_response, delta=delta)

    def complete(self, prompt: str, image_source: str, **kwargs) -> CompletionResponse:
        encoded_image = self._encode_image(image_source)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [encoded_image]
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.ollama_url, headers=headers, data=json.dumps(payload), stream=True)

        output = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                output += chunk.get("response", "")

        return CompletionResponse(text=output)
    
    def _is_url(self, path_or_url: str) -> bool:
        parsed = urlparse(path_or_url)
        return parsed.scheme in ("http", "https")
    
    def _encode_image(self, image_source: str) -> str:
        parsed = urlparse(image_source)
        if parsed.scheme in ("http", "https"):
            response = requests.get(image_source)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode("utf-8")
            raise Exception(f"Failed to fetch image from URL: {response.status_code}")
        elif isinstance(image_source, bytes):
            return base64.b64encode(image_source).decode("utf-8")

        else:
            if not os.path.exists(image_source):
                raise FileNotFoundError(f"Image not found: {image_source}")
            with open(image_source, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    

if __name__ == '__main__':
    model_name = 'gemma3:12b'
    llm = OllamaVisionLLM(model_name=model_name)
    image_url = 'http://localhost:8000/get_image?filename=65567.jpg'
    query = 'Can you describe this image ?'
    #output = llm.complete(prompt=query, image_source=image_url)
    #print(output)

        # Stream response
    response_gen = llm.stream_complete(prompt=query, image_source=image_url)

    final_response = ""
    for chunk in response_gen:
        print(chunk.delta, end="", flush=True)  # Print tokens as they stream
        final_response += chunk.delta

    print("\n\nFull response:")
    print(final_response)