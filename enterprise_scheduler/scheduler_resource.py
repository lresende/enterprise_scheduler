# -*- coding: utf-8 -*-
#
# Copyright 2018-2019 Luciano Resende
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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

        if 'endpoint' not in task.keys():
            task['endpoint'] = self.default_gateway_host

        if 'kernelspec' not in task.keys():
            task['kernelspec'] = self.default_kernelspec

        scheduler.schedule_task(task)

        return 'submitted', 201


