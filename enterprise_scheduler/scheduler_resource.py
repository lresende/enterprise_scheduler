
from flask import Flask, Response, request, json
from flask_restful import reqparse, abort, Api, Resource
from scheduler import Scheduler


DEFAULT_HOST = 'lresende-elyra:8888'
DEFAULT_KERNELSPEC = 'spark_scala_yarn_cluster'

scheduler = Scheduler()
scheduler.start()


class SchedulerResource(Resource):

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
            task['host'] = DEFAULT_HOST

        if 'kernelspec' not in task.keys():
            task['kernelspec'] = DEFAULT_KERNELSPEC

        if not task['notebook_location']:
            raise ValueError('Submitted task is missing [notebook_location] information')

        scheduler.schedule_task(task)

        return 'submitted', 201


app = Flask('Notebook Scheduler')
api = Api(app)

api.add_resource(SchedulerResource, '/scheduler/tasks')

print('Add new tasks via http://localhost:5000/scheduler/tasks ')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


"""
curl http://localhost:5000/scheduler/tasks -d "{\"notebook_location\":\"http://home.apache.org/~lresende/notebooks/notebook-brunel.ipynb\"}" -X POST -v
"""
