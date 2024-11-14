import math
import logging
import time
from typing import List
from core.data_storage import (
    DataCategory,
    DataConnection,
    DataFloat,
    DataInt,
    append_connections,
    read_category_links_grid,
    read_category_set,
)


MAX_SIMILARITY_CONNECTIONS = 10


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("memes_processor.log"))


def log_prefix():
    return f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}]"


links_grid = read_category_links_grid("../../results/9gag-memes-category-links.bin")
categories_set_raw = read_category_set("../../results/9gag-memes-category-set.bin")

# sort categories by category.count
categories_sorted: List[DataCategory] = sorted(
    list(categories_set_raw.categories), key=lambda x: x.count.value, reverse=True
)

# top 30 categories
categories_top_30: List[DataCategory] = categories_sorted[2:32]

total_posts = len(links_grid.category_links)
logger.info(f"{log_prefix()} Total posts: {total_posts}")

# Calculate idf for each category
logger.info(f"{log_prefix()} Calculating idf for each category...")
idf = {}
for category in categories_top_30:
    idf[category.uid.value] = math.log(
        (total_posts + 1) / (category.count.value + 1), total_posts + 1
    )

# Sort idf by value
idf_sorted = sorted(idf.items(), key=lambda x: x[1], reverse=True)

logger.info(f"{log_prefix()} IDF sorted: {idf_sorted}")

# Top 5 categories
top_5_categories = idf_sorted[:5]
logger.info(f"{log_prefix()} Top 5 categories:")
for category in top_5_categories:
    logger.info(f"{log_prefix()} {category[0]} - {category[1]}")

# Loop links
logger.info(f"{log_prefix()} Preparing links grid...")
links_grid_int: list[set[int]] = [
    set([link.value for link in links.linked_categories]) for links in links_grid.category_links
]

for i in range(len(links_grid_int)):
    similarity = {}
    for j in range(len(links_grid_int)):
        if i == j:
            continue

        # Get the number of categories that are the same between two ids
        intersection = links_grid_int[i] & links_grid_int[j]
        if len(intersection) == 0:
            continue

        # Calculate similarity value
        similarity[j] = sum([idf[category] for category in intersection if category in idf])

    # sort similarity by value and use the first MAX_SIMILARITY_CONNECTIONS
    similarity_sorted = sorted(similarity.items(), key=lambda x: x[1], reverse=True)[
        :MAX_SIMILARITY_CONNECTIONS
    ]

    append_connections(
        "9gag-memes-connections.bin",
        [
            DataConnection(DataInt(i), DataInt(j), DataFloat(value))
            for j, value in similarity_sorted
        ],
    )
    logger.info(f"{log_prefix()} Processed post {i}th with {len(similarity_sorted)} connections")

logger.info(f"{log_prefix()} Done!")
