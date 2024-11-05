import sys
import pandas as pd
import matplotlib.pyplot as plt

def read_tsv(tsv_file_path: str) -> pd.DataFrame:
    with open(tsv_file_path, "r") as file:
        df = pd.read_csv(
            file,
            delimiter="\t",
            header=0,  # First row is header
        )
        # Convert columns to numeric
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'])
        df['upvotes'] = pd.to_numeric(df['upvotes'])
        return df

if len(sys.argv) != 2:
    print("Usage: python main.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

df = read_tsv(file_path)

# Assign each sentiment score to the closest group
# bins = [-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1]
# df['sentiment_group'] = pd.cut(df['sentiment_score'], bins=bins, labels=[-0.9, -0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7, 0.9])

bins = [-1, -0.05, 0.05, 1]
labels = ['Negative', 'Neutral', 'Positive']
df['sentiment_group'] = pd.cut(df['sentiment_score'], bins=bins, labels=labels)

# Count the number of records in each sentiment group
sentiment_counts = df['sentiment_group'].value_counts().sort_index()

# Create the bar chart
plt.figure(figsize=(10, 6))
sentiment_counts.plot(kind='bar')

# Add labels and title
plt.title('Distribution of Records by Sentiment Score')
plt.xlabel('Sentiment Score')
plt.ylabel('Count')
plt.xticks(rotation=45)

# Show the chart
plt.tight_layout()
plt.savefig("bar-chart-sentiment_counts.png", dpi=300)

plt.clf()

# Calculate the average upvotes for each sentiment group
sentiment_avg_upvotes = df.groupby('sentiment_group')['upvotes'].mean().sort_index()

# Create the bar chart
plt.figure(figsize=(10, 6))
sentiment_avg_upvotes.plot(kind='bar')

# Add labels and title
plt.title('Average Upvotes by Sentiment Group')
plt.xlabel('Sentiment Group')
plt.ylabel('Average Upvotes')

# Set the x-axis tick labels
plt.xticks(range(len(sentiment_avg_upvotes)), sentiment_avg_upvotes.index)

# Show the chart
plt.tight_layout()
plt.savefig("bar-chart-avg-upvotes.png", dpi=300)