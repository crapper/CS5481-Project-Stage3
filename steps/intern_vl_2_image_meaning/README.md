## Prerequisites

```sh
cd ./steps/intern_vl_2_image_meaning

# Setup venv
./build_venv.sh

# IMPORTANT: Deactivate after you are done
deactivate
```

## Run

```sh
cd ./steps/intern_vl_2_image_meaning

source ./venv/bin/activate

# See available GPUs
nvidia-smi

# Run the script
export CUDA_VISIBLE_DEVICES="1"
python ./main.py 1 0

# Read the last 10 posts
python ./tail.py
```

## Run with multiple workers in the background

```sh
cd ./steps/llama3_2_describe_the_image

# See available GPUs
nvidia-smi

# IMPORTANT: Set the CUDA_VISIBLE_DEVICES environment variable to the GPU you want to use
screen -dmS memes_processor1 bash -c 'export CUDA_VISIBLE_DEVICES="1" && source ./venv/bin/activate && python main.py 2 0'

screen -dmS memes_processor2 bash -c 'export CUDA_VISIBLE_DEVICES="2" && source ./venv/bin/activate && python main.py 2 1'

# check if screen is running
screen -ls

# attach to screen
screen -r memes_processor1

# detach from screen
Ctrl + A + D
```
