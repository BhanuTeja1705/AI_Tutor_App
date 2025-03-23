import google.genai as genai
from PIL import Image

import io
import os
import requests
from io import BytesIO
GOOGLE_API_KEY="AIzaSyAOz1lt8GWmd8T5J8p5Ldr-_yzkb-vyAVI"
client = genai.Client(api_key=GOOGLE_API_KEY)
model_name = "gemini-2.0-flash"
image = "pb.jpg" # @param ["Socks.jpg","Vegetables.jpg","Japanese_bento.png","Cupcakes.jpg","Origamis.jpg","Fruits.jpg","Cat.jpg","Pumpkins.jpg","Breakfast.jpg","Bookshelf.jpg", "Spill.jpg"] {"allow-input":true}

im = Image.open(image)
prompt = "Explain about that image"  # @param {type:"string"}

# Load and resize image
im = Image.open(BytesIO(open(image, "rb").read()))
im.thumbnail([1024,1024], Image.Resampling.LANCZOS)

# Run model to find bounding boxes
response = client.models.generate_content(
    model=model_name,
    contents=[prompt, im]


)

# Check output
print(response.text)