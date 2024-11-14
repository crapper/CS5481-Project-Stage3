# read links and category set
from core.data_storage import read_category_links_grid, read_category_set


links = read_category_links_grid("9gag-memes-category-links.bin")
categories = read_category_set("9gag-memes-category-set.bin")

# print the number of links and categories
print(f"Number of categories: {len(categories.categories)}")

# print the last 10 links
print("Last 10 links:")
for links in (links.category_links)[-10:]:
    print(", ".join([str(num.value) for num in links.linked_categories]))

print("\nTop 50 categories:")
categories_sorted = sorted(list(categories.categories), key=lambda x: x.count.value, reverse=True)
for category in categories_sorted[:50]:
    print(f"{category.uid.value}: {category.name.value}")
