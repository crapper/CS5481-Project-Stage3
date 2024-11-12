python -m venv venv
source ./venv/bin/activate
pip list
python -m pip install --upgrade pip
pip install --editable ../../src

pip list
