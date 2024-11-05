## Prerequisites

```sh
cd ./steps/analysis_sentiment_upvotes

# Setup venv
./build_venv.sh

# IMPORTANT: Deactivate after you are done
deactivate
```

## Run

```sh
cd ./steps/analysis_sentiment_upvotes

source ./venv/bin/activate

python ./spotted_main.py ../../results/9gag-memes-llama-description-7k-sentiment.tsv

python ./bar_main.py ../../results/9gag-memes-llama-description-7k-sentiment.tsv
```
