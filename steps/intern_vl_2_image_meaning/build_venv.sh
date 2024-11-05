python -m venv venv
source ./venv/bin/activate
pip list
pip install --upgrade pip
pip install --editable ../../src
pip install lmdeploy
pip install timm
pip install pandas
pip install pillow
pip install requests

pip list
