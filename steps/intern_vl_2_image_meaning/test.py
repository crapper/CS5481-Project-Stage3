import sys
import pandas as pd
import time
import requests

from lmdeploy import pipeline, TurbomindEngineConfig
from PIL import Image

if len(sys.argv) != 2:
    print("Usage: python test.py <post_id>")
    sys.exit(1)

post_id = sys.argv[1]


def read_tsv(tsv_file_path: str) -> pd.DataFrame:
    with open(tsv_file_path, "r") as file:
        return pd.read_csv(
            file,
            delimiter="\t",
            header=None,
            names=["id", "title", "image_url", "upvotes", "comments"],
        )


stage1_df = read_tsv("../../results/9gag-memes-dataset-stage1-10k.tsv")

start_time = time.time()

print(f"Initializing model")

model = "OpenGVLab/InternVL2-8B"
pipe = pipeline(model, backend_config=TurbomindEngineConfig(session_len=8192))

print(f"Reading image for post {post_id}")

post = stage1_df.loc[stage1_df["id"] == post_id]
title = post["title"].values[0]
image_url = post["image_url"].values[0]
if not image_url:
    print(f"Image URL not found for post {post_id}")
    sys.exit(1)

image = Image.open(requests.get(image_url, stream=True).raw)

print(f"Generating response for post {post_id}")
prompt = f"what is the meaning of this meme? post title: {title}"
response = pipe((prompt, image))

print(f"Post {post_id}: {response.text}")

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Time taken: {elapsed_time:.2f} seconds")
