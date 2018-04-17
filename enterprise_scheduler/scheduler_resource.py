
from flask import Response, request
from flask_restful import Resource

from enterprise_scheduler.scheduler import Scheduler

scheduler = Scheduler()
scheduler.start()

class SchedulerResource(Resource):
    """
    Scheduler REST API used to submit Jupyter Notebooks for batch executions

    curl -X POST -v http://localhost:5000/scheduler/tasks -d "{\"notebook_location\":\"http://home.apache.org/~lresende/notebooks/notebook-brunel.ipynb\"}"
    """

    def __init__(self, default_gateway_host, default_kernelspec):
        self.default_gateway_host = default_gateway_host
        self.default_kernelspec = default_kernelspec

    def _html_response(self, data):
        resp = Response(data, mimetype='text/plain', headers=None)
        resp.status_code = 200
        return resp

    def post(self):
        global scheduler
        task = request.get_json(force=True)

        print(task)
        print(task.keys())

        if 'host' not in task.keys():
            task['host'] = self.default_gateway_host

        if 'kernelspec' not in task.keys():
            task['kernelspec'] = self.default_kernelspec

        scheduler.schedule_task(task)

        return 'submitted', 201


