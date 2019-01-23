#!/usr/bin/env bash

set -e

pip install --upgrade pip
pip install --upgrade ipykernel
pip install --upgrade websocket-client
pip install --pre --upgrade jupyter_enterprise_gateway
pip install --upgrade yarn-api-client

echo "Available Jupyter kernels..."
jupyter kernelspec list

jupyter enterprisegateway --ip=0.0.0.0 --port=8888 --NotebookApp.allow_remote_access=True & echo $! > enterprise_gateway.pid

./run_notebook.py

pkill -F enterprise_gateway.pid
