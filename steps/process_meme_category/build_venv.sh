python -m venv venv
source ./venv/bin/activate
pip list
python -m pip install --upgrade pip
pip install --editable ../../src
pip install pandas
pip install pillow
pip install requests
pip install nltk

pip list
