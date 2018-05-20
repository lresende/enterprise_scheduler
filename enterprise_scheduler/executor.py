import os
import json
import tempfile
import time
import uuid
import zipfile

import nbformat

from subprocess import Popen, PIPE

from enterprise_scheduler.kernel_client import KernelLauncher
from enterprise_scheduler.util import zip_directory


class Executor:
    def __init__(self, default_gateway_host=None, default_kernelspec=None):
        self.default_gateway_host = default_gateway_host
        self.default_kernelspec = default_kernelspec


class JupyterExecutor(Executor):
    TYPE = "jupyter"

    def execute_task(self, task):
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


class FfDLExecutor(Executor):
    TYPE = "ffdl"

    def __init__(self):
        self.workdir = os.path.join(tempfile.gettempdir(), str(FfDLExecutor.TYPE))
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

        self.runtimedir = os.path.join(os.path.dirname(__file__), 'resources/ffdl')
        print(self.runtimedir)


    def execute_task(self, task):
        self._create_ffdl_zip(task)


        #docker run
        # -it
        # --volume /Users/lresende/opensource/jupyter/jupyter_enterprise_scheduler/enterprise_scheduler/resources/ffdl/:/tmp/scheduler
        # tensorflow/tensorflow
        # /bin/bash -x /tmp/scheduler/start.sh

        command = 'docker run --volume {}:/tmp/scheduler tensorflow/tensorflow /bin/bash -x /tmp/scheduler/start.sh'.format(self.runtimedir)

        print('>>> {}'.format(command))

        p = Popen([command ], stdout=PIPE, stderr=PIPE, shell=True, cwd=self.runtimedir)
        p.wait()
        #print(p.stdout.read())
        #print(p.stderr.read())

        #pass


    def _create_ffdl_zip(self, task):
        unique_id = 'ffdl-' + str(uuid.uuid4())[:8]
        task_directory = os.path.join(self.workdir, unique_id)
        os.makedirs(task_directory)

        self._write_file(task_directory, "notebook.ipynb", task['notebook'])

        zip_file = os.path.join(self.workdir, '{}.zip'.format(unique_id))
        print('>>> {}'.format(zip_file))
        print('>>> {}'.format(task_directory))
        zip_directory(zip_file, task_directory)


    @staticmethod
    def _write_file(directory, filename, contents):
        filename = os.path.join(directory, filename)
        with open(filename, 'w') as f:
            f.write(str(contents))
