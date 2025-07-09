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
#from fastapi import UploadFile
from starlette.datastructures import UploadFile

from typing import Union
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

    def stream_complete(self, prompt: str, image_source: str = None, **kwargs) -> CompletionResponseGen:       

        payload = {
            "model": self.model_name,
            "prompt": prompt,
        }
        if image_source:
            #encoded_image = self._encode_image(image_source)
            payload['images'] = [image_source]

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
    '''
    def _encode_image(self, image_source: Union[str, UploadFile]) -> str:
        """
        Convert a FastAPI UploadFile, local path, or URL into a base64‑encoded string.

        Raises:
            FileNotFoundError: bad local path
            ValueError: empty UploadFile or unknown scheme
            Exception: HTTP error on URL fetch
        """
        # ---- 1) FastAPI UploadFile --------------------------------------------
        if isinstance(image_source, UploadFile):
            # read() consumes the stream; remember to rewind if you need it again
            image_bytes = image_source.file.read()
            if not image_bytes:
                raise ValueError("UploadFile is empty")
            # optional: image_source.file.seek(0)  # rewind for future use
            return base64.b64encode(image_bytes).decode("utf-8")

        # ---- 2) str – could be URL or local path ------------------------------
        if not isinstance(image_source, str):
            raise ValueError("image_source must be str or UploadFile")

        parsed = urlparse(image_source)

        # 2a) Remote URL
        if parsed.scheme in ("http", "https"):
            resp = requests.get(image_source, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"Failed to fetch image: HTTP {resp.status_code}")
            return base64.b64encode(resp.content).decode("utf-8")

        # 2b) Local file path
        if os.path.exists(image_source):
            with open(image_source, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

        # 2c) Anything else is unsupported
        raise FileNotFoundError(f"Image not found or unsupported path: {image_source}")
        '''

def get_image(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")

if __name__ == '__main__':
    model_name = 'gemma3:12b'
    llm = OllamaVisionLLM(model_name=model_name)
    image_url = 'http://localhost:8000/get_image?filename=65567.jpg'
    query = 'Can you describe this image ?'

    image_source = get_image(image_url)

    response_gen = llm.stream_complete(prompt=query, image_source=image_url)

    final_response = ""
    for chunk in response_gen:
        print(chunk.delta, end="", flush=True)  # Print tokens as they stream
        final_response += chunk.delta

    print()
    #print("\n\nFull response:")
    #print(final_response)