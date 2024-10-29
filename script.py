from typing import List, Set
import pandas as pd

from data_storage import DataInt, DataPost, DataString, append_post, read_data_grid, read_data_grid_ids

def read_tsv(tsv_file_path: str) -> pd.DataFrame:
    with open(tsv_file_path, "r") as file:
        return pd.read_csv(file, delimiter="\t", header=None, names=["id", "title", "image_url", "upvotes", "comments"])

stage1_df = read_tsv("9gag-memes-dataset-stage1.tsv")
print(stage1_df.head())

append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id1"), DataString("title1"), DataString("image_url1"), DataInt(100), DataInt(20)))
append_post("9gag-memes-dataset-stage3.bin", DataPost(DataString("id2"), DataString("title2"), DataString("image_url2"), DataInt(101), DataInt(21)))

data_grid = read_data_grid("9gag-memes-dataset-stage3.bin")
for post in data_grid.posts:
    print(post)

data_ids = read_data_grid_ids("9gag-memes-dataset-stage3.bin")
print(data_ids)
