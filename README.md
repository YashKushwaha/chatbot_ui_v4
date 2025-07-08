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
- Link to demo video given below:
[![Watch Demo](https://img.youtube.com/vi/XOft0mfv8bo/0.jpg)](https://youtu.be/Sk9ZbGdT8Mg)
