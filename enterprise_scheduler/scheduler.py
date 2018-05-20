import queue
import uuid
from threading import Thread
from urllib.request import urlopen

from enterprise_scheduler.executor import JupyterExecutor, FfDLExecutor


class Scheduler:

    def __init__(self, default_gateway_host=None, default_kernelspec=None, number_of_threads=5):
        self.default_gateway_host = default_gateway_host
        self.default_kernelspec = default_kernelspec
        self.number_of_threads = number_of_threads

        self.executors = {}
        self.executors[JupyterExecutor.TYPE] = JupyterExecutor()
        self.executors[FfDLExecutor.TYPE] = FfDLExecutor()

        self.queue = queue.PriorityQueue()
        self.executor_threads = []
        self.running = False

    def _executor(self):
        while self.running:
            if not self.queue.empty():
                task = self.queue.get()
                self._execute_task(task)
                self.queue.task_done()

    def _execute_task(self, task):
        executor_type = task['executor']
        executor = self.executors[executor_type]
        executor.execute_task(task)

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
        self.running = True
        for i in range(1, self.number_of_threads):
            t = Thread(target=self._executor)
            t.daemon = True

            self.executor_threads.append(t)

            t.start()

    def stop(self):
        #self.queue.join()
        self.running = False

        for t in self.executor_threads:
            t.join()

    @staticmethod
    def _validate_task(task):
        if 'executor' not in task.keys():
            raise ValueError('Submitted task is missing [executor] information')

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
