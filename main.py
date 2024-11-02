import os

os.environ["HF_TOKEN"] = "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"

import time
import pandas as pd
import requests

from PIL import Image
from typing import List, Set
from transformers import AutoProcessor, AutoModelForPreTraining
from data_storage import (
    DataInt,
    DataPost,
    DataString,
    append_post,
    read_data_grid,
    read_data_grid_ids,
)

processor = AutoProcessor.from_pretrained("unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit")
model = AutoModelForPreTraining.from_pretrained("unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit")


def read_tsv(tsv_file_path: str) -> pd.DataFrame:
    with open(tsv_file_path, "r") as file:
        return pd.read_csv(
            file,
            delimiter="\t",
            header=None,
            names=["id", "title", "image_url", "upvotes", "comments"],
        )


stage1_df = read_tsv("9gag-memes-dataset-stage1-10k.tsv")


j = 0
for index, row in stage1_df.iterrows():
    start_time = time.time()
    print(f"[{time.strftime('%H:%M:%S', time.localtime(start_time))}] Processing {j}th post")

    id = row["id"]
    title = row["title"]
    image_url = row["image_url"]
    upvotes = int(row["upvotes"])
    comments = int(row["comments"])

    if image_url == "<video-content>":
        print(f"Skipping {id} because it is a video")
    else:
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
            prompt = f"<|image|><|begin_of_text|>Describe the image"
            inputs = processor(image, prompt, return_tensors="pt").to(model.device)
            output = model.generate(**inputs, max_new_tokens=200)

            description = processor.decode(output[0]).replace(prompt, "")

            append_post(
                "9gag-memes-dataset-stage3.bin",
                DataPost(
                    DataString(id),
                    DataString(title),
                    DataString(description),
                    DataInt(upvotes),
                    DataInt(comments),
                ),
            )

            print(f"Processed {id} in {time.time() - start_time} seconds")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

    j += 1

# print(stage1_df.head())

# append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id1"), DataString("title1"), DataString("image_url1"), DataInt(100), DataInt(20)))
# append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id2"), DataString("title2"), DataString("image_url2"), DataInt(101), DataInt(21)))

# data_grid = read_data_grid("9gag-memes-dataset-stage3.bin")
# for post in data_grid.posts:
#     print(post)

# data_ids = read_data_grid_ids("9gag-memes-dataset-stage3.bin")
# print(data_ids)
