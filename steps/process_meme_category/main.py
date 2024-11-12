# imports
from core.data_storage import (
    DataCategory,
    DataCategoryLinks,
    DataInt,
    DataString,
    append_category_links,
    read_data_grid,
    write_category_set,
)
from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import nltk
import string
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("memes_processor.log"))


def log_prefix():
    return f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}]"


# Specific exclusions and transformations
specific_exclusions = ["#tags#", "text"]

# Download stopwords and lemmatizer
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger_eng")
nltk.download("wordnet")
lemmatizer = WordNetLemmatizer()

logger.info(f"{log_prefix()} Reading data")
posts = read_data_grid("../../results/9gag-memes-intern-meme-category-7k.bin")

# 9gag-memes-category-links.bin
# 9gag-memes-category-set.bin

# { category_name: { uid: int, count: int } }
known_categories = {}

last_category_index = 0


# Reference: https://www.cnblogs.com/jclian91/p/9898511.html
def get_wordnet_pos(tag: str):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV
    else:
        return None


def lemmatize_word(word: str):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    wn_tag = get_wordnet_pos(tag)
    if wn_tag is None:
        return word
    return lemmatizer.lemmatize(word, wn_tag)


def count_category(category_name: str) -> int:
    global last_category_index
    if category_name not in known_categories:
        target = {"uid": last_category_index, "count": 0}
        known_categories[category_name] = target
        last_category_index += 1
    else:
        target = known_categories[category_name]
    target["count"] += 1

    return target["uid"]


logger.info(f"{log_prefix()} Processing posts")
i = 0
for post in posts.posts:
    post_category_raw_string = post.content

    lines = post_category_raw_string.lower().split("\n")

    linked_categories = []
    if ":" in lines[0]:
        #  this is a special case where the model outputs the category name in point form
        category_names = [t[2:] for t in lines[2:]]  # remove "- "
    else:
        category_names = lines[0].split(", ")

    category_names = set([name.strip().strip(string.punctuation) for name in category_names])
    category_names = set(
        [
            lemmatize_word(name)
            for name in category_names
            if name != ""
            and name not in specific_exclusions
            and name not in stopwords.words("english")
        ]
    )

    category_ids: list[DataInt] = []
    for category_name in category_names:
        category_ids.append(DataInt(count_category(category_name)))

    append_category_links("9gag-memes-category-links.bin", DataCategoryLinks(category_ids))

    logger.info(f"{log_prefix()} Processed post {post.id} ({i})")
    i += 1

logger.info(f"{log_prefix()} Writing category set")
write_category_set(
    "9gag-memes-category-set.bin",
    [
        DataCategory(DataInt(item["uid"]), DataString(name), DataInt(item["count"]))
        for name, item in known_categories.items()
    ],
)

logger.info(f"{log_prefix()} Done")
