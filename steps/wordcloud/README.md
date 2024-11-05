## Prerequisites

```sh
cd ./steps/wordcloud

# Setup venv
./build_venv.sh

# IMPORTANT: Deactivate after you are done
deactivate
```

## Run

```sh
cd ./steps/wordcloud

source ./venv/bin/activate

python ./main.py ../../results/9gag-memes-dataset-stage3-7k-words-cleaned.txt
```
