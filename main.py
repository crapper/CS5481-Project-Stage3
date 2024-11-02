import os

os.environ["HF_TOKEN"] = "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"

import time
import pandas as pd
import requests
import logging

from PIL import Image
from typing import List, Set
from transformers import AutoProcessor, AutoModelForPreTraining
from data_storage import DataPost, DataString, append_post, read_data_grid_ids
from transformers.models.mllama.processing_mllama import MllamaProcessor
from transformers.models.mllama.modeling_mllama import MllamaForConditionalGeneration

processor: MllamaProcessor = AutoProcessor.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit"
)
model: MllamaForConditionalGeneration = AutoModelForPreTraining.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("memes_processor.log"))


def read_tsv(tsv_file_path: str) -> pd.DataFrame:
    with open(tsv_file_path, "r") as file:
        return pd.read_csv(
            file,
            delimiter="\t",
            header=None,
            names=["id", "title", "image_url", "upvotes", "comments"],
        )


stage1_df = read_tsv("9gag-memes-dataset-stage1-10k.tsv")


def safe_string(value: str) -> str:
    """
    Decode the string by removing the last byte until it is valid.
    """
    str_bytes = value.encode("utf-8")
    while len(str_bytes) > 0:
        try:
            return str_bytes.decode("utf-8")
        except UnicodeDecodeError:
            str_bytes = str_bytes[:-1]
    return ""

if os.path.exists("9gag-memes-dataset-stage3.bin"):
    data_ids = read_data_grid_ids("9gag-memes-dataset-stage3.bin")
else:
    data_ids = []

j = 0
for index, row in stage1_df.iterrows():
    start_time = time.time()
    logger.info(f"[{time.strftime('%H:%M:%S', time.localtime(start_time))}] Processing {j}th post")

    id = row["id"]
    title = row["title"]
    image_url = row["image_url"]
    upvotes = row["upvotes"]
    comments = row["comments"]
    
    if id in data_ids:
        logger.info(f"Skipping {id} because it is already processed")
    elif image_url == "<video-content>":
        logger.info(f"Skipping {id} because it is a video")
    else:
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
            prompt = f"<|image|><|begin_of_text|>Describe the image"
            inputs = processor(image, prompt, return_tensors="pt").to(model.device)
            output = model.generate(**inputs, max_new_tokens=200)

            description = safe_string(processor.decode(output[0]).replace(prompt, ""))

            append_post(
                "9gag-memes-dataset-stage3.bin",
                DataPost(
                    DataString(id),
                    DataString(title),
                    DataString(description),
                    DataString(upvotes),
                    DataString(comments),
                ),
            )

            logger.info(f"Processed {id} in {time.time() - start_time} seconds")
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(e)

    j += 1

# print(stage1_df.head())

# append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id1"), DataString("title1"), DataString("image_url1"), DataInt(100), DataInt(20)))
# append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id2"), DataString("title2"), DataString("image_url2"), DataInt(101), DataInt(21)))

# data_grid = read_data_grid("9gag-memes-dataset-stage3.bin")
# for post in data_grid.posts:
#     print(post)

