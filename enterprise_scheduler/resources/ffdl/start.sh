#!/usr/bin/env bash

set -e

pip install --upgrade pip
pip install --upgrade ipykernel
pip install --upgrade jupyter_enterprise_gateway-2.0.0.dev0-py2.py3-none-any.whl

jupyter enterprisegateway --ip=0.0.0.0 --port=8888 --NotebookApp.allow_remote_access=True & echo $! > enterprise_gateway.pid

./run_notebook.py

pkill -F enterprise_gateway.pid
