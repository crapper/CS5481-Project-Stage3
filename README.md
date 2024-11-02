## Prerequisites

```sh
wget https://github.com/25077667/standalone-python/releases/download/release-2024-04-29/release-3.10-x86_64.tar.gz

# unzip
tar -xvf release-3.10-x86_64.tar.gz

# setup venv
./build_venv.sh

# Chmod
chmod 777 ./venv/bin/activate

# Activate Env
. ./venv/bin/activate 

# exit env when activate
deactivate
```

## Run

```sh
screen -dmS memes_processor bash -c 'cd /home/bsft21/chlum4/CS5481-Project-Stage3 && source ./venv/bin/activate && python main.py > memes_processor.log 2>&1'

# check if screen is running
screen -ls

# attach to screen
screen -r memes_processor

# detach from screen
Ctrl + A + D
```
