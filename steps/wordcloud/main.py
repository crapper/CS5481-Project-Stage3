import sys
from wordcloud import WordCloud

if len(sys.argv) != 2:
    print("Usage: python main.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

wordcloud = WordCloud(width=1024, height=1024, background_color="white").generate(text)

file_name = file_path.split("/")[-1].split(".")[0]

wordcloud.to_file(f"{file_name}.png")
