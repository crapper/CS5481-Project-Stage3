import threading
import time
import logging
import pandas as pd
import os
import requests
import sys
from queue import Queue

from PIL import Image
from core.data_storage import DataPost, DataString, append_post, read_data_grid_ids
from lmdeploy import pipeline, TurbomindEngineConfig

num_workers = 1
worker_id = 0
if len(sys.argv) != 3:
    print("Usage: python main.py <num_workers> <worker_id>")
    sys.exit(1)
else:
    num_workers = int(sys.argv[1])
    worker_id = int(sys.argv[2])


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


def log_prefix():
    return f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}][Worker {worker_id}]"



logger.info(f"{log_prefix()} Reading tsv file...")
stage1_df = read_tsv("../../results/9gag-memes-dataset-stage1-10k.tsv")

logger.info(f"{log_prefix()} Checking if data grid exists...")
if os.path.exists("9gag-memes-intern-meme-category.bin"):
    data_ids = read_data_grid_ids("9gag-memes-intern-meme-category.bin")
else:
    data_ids = []

logger.info(f"{log_prefix()} Initializing model...")
queue_size = 10

model = "OpenGVLab/InternVL2-8B"
pipe = pipeline(model, backend_config=TurbomindEngineConfig(session_len=8192))


class ImagePost:
    def __init__(self, id: str, title: str, image: Image, upvotes: str, comments: str):
        self.id = id
        self.title = title
        self.image = image
        self.upvotes = upvotes
        self.comments = comments


class Producer:
    def __init__(self, df: pd.DataFrame, q: Queue):
        self.df = df
        self.q = q

    def produce(self):
        total = len(self.df)
        for index, row in self.df.iterrows():
            if index % num_workers != worker_id:
                continue

            while self.q.full():
                time.sleep(1)

            id = row["id"]
            image_url = row["image_url"]
            if id in data_ids:
                logger.info(
                    f"{log_prefix()} Skipping {id} because it is already processed ({index} of {total})"
                )
            elif image_url == "<video-content>":
                logger.info(
                    f"{log_prefix()} Skipping {id} because it is a video ({index} of {total})"
                )
            else:
                try:
                    image = Image.open(requests.get(image_url, stream=True).raw)
                    title = row["title"]
                    upvotes = row["upvotes"]
                    comments = row["comments"]
                    self.q.put(ImagePost(id, title, image, upvotes, comments))

                    logger.info(f"{log_prefix()} Fetched {id} image post ({index} of {total})")
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"{log_prefix()} Error reading image {image_url}: {e}")

        logger.info(f"{log_prefix()} Producer finished")


class Consumer:
    def __init__(self, q: Queue):
        self.q = q

    def consume(self):
        j = 0
        while True:
            while self.q.empty():
                time.sleep(1)

            try:
                start_time = time.time()
                logger.info(f"{log_prefix()} Processing {j}th post")

                post: ImagePost = self.q.get()
                prompt = f"Tag the image with categories, tag can be more than one, not too many, separated by commas"
                response = pipe((prompt, post.image))

                meaning = safe_string(response.text)

                append_post(
                    "9gag-memes-intern-meme-category.bin",
                    DataPost(
                        DataString(post.id),
                        DataString(post.title),
                        DataString(meaning),
                        DataString(post.upvotes),
                        DataString(post.comments),
                    ),
                )

                logger.info(
                    f"{log_prefix()} Processed {post.id} in {time.time() - start_time:.2f} seconds"
                )
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"{log_prefix()} Error processing post: {e}")

            j += 1

        logger.info(f"{log_prefix()} Consumer finished")


image_queue = Queue(queue_size)

producer = Producer(stage1_df, image_queue)
consumer = Consumer(image_queue)

# separate threads
producer_thread = threading.Thread(target=producer.produce)
consumer_thread = threading.Thread(target=consumer.consume)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

logger.info(f"{log_prefix()} All threads finished")


