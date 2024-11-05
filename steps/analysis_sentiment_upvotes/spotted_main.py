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

# Create figure with specific size
plt.figure(figsize=(12, 8))

# Create scatter plot with formatting
plt.scatter(df['sentiment_score'], df['upvotes'], 
           alpha=0.2,
           s=20,
           rasterized=True,
           color='#1f77b4')  # Set specific color

# Set axis limits with padding
x_margin = (df['sentiment_score'].max() - df['sentiment_score'].min()) * 0.05
y_margin = (df['upvotes'].max() - df['upvotes'].min()) * 0.05

plt.xlim(df['sentiment_score'].min() - x_margin, 
         df['sentiment_score'].max() + x_margin)
plt.ylim(df['upvotes'].min() - y_margin, 
         df['upvotes'].max() + y_margin)

# Add titles and labels with better formatting
plt.title('Scatter Plot of Sentiment Score vs. Upvotes', pad=20, fontsize=12)
plt.xlabel('Sentiment Score', labelpad=10, fontsize=10)
plt.ylabel('Upvotes', labelpad=10, fontsize=10)

# Customize grid
plt.grid(True, linestyle='--', alpha=0.3)

# Adjust layout
plt.tight_layout()

# Save plot
plt.savefig("scatter-plot.png", 
            bbox_inches='tight',
            dpi=300,
            facecolor='white')