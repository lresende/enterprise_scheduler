import json
import queue
import time
from urllib.request import urlopen

import nbformat
import uuid
from threading import Thread

from enterprise_scheduler.kernel_client import KernelLauncher


class Scheduler:

    def __init__(self, default_gateway_host=None, default_kernelspec=None):
        self.default_gateway_host = default_gateway_host
        self.default_kernelspec = default_kernelspec

        self.queue = queue.PriorityQueue()
        self.executors = []

    def _executor(self):
        while True:
            if not self.queue.empty():
                task = self.queue.get()
                self._execute_task(task)
                self.queue.task_done()

    def _execute_task(self, task):

        # start notebook
        print('')
        print('Start notebook execution...')
        print('Starting kernel...')

        launcher = KernelLauncher(task['host'])
        kernel = launcher.launch(task['kernelspec'])

        time.sleep(10)

        # execute all cells
        try:
            print('reading notebook contents')
            notebook = nbformat.reads(json.dumps(task['notebook']), as_version=4)

            print('Starting cell execution')
            for cell in notebook.cells:
                print('Executing cell\n{}'.format(cell.source))
                response = kernel.execute(cell.source)
                print('Response\n{}'.format(response))
                outputs = []
                outputs.append(response)
                cell['outputs'] = outputs


        except BaseException as base:
            print('Error executing notebook cells: {}'.format(base))

        finally:
            print('Starting kernel shutdown')
            # shutdown notebook
            launcher.shutdown(kernel.kernel_id)

        print('Notebook execution done')
        print('')

    def schedule_task(self, task):
        id = uuid.uuid4()
        task['id'] = id

        if 'notebook_location' in task.keys():
            notebook_location = task['notebook_location']
            task['notebook'] = self._read_remote_notebook_content(notebook_location)

        self._validate_task(task)

        print('adding task [{}] to queue:\n {}'.format(id, str(task)))
        self.queue.put(item=task)
        return id

    def start(self):
        for i in range(1, 5):
            t = Thread(target=self._executor)
            t.daemon = True

            self.executors.append(t)

            t.start()

    def stop(self):
        self.queue.join()

        for t in self.executors:
            t._stop()

    @staticmethod
    def _validate_task(task):
        if 'host' not in task.keys():
            raise ValueError('Submitted task is missing [host] information')

        if 'kernelspec' not in task.keys():
            raise ValueError('Submitted task is missing [kernelspec] information')

        if 'notebook_location' not in task.keys() and 'notebook' not in task.keys():
            raise ValueError('Submitted task is missing notebook information (either notebook_location or notebook)')


    @staticmethod
    def _read_remote_notebook_content(notebook_location):
        try:
            notebook_content = urlopen(notebook_location).read().decode()
            return notebook_content
        except BaseException as base:
            raise Exception('Error reading notebook source "{}": {}'.format(notebook_location, base))

#
# host = 'lresende-elyra:8888'
# kernelspec = 'spark_scala_yarn_cluster'
# notebook_location = 'http://home.apache.org/~lresende/notebooks/notebook-brunel.ipynb'
# priority = 0
#
# scheduler = Scheduler()
# scheduler.schedule(host, kernelspec, notebook_location, priority)
# scheduler.start()
#
# time.sleep(30 * 60)
