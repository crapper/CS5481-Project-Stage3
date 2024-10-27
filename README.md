Install standalone python 3.10

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