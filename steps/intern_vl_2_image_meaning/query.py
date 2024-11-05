import sys
import pandas as pd

from core.data_storage import DataPost, DataString, read_data_post_by_id

if len(sys.argv) != 2:
    print("Usage: python query.py <post_id>")
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

post = read_data_post_by_id("9gag-memes-intern-image-meaning.bin", post_id)
title = post.title
post_url = f"https://9gag.com/gag/{post_id[10:]}"

print(f"Post {post_id}: {title}")
print(f"Post URL: {post_url}")
print(f"Image URL: {post.content}")
print(f"Upvotes: {post.upvotes}")
print(f"Comments: {post.comments}")
