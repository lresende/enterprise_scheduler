#!/usr/bin/env bash
pip install ipykernel
pip install --upgrade jupyter_enterprise_gateway
pip install --upgrade enterprise_scheduler

jupyter enterprisegateway --ip=0.0.0.0 --port=8888 &

./run_notebook.py

kill $(ps aux | grep jupyter-enterprisegateway | awk '{print $2}')
