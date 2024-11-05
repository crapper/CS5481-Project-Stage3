from typing import List, Set


class DataString(str):
    def __init__(self, value: str):
        self.value = value

    def serialize(self) -> bytes:
        # length of the string in bytes
        payload = self.value.encode("utf-8")
        length = len(payload)
        return length.to_bytes(4, "big") + payload

    @property
    def serialize_len(self) -> int:
        return 4 + len(self.value.encode("utf-8"))

    def deserialize(data: bytes) -> "DataString":
        length = int.from_bytes(data[0:4], "big")
        value = data[4 : 4 + length].decode("utf-8")
        return DataString(value)


class DataInt:
    def __init__(self, value: int):
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(4, "big")

    @property
    def serialize_len(self) -> int:
        return 4

    def deserialize(data: bytes) -> "DataInt":
        return DataInt(int.from_bytes(data[:4], "big"))

    def __str__(self) -> str:
        return str(self.value)


class DataPost:
    def __init__(
        self,
        id: DataString,
        title: DataString,
        content: DataString,
        upvotes: DataString,
        comments: DataString,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.upvotes = upvotes
        self.comments = comments

    def serialize(self) -> bytes:
        payload = (
            self.id.serialize()
            + self.title.serialize()
            + self.content.serialize()
            + self.upvotes.serialize()
            + self.comments.serialize()
        )
        return len(payload).to_bytes(4, "big") + payload

    @property
    def serialize_len(self) -> int:
        return (
            4
            + self.id.serialize_len
            + self.title.serialize_len
            + self.content.serialize_len
            + self.upvotes.serialize_len
            + self.comments.serialize_len
        )

    def deserialize(data: bytes) -> "DataPost":
        payload = data[4:]
        id: DataString = DataString.deserialize(payload)
        payload = payload[id.serialize_len :]
        title: DataString = DataString.deserialize(payload)
        payload = payload[title.serialize_len :]
        content: DataString = DataString.deserialize(payload)
        payload = payload[content.serialize_len :]
        upvotes: DataString = DataString.deserialize(payload)
        payload = payload[upvotes.serialize_len :]
        comments: DataString = DataString.deserialize(payload)
        return DataPost(id, title, content, upvotes, comments)

    def __str__(self) -> str:
        return f"DataPost(id={self.id}, title={self.title}, content={self.content}, upvotes={self.upvotes}, comments={self.comments})"


class DataGrid:
    def __init__(self, posts: List[DataPost]):
        self.posts = posts

    def serialize(self) -> bytes:
        return b"".join(post.serialize() for post in self.posts)

    def deserialize(data: bytes) -> "DataGrid":
        posts = []
        while data:
            post = DataPost.deserialize(data)
            posts.append(post)
            data = data[post.serialize_len :]
        return DataGrid(posts)


def append_to_file(file_path: str, data: bytes):
    with open(file_path, "ab") as file:
        file.write(data)


def append_post(file_path: str, post: DataPost):
    append_to_file(file_path, post.serialize())


def read_data_grid(file_path: str) -> DataGrid:
    with open(file_path, "rb") as file:
        data = file.read()
        return DataGrid.deserialize(data)


def read_data_grid_ids(file_path: str) -> Set[str]:
    ids = set()
    with open(file_path, "rb") as file:
        data = file.read()
        while data:
            # read length of the data
            length = int.from_bytes(data[:4], "big")
            # read the data
            data = data[4:]
            # deserialize the first string
            id = DataString.deserialize(data)
            ids.add(id.value)
            data = data[length:]
        return ids


# # test serialize and deserialize
# integer = DataInt(100)
# serialized = integer.serialize()
# # print(serialized)
# deserialized = DataInt.deserialize(serialized)
# print(deserialized)

# string = DataString("hello")
# serialized = string.serialize()
# # print(serialized)
# deserialized = DataString.deserialize(serialized)
# print(deserialized)

# post = DataPost(DataString("id1"), DataString("title"), DataString("image_url!"), DataInt(100), DataInt(20))
# serialized = post.serialize()
# # print(serialized)
# deserialized = DataPost.deserialize(serialized)
# print(deserialized)
