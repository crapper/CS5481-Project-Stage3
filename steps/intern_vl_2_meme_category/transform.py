# Transform file "step0_id_to_category_text.json" from CWKSC's repositry to binary file

import json
import pathlib
import pandas as pd
import logging
import time
from core.data_storage import DataPost, DataString, append_post

current_folder = pathlib.Path(__file__).parent
original_file = current_folder / "step0_id_to_category_text.json"
destination_file = current_folder / "9gag-memes-intern-meme-category.bin"


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

def log_prefix():
    return f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}]"

logger.info(f"{log_prefix()} Reading tsv file...")
stage1_df = read_tsv("../../results/9gag-memes-dataset-stage1-10k.tsv")

logger.info(f"{log_prefix()} Reading json file...")
all_memes = json.load(open(original_file, "r"))

logger.info(f"{log_prefix()} Transforming json to binary file...")
# for all memes in tsv
for index, row in stage1_df.iterrows():
    try:
        id = row["id"]
        image_url = row["image_url"]
        if image_url == "<video-content>":
            logger.info(f"{log_prefix()} Skipping {id} because it is a video")
            continue
        if id not in all_memes:
            logger.warning(f"{log_prefix()} Meme {id} not found in json file")
            continue
        title = str(row["title"]) # in some cases title is float
        upvotes = row["upvotes"]
        comments = row["comments"]
        categories = all_memes[id]
        
        append_post(
            destination_file,
            DataPost(
                DataString(id),
                DataString(str(title)),
                DataString(categories),
                DataString(upvotes),
                DataString(comments),
            ),
        )
        
        logger.info(f"{log_prefix()} Processed {id}")
    except Exception as e:
        logger.error(f"{log_prefix()} Error processing {id}: {e}")

logger.info(f"{log_prefix()} Done")
