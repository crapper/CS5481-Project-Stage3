The OCR results obtained from the CWKSC's repositroy.

## Prerequisites

```sh
cd ./steps/intern_vl_2_ocr

# Setup venv
./build_venv.sh

# IMPORTANT: Deactivate after you are done
deactivate
```

## Run

```sh
cd ./steps/intern_vl_2_ocr

source ./venv/bin/activate

# Run the script
python ./from_txt_to_bin.py

# Read the last 10 posts
python ./tail.py
```