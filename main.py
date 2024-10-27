import os
import requests
from PIL import Image
import time
os.environ["HF_TOKEN"] = "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"

from transformers import AutoProcessor, AutoModelForPreTraining

processor = AutoProcessor.from_pretrained("unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit")
model = AutoModelForPreTraining.from_pretrained("unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit")

t = time.time()
url = "https://img-9gag-fun.9cache.com/photo/aPAYX5Q_460s.jpg"
image = Image.open(requests.get(url, stream=True).raw)
#Return JSON format of {object:array, body_lang:array, emotion:array, tone:array, text:string}
prompt = "<|image|><|begin_of_text|>Describe the image"
inputs = processor(image, prompt, return_tensors="pt").to(model.device)

output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0]).replace(prompt, ""))
print("Time used: ", time.time() - t)