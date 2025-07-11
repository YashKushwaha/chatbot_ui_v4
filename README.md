### Overview

This is my 4th project exploring the use of llama index for LLM applications. In the project, I have implemented multi modal RAG.

**Dataset**

- [flickr30k](https://huggingface.co/datasets/nlphuji/flickr30k) dataset on Huggingface is used to build the knowledge base for the project
- the dataset consists of 31k images. Each image also has 5 captions attached to it

**Embedding Model**

- [laion/CLIP-ViT-L-14-laion2B-s32B-b82K](https://huggingface.co/laion/CLIP-ViT-L-14-laion2B-s32B-b82K) is used as the embedding model
- It maps text and image data into the same embedding space
- [OpenClip library](https://github.com/mlfoundations/open_clip) (`pip install open-clip-torch`) used to run the embedding model

**Vector Database**

- **chromadb** (`pip install chromadb`) is used to store the embeddings for images and captions
- Two collections were created - 
  - `images` for storing embeddings of images
  - `captions` for storing captions 

**Mongodb Database**

- Used to store captions and filenames
- Useful in mapping metadata stored in vector databases to full record
- The database service was running locally using docker `docker pull mongo:8.0.9`

**Sample record in HuggingFace dataset**
- Dataset is stored in `.arrow` format where each row represents image and its captions 
```python
{'image': <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=333x500>,
 'caption': ['Two young guys with shaggy hair look at their hands while hanging out in the yard.',
  'Two young, White males are outside near many bushes.',
  'Two men in green shirts are standing in a yard.',
  'A man in a blue shirt standing in a garden.',
  'Two friends enjoy time spent together.'],
 'sentids': ['0', '1', '2', '3', '4'],
 'split': 'train',
 'img_id': '0',
 'filename': '1000092795.jpg'}
 ```
---
### Retrieval Pipeline

To test the retrieval pipeline end to end, it has been connected to front end and is available at the endpoint `/retriever`
- User query is taken from front end and passed to the back end function
- The back end FastAPI function, accessed the vector store & embedding model, converts the user query into embedding and performs query operation on vector store
- By default, vector store returns top 5 results. File name of the image is stored in the nodes.
- File name is extracted from the nodes and coverted to text
- The front end already has the capability to render markdown thus instead of sending the filename, an url to the image is returned
- Custom endpoint has been implemented to return files/images stored locally through URL
- Demo video can be seen on the link give below:

[![Watch Demo](https://img.youtube.com/vi/XOft0mfv8bo/0.jpg)](https://youtu.be/XOft0mfv8bo)


### LLM Vision Integration

- To build full fledged multi modal rag application we need to integrate our retrieval pipeline with LLM that has vision capability
- I have selected `gemma3` model with [12 billion parameters](https://ollama.com/library/gemma3:12b) for this project
- `llama-index` does support multi modal LLms like OpenAI ([see example here](https://docs.llamaindex.ai/en/stable/examples/multi_modal/openai_multi_modal/)), Anthropic ([see example here](https://docs.llamaindex.ai/en/stable/examples/multi_modal/anthropic_multi_modal/)) but this feature is not available for all LLMs
- For this project, I have created custom LLM class to work with `gemma3` model

**Testing the LLM**

- To evaluate the LLM for image reasoning, apart from running the model as a script, it was also integrated with a UI where user can paste image and ask question
- A video demo of image reasoning using `gemma` can be seen on the follwing link

 [![Watch Demo](https://img.youtube.com/vi/ZQtXqu9Fboo/0.jpg) ](https://youtu.be/ZQtXqu9Fboo)

 ### Full multi modal RAG pipeline

 After testing the retrieval and generation components individually, I tested both components together. 
 Experiment:
 - User query sent to vector DB for retrieval, top 5 results returned
 - Images loaded from image database based on the filenames returned from retrieval, converted to base64 strings
 - User query loaded into prompt, base64 images added to the payload. The prompt asks the LLM to compare images with user query and return the most relevant image
 - LLM returns the name of most of most relevant image, now the llm response can be parsed and image can be rendered separately in the front end

For further refining of the code, I converted the retrieval and generation components as Tools, the pipeline worked but for some reason inference is now happening on CPU instead of GPU. On further reading, I came to know that retrieval is best candidate for converting to a tool however LLM calls should not be done in Tools.

I also built Workflow architecture but still the inference is happening on CPU. This is not an issue when using a remote/cloud LLM service (openai, mistral etc) but it got me curious why this has started to happen. Maybe it's a Ollama / WSL issue.

While my simple end to end script is working, I need to deep dive into agent architecture, ochestration and workflow etc to make the LLM calls more robust. 
