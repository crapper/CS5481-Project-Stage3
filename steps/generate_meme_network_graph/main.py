import threading
import time
import logging
import networkx as nx
from ipysigma import Sigma
from typing import Dict, List
import os
import sys
import pathlib

from core.data_storage import (
    DataCategory,
    read_category_links_grid,
    read_category_set,
    read_connection_grid,
    read_data_grid,
)


MAGIC_NUM_1 = 2000
MAGIC_NUM_2 = 40
MAGIC_NUM_3 = 4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("memes_processor.log"))


def log_prefix():
    return f"[{time.strftime('%H:%M:%S', time.localtime(time.time()))}]"


# Read data
logger.info(f"{log_prefix()} Reading data")
posts = read_data_grid("../../results/9gag-memes-intern-meme-category-7k.bin")
meme_connections_grid = read_connection_grid("../../results/9gag-memes-connections.bin")
categories_links_grid = read_category_links_grid("../../results/9gag-memes-category-links.bin")
categories_set_raw = read_category_set("../../results/9gag-memes-category-set.bin")

# sort categories by category.count
logger.info(f"{log_prefix()} Initializing")
categories_sorted: List[DataCategory] = sorted(
    list(categories_set_raw.categories), key=lambda x: x.count.value, reverse=True
)

# top 30 categories, except for the first 2 (which are "meme" and "humor")
categories_top_30: List[DataCategory] = categories_sorted[2:32]

logger.info(f"{log_prefix()} Initializing categories to posts")

categories_to_posts: Dict[int, List[int]] = {}
i = 0
for links in categories_links_grid.category_links:
    if len(links.linked_categories) > MAGIC_NUM_1:
        continue

    for category_id in links.linked_categories:
        if category_id.value not in categories_to_posts:
            categories_to_posts[category_id.value] = []
        categories_to_posts[category_id.value].append(
            i
        )  # i is the index of the post, matches the index of the post in the posts array
    i += 1

logger.info(f"{log_prefix()} Initializing connections")
connections_by_ids: Dict[int, List[int]] = {}
for connection in meme_connections_grid.connections:
    if connection.from_id.value not in connections_by_ids:
        connections_by_ids[connection.from_id.value] = []
    connections_by_ids[connection.from_id.value].append(connection.to_id.value)

# Create graph
logger.info(f"{log_prefix()} Creating graph")
DG = nx.Graph()
attributes = {}


def get_post_categories(post_index: int) -> List[str]:
    return [
        categories_sorted[category_id.value].name.value
        for category_id in categories_links_grid.category_links[post_index].linked_categories
    ]


for category in categories_top_30:
    DG.add_node(category.name.value)

    post_indexes = (
        categories_to_posts[category.uid.value] if category.uid.value in categories_to_posts else []
    )[:MAGIC_NUM_2]
    for post_index in post_indexes:
        post = posts.posts[post_index]
        DG.add_edge(category.name.value, post.title.value)
        attributes[post.title.value] = {
            "categories": ", ".join(get_post_categories(post_index)),
            "post_id": post.id.value,
        }

    logger.info(f"{log_prefix()} Added {len(post_indexes)} posts to category {category.name.value}")

# Dict[post_index, int], init with zero
connection_counters: Dict[int, int] = {}
for post_index in range(len(posts.posts)):
    connection_counters[post_index] = 0
for post_index in range(len(posts.posts)):
    from_post = posts.posts[post_index]
    conns = connections_by_ids[post_index] if post_index in connections_by_ids else []

    for conn in conns:
        if connection_counters[post_index] > MAGIC_NUM_3:
            break

        if connection_counters[conn] > MAGIC_NUM_3:
            continue

        to_post = posts.posts[conn]
        DG.add_edge(from_post.title.value, to_post.title.value)

        connection_counters[post_index] += 1
        connection_counters[conn] += 1

nx.set_node_attributes(DG, attributes)

Sigma(DG, node_color="tag", node_label_size=DG.degree, node_size=DG.degree)

current_folder = pathlib.Path(__file__).parent
progressive_html = current_folder / "output.html"

Sigma.write_html(
    DG,
    progressive_html,
    default_edge_type="curve",
    default_node_label_size=16,
    fullscreen=True,
    # label_rendered_size_threshold=30,
    max_categorical_colors=30,
    node_border_color_from="node",
    node_color="louvain",
    node_metrics=["louvain"],
    node_size_range=(3, 20),
    node_size=DG.degree,
)

logger.info(f"{log_prefix()} Done!")
