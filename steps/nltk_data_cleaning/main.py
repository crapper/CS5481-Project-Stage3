import logging
import sys
from core.data_storage import read_data_grid
import nltk
from nltk.corpus import stopwords
from nltk.corpus import words

if len(sys.argv) != 2:
    print("Usage: python main.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]
file_name = file_path.split("/")[-1].split(".")[0]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("memes_processor.log"))

nltk.download("punkt_tab")
nltk.download("words")
nltk.download("stopwords")

logger.info("Initializing nltk...")
custom_words = set(["image", "caption", "man", "text"])
words = set(words.words())
stop_words = set(stopwords.words("english"))

logger.info("Reading data...")
data_grid = read_data_grid(file_path)

logger.info("Processing posts...")

i = 0
for post in data_grid.posts:
    tokens: list[str] = nltk.word_tokenize(post.description.value.lower())

    word_counts = {}
    filtered_tokens = []
    for word in tokens:
        if word in words and word not in stop_words and word not in custom_words:
            word_counts[word] = word_counts.get(word, 0) + 1
            if word_counts[word] == 10:
                logger.info(f"Removing {word} because it appears 10 times")
            elif word_counts[word] < 10:
                filtered_tokens.append(word)

    with open(f"./{file_name}-words-cleaned.txt", "a") as file:
        file.write(" ".join(filtered_tokens) + "\n")

    logger.info(f"Processed {post.id} ({i+1}/{len(data_grid.posts)})")

    i += 1
