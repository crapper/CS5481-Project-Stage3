./opt/python/bin/python -m venv venv
source venv/bin/activate
pip list
pip install --upgrade pip
pip install --upgrade git+https://github.com/huggingface/transformers
pip install requests
# pip install triton
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu113
pip install pillow

pip list

# pip install 