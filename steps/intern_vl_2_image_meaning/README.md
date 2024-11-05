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
python ./main.py

# Read the last 10 posts
python ./tail.py
```
