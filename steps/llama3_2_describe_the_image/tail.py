import os

from core.data_storage import DataGrid, DataPost


def read_data_grid(file_path: str) -> DataGrid:
    with open(file_path, "rb") as file:
        data = file.read()
        posts = []
        i = 0
        while data:
            try:
                post = DataPost.deserialize(data)
                posts.append(post)
                data = data[post.serialize_len :]
            except Exception as e:
                serialized_len = int.from_bytes(data[0:4], "big")
                print(f"Failed to deserialize post {i}, skipping {serialized_len} bytes: {e}")
                data = data[4 + serialized_len :]
            finally:
                i += 1

        print(f"Read {len(posts)} posts")
        return DataGrid(posts)


def display_last_posts():
    try:
        # Read the data grid from the binary file
        data_grid = read_data_grid("9gag-memes-llama-description.bin")

        # Get all posts
        posts = data_grid.posts

        # Display last 10 posts
        print("\nLast 10 posts:")
        print("-" * 50)
        for post in posts[-10:]:
            print(f"ID: {post.id.value}")
            print(f"Title: {post.title.value}")
            print(f"Description: {post.description.value}")
            print(f"Upvotes: {post.upvotes.value}")
            print(f"Comments: {post.comments.value}")
            print("-" * 50)

    except FileNotFoundError:
        print("Error: Data file not found")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    display_last_posts()
