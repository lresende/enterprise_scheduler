#!/usr/bin/env bash

set -e
set -x

pip install --upgrade pip
pip install --upgrade ipykernel
pip install --upgrade papermill

echo "Available Jupyter kernels..."
jupyter kernelspec list

echo "Configuring env..."
source ./env.sh

./run_notebook.py
