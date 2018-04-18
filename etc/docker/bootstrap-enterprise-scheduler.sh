#!/bin/bash

server_name=${EGS_SCHEDULER_HOST:-"0.0.0.0:5000"}
gateway_host=${EGS_GATEWAY_HOST:-"localhost:8888"}
kernelspec=${EGS_KERNELSPEC:-"python_tf_kubernetes"}

# Flask host and port can be overridden using SERVER_NAME
export SERVER_NAME=${server_name}

enterprise_scheduler --gateway_host ${gateway_host} --kernelspec ${kernelspec}
exit $?
