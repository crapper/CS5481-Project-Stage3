## Prerequisites

```sh
cd ./steps/llama3_2_describe_the_image

# Setup venv
./build_venv.sh

# IMPORTANT: Deactivate after you are done
deactivate
```

## Run

```sh
cd ./steps/llama3_2_describe_the_image

source ./venv/bin/activate

# Run the script
python ./main.py

# Read the last 10 posts
python ./tail.py
```

## Run In Screen

```sh
cd ./steps/llama3_2_describe_the_image

# See available GPUs
nvidia-smi

# IMPORTANT: Set the CUDA_VISIBLE_DEVICES environment variable to the GPU you want to use
screen -dmS memes_processor bash -c 'export CUDA_VISIBLE_DEVICES="1" && source ./venv/bin/activate && python main.py'

# check if screen is running
screen -ls

# attach to screen
screen -r memes_processor

# detach from screen
Ctrl + A + D
```
