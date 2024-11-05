import logging
import os
import pandas as pd
from core.data_storage import DataPost, DataString, append_post


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


stage1_df = read_tsv("../../results/9gag-memes-dataset-stage1-10k.tsv")

posts: list[DataPost] = []

for index, row in stage1_df.iterrows():
    post_id = row["id"]
    if not os.path.exists(f"text_ocr_intern_vl_2/{post_id}.txt"):
        logger.info(f"Post {post_id} not found")
        continue
    try:
        with open(f"text_ocr_intern_vl_2/{post_id}.txt", "r") as f:
            ocr_result = f.read()
            title = row["title"]
            upvotes = row["upvotes"]
            comments = row["comments"]
            append_post(
                "9gag-memes-intern-ocr-7k.bin",
                DataPost(
                    DataString(post_id),
                    DataString(title),
                    DataString(ocr_result),
                    DataString(upvotes),
                    DataString(comments),
                ),
            )
            logger.info(f"Processed post {post_id}")
    except Exception as e:
        logger.error(f"Error reading post {post_id}: {e}")
        continue
