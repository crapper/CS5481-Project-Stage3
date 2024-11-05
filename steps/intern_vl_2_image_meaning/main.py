import pathlib
import threading
import time
import logging
import pandas as pd
import os
import requests
from queue import Queue

from PIL import Image
from core.data_storage import DataPost, DataString, append_post, read_data_grid_ids
from lmdeploy import pipeline, TurbomindEngineConfig
from lmdeploy.vl import load_image


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


if os.path.exists("9gag-memes-intern-image-meaning.bin"):
    data_ids = read_data_grid_ids("9gag-memes-intern-image-meaning.bin")
else:
    data_ids = []


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
        j = 0
        for index, row in self.df.iterrows():
            while self.q.full():
                time.sleep(1)

            id = row["id"]
            image_url = row["image_url"]
            if id in data_ids:
                logger.info(f"Skipping {id} because it is already processed")
            elif image_url == "<video-content>":
                logger.info(f"Skipping {id} because it is a video")
            else:
                try:
                    image = Image.open(requests.get(image_url, stream=True).raw)
                    title = row["title"]
                    upvotes = row["upvotes"]
                    comments = row["comments"]
                    self.q.put(ImagePost(id, title, image, upvotes, comments))

                    logger.info(
                        f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}] Fetched {j}th image post"
                    )
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error reading image {image_url}: {e}")
                    continue

        logger.info("Producer finished")


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
                logger.info(
                    f"[{time.strftime('%H:%M:%S', time.localtime(start_time))}] Processing {j}th post"
                )

                post: ImagePost = self.q.get()
                prompt = "what is the meaning of this image"
                response = pipe((prompt, post.image))

                meaning = safe_string(response.text)

                append_post(
                    "9gag-memes-intern-image-meaning.bin",
                    DataPost(
                        DataString(post.id),
                        DataString(post.title),
                        DataString(meaning),
                        DataString(post.upvotes),
                        DataString(post.comments),
                    ),
                )

                logger.info(f"Processed {post.id} in {time.time() - start_time:.2f} seconds")
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(e)

            j += 1

        logger.info("Consumer finished")


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

logger.info("All threads finished")

# current_folder = pathlib.Path(__file__).parent
# images_folder = current_folder / "images"

# start_time = time.time()
# for image_path in images_folder.iterdir():
#     path = image_path.resolve().as_posix()
#     image = load_image(path)
#     response = pipe(("what is the meaning of this image", image))
#     print(response.text)
#     with open(f"meaning_intern_vl_2/{image_path.stem}.txt", "w") as f:
#         f.write(response.text)

# end_time = time.time()

# elapsed_time = end_time - start_time
# print(f"Time taken: {elapsed_time:.2f} seconds")

# Time taken: 8.44 seconds
