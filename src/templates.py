from jinja2 import Template

QUERY_TEMPLATE = """
You are a helpful assistant. Your job is to evaluate the relevance of a list of images to the user query.

Images are going to be in the format <image_num> : <image_id> e.g.
<image_1> : 123.jpg
<image_2> : 456.jpg
<image_3> : abc.jpg

Identify the most relevant image and also write a short description of the image.
Output in json format only using the format:
{"best_image":"456.jpg",
 "description": "Description of the image"
}

USER QUERY:
{{user_query}}

IMAGES:
{{images}}

"""
image_evaluator_template = Template(QUERY_TEMPLATE)