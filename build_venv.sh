python -m venv venv
source venv/bin/activate
pip list
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install --upgrade git+https://github.com/huggingface/transformers
pip install pillow
pip install requests
pip install bitsandbytes
pip install 'accelerate>=0.26.0'

pip list

# pip install 