from data_storage import DataPost, DataString, append_post


post = DataPost(DataString("id1"), DataString("title"), DataString("image_url!"), DataString("100"), DataString("20"))
serialized = post.serialize()
# print(serialized)
deserialized: DataPost = DataPost.deserialize(serialized)
print(deserialized)

# append_post("test.bin", post)