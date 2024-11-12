import struct
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


class DataFloat:
    def __init__(self, value: float):
        self.value = value

    def serialize(self) -> bytes:
        return struct.pack("f", self.value)

    @property
    def serialize_len(self) -> int:
        return 4

    def deserialize(data: bytes) -> "DataFloat":
        return DataFloat(struct.unpack("f", data)[0])

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


class DataCategoryLinks:
    def __init__(self, linked_categories: List[DataInt]):
        self.linked_categories = linked_categories

    def serialize(self) -> bytes:
        payload = b"".join(category.serialize() for category in self.linked_categories)
        return len(payload).to_bytes(4, "big") + payload

    @property
    def serialize_len(self) -> int:
        return 4 + sum(category.serialize_len for category in self.linked_categories)

    def deserialize(data: bytes) -> "DataCategoryLinks":
        length = int.from_bytes(data[:4], "big")
        payload = data[4 : 4 + length]
        linked_categories = []
        while payload:
            linked_categories.append(DataInt.deserialize(payload))
            payload = payload[4:]
        return DataCategoryLinks(linked_categories)

    def __str__(self) -> str:
        return f"DataCategoryLinks({self.linked_categories})"


class DataCategoryLinksGrid:
    def __init__(self, category_links: List[DataCategoryLinks]):
        self.category_links = category_links

    def serialize(self) -> bytes:
        return b"".join(category_link.serialize() for category_link in self.category_links)

    @property
    def serialize_len(self) -> int:
        return sum(category_link.serialize_len for category_link in self.category_links)

    def deserialize(data: bytes) -> "DataCategoryLinksGrid":
        category_links = []
        while data:
            category_link = DataCategoryLinks.deserialize(data)
            category_links.append(category_link)
            data = data[category_link.serialize_len :]
        return DataCategoryLinksGrid(category_links)


class DataCategory:
    def __init__(self, uid: DataInt, name: DataString, count: DataInt):
        self.uid = uid
        self.name = name
        self.count = count

    def serialize(self) -> bytes:
        return self.uid.serialize() + self.name.serialize() + self.count.serialize()

    @property
    def serialize_len(self) -> int:
        return self.uid.serialize_len + self.name.serialize_len + self.count.serialize_len

    def deserialize(data: bytes) -> "DataCategory":
        uid = DataInt.deserialize(data)
        payload = data[uid.serialize_len :]
        name = DataString.deserialize(payload)
        payload = payload[name.serialize_len :]
        count = DataInt.deserialize(payload)
        return DataCategory(uid, name, count)

    def __str__(self) -> str:
        return f"DataCategory(uid={self.uid}, name={self.name}, count={self.count})"


class DataCategorySet:
    def __init__(self, categories: Set[DataCategory]):
        self.categories = categories

    def serialize(self) -> bytes:
        return b"".join(category.serialize() for category in self.categories)

    @property
    def serialize_len(self) -> int:
        return sum(category.serialize_len for category in self.categories)

    def deserialize(data: bytes) -> "DataCategorySet":
        categories = set()
        while data:
            category = DataCategory.deserialize(data)
            categories.add(category)
            data = data[category.serialize_len :]
        return DataCategorySet(categories)


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


class DataConnection:
    def __init__(self, from_id: DataInt, to_id: DataInt, value: DataFloat):
        self.from_id = from_id
        self.to_id = to_id
        self.value = value

    def serialize(self) -> bytes:
        return self.from_id.serialize() + self.to_id.serialize() + self.value.serialize()

    @property
    def serialize_len(self) -> int:
        return self.from_id.serialize_len + self.to_id.serialize_len + self.value.serialize_len

    def deserialize(data: bytes) -> "DataConnection":
        from_id = DataInt.deserialize(data)
        payload = data[from_id.serialize_len :]
        to_id = DataInt.deserialize(payload)
        payload = payload[to_id.serialize_len :]
        value = DataFloat.deserialize(payload)
        return DataConnection(from_id, to_id, value)

    def __str__(self) -> str:
        return f"DataConnection(from_id={self.from_id}, to_id={self.to_id}, value={self.value})"


class DataConnectionGrid:
    def __init__(self, connections: List[DataConnection]):
        self.connections = connections

    def serialize(self) -> bytes:
        return b"".join(connection.serialize() for connection in self.connections)

    def deserialize(data: bytes) -> "DataConnectionGrid":
        connections = []
        while data:
            connection = DataConnection.deserialize(data)
            connections.append(connection)
            data = data[connection.serialize_len :]
        return DataConnectionGrid(connections)


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


def read_data_post_by_id(file_path: str, post_id: str) -> DataPost:
    with open(file_path, "rb") as file:
        data = file.read()
        while data:
            # read length of the data
            length = int.from_bytes(data[:4], "big")
            # deserialize the first string
            id = DataString.deserialize(data[4:])
            if id.value == post_id:
                return DataPost.deserialize(data)
            data = data[4:]
            data = data[length:]
        raise ValueError(f"Post {post_id} not found")


def append_category_links(file_path: str, category_links: DataCategoryLinks):
    append_to_file(file_path, category_links.serialize())


def read_category_links_grid(file_path: str) -> DataCategoryLinksGrid:
    with open(file_path, "rb") as file:
        data = file.read()
        return DataCategoryLinksGrid.deserialize(data)


def write_category_set(file_path: str, category_set: List[DataCategory]):
    c = DataCategorySet(category_set)
    with open(file_path, "wb") as file:
        file.write(c.serialize())


def read_category_set(file_path: str) -> DataCategorySet:
    with open(file_path, "rb") as file:
        data = file.read()
        return DataCategorySet.deserialize(data)


def append_connections(file_path: str, connections: List[DataConnection]):
    append_to_file(file_path, b"".join(connection.serialize() for connection in connections))


def read_connection_grid(file_path: str) -> DataConnectionGrid:
    with open(file_path, "rb") as file:
        data = file.read()
        return DataConnectionGrid.deserialize(data)


# # test serialize and deserialize
# integer = DataInt(100)
# serialized = integer.serialize()
# # print(serialized)
# deserialized = DataInt.deserialize(serialized)
# print(deserialized)

# float = DataFloat(100.1)
# serialized = float.serialize()
# # print(serialized)
# deserialized = DataFloat.deserialize(serialized)
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
