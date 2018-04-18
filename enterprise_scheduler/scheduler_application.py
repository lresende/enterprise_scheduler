# -*- coding: utf-8 -*-

"""Jupyter Enterprise Scheduler - Schedule Notebook execution."""
import os
import sys

import asyncio
import click
from flask import Flask
from flask_restful import Api

from enterprise_scheduler.scheduler_resource import SchedulerResource
from enterprise_scheduler.util import fix_asyncio_event_loop_policy

server_name = os.getenv('SERVER_NAME','127.0.0.1:5000')

@click.command()
@click.option('--gateway_host', default='lresende-elyra:8888', help='Jupyter Enterprise Gateway host information')
@click.option('--kernelspec', default='python2', help='Jupyter Notebook kernelspec to use while executing notebook')
def main(gateway_host, kernelspec):
    """Jupyter Enterprise Scheduler - Schedule Notebook execution."""
    click.echo('Starting Scheduler at {} using Gateway at {} with default kernelspec {}'.format(server_name, gateway_host, kernelspec))
    click.echo('Add new tasks via post commands to http://{}/scheduler/tasks '.format(server_name))

    fix_asyncio_event_loop_policy(asyncio)

    app = Flask('Notebook Scheduler')
    api = Api(app)

    api.add_resource(SchedulerResource, '/scheduler/tasks',
                     resource_class_kwargs={ 'default_gateway_host': gateway_host, 'default_kernelspec': kernelspec })

    print('Add new tasks via http://{}/scheduler/tasks '.format(server_name))

    server_parts = server_name.split(':')

    app.run(host=server_parts[0], port=int(server_parts[1]), debug=True, use_reloader=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
