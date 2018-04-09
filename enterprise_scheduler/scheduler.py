
"""
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
"""

import queue
from threading import Thread
import time
from urllib.request import urlopen

import nbformat
from nbconvert import PDFExporter
from traitlets.config import Config

from kernel_client import KernelLauncher, Kernel


class Scheduler:

    def __init__(self):
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
        print('Start notebook execution')
        print('Starting kernel')
        print(task)
        launcher = KernelLauncher(task['host'])
        kernel = launcher.launch(task['kernelspec'])

        # execute all cells
        notebook_content = urlopen(task['notebook_location']).read().decode()
        notebook = nbformat.reads(notebook_content, as_version=4)

        time.sleep(10)

        print('Starting cell execution')
        for cell in notebook.cells:
            print('Executing cell\n{}'.format(cell.source))
            response = kernel.execute(cell.source)
            print('Response\n{}'.format(response))

        print('Starting kernel shutdown')
        # shutdown notebook
        launcher.shutdown(kernel.kernel_id)

        print('Notebook execution done')
        print('')

    def schedule_task(self, task):
        print('adding task to queue: ' + str(task))
        self.queue.put(item=task)

    def schedule(self, host, kernelspec, notebook_location, priority):
        task = {}
        task['host'] = host
        task['kernelspec'] =  kernelspec
        task['notebook_location'] = notebook_location
        task['priority'] = priority

        self.schedule_task(task)

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
