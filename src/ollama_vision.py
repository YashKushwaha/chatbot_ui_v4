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
            context_window=512,
            num_output=512,
            is_chat_model=False,
            is_function_calling_model=False,
        )

    def process_ollama_stream(self, response):
        full_response = ""

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                delta = chunk.get("response", "")
                full_response += delta
                yield CompletionResponse(text=full_response, delta=delta)

                if chunk.get("done", False):
                    break

    def stream_complete(self, prompt: str, image_source: str = None, **kwargs) -> CompletionResponseGen:       

        payload = {
            "model": self.model_name,
            "prompt": prompt,
        }
        if image_source:
            #encoded_image = self._encode_image(image_source)
            if isinstance(image_source, list):
                payload['images'] = image_source
            else:
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

    def complete(self, prompt: str, image_source: str = None, **kwargs) -> CompletionResponse:

        payload = {
            "model": self.model_name,
            "prompt": prompt,
        }
        if image_source:
            #encoded_image = self._encode_image(image_source)
            if isinstance(image_source, list):
                payload['images'] = image_source
            else:
                payload['images'] = [image_source]

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.ollama_url,
            headers=headers,
            data=json.dumps(payload),
            stream=False
        )
        final_response = None
        for chunk in self.process_ollama_stream(response):
            final_response = chunk  # keep updating with latest

        return final_response  # return only once, with full text
        
    def _is_url(self, path_or_url: str) -> bool:
        parsed = urlparse(path_or_url)
        return parsed.scheme in ("http", "https")

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
 
    response_gen = llm.stream_complete(prompt=query, image_source=image_source)

    final_response = ""
    for chunk in response_gen:
        print(chunk.delta, end="", flush=True)  # Print tokens as they stream
        final_response += chunk.delta
    """
    response_gen = llm.complete(prompt=query, image_source=image_source)
    print(response_gen.text)
       """
    #print("\n\nFull response:")
    #print(final_response)