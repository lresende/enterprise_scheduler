# -*- coding: utf-8 -*-

"""Jupyter Enterprise Scheduler - Schedule Notebook execution."""
import sys

import asyncio
import click
from flask import Flask
from flask_restful import Api

from enterprise_scheduler.scheduler_resource import SchedulerResource
from enterprise_scheduler.util import fix_asyncio_event_loop_policy

@click.command()
@click.option('--gateway_host', default='lresende-elyra:8888', help='Jupyter Enterprise Gateway host information')
@click.option('--kernelspec', default='python2', help='Jupyter Notebook kernelspec to use while executing notebook')
def main(gateway_host, kernelspec):
    """Jupyter Enterprise Scheduler - Schedule Notebook execution."""
    click.echo('Starting Scheduler at {} using {} default kernelspec'.format(gateway_host, kernelspec))
    click.echo('Add new tasks via post commands to http://localhost:5000/scheduler/tasks ')

    fix_asyncio_event_loop_policy(asyncio)

    app = Flask('Notebook Scheduler')
    api = Api(app)

    api.add_resource(SchedulerResource, '/scheduler/tasks',
                     resource_class_kwargs={ 'default_gateway_host': gateway_host, 'default_kernelspec': kernelspec })

    print('Add new tasks via http://localhost:5000/scheduler/tasks ')

    app.run(debug=True, use_reloader=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
