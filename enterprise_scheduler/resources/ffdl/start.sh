#!/usr/bin/env bash

set -e

pip install --upgrade pip
pip install --upgrade ipykernel
pip install --upgrade papermill

echo "Available Jupyter kernels..."
jupyter kernelspec list

./run_notebook.py
