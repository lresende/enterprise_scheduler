import os
import json
import tempfile
import time
import uuid
import yaml
import zipfile

import nbformat

from subprocess import Popen, PIPE
from shutil import copyfile

from enterprise_scheduler.kernel_client import KernelLauncher
from enterprise_scheduler.util import zip_directory


class Executor:
    """Base executor class for :
        - Jupyter
        - FFDL (Fabric for Deep Learning)
        - DLAAS (Deep Learning as a Service)"""
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
    """FFDL Executor Supports :
        - TensorFlow
        - Keras
        - Caffe
        - Caffe 2
        - PyTorch"""
    TYPE = "ffdl"

    def __init__(self):
        self.workdir = os.path.join(tempfile.gettempdir(), str(FfDLExecutor.TYPE))
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

        rootdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.runtimedir = os.path.join(rootdir, 'resources/ffdl')
        print(self.runtimedir)

    def execute_task(self, task):

        ffdl_endpoint = task['host']
        ffdl_authorization = task['user']
        ffdl_userinfo = task['userinfo']
        ffdl_zip = self._create_ffdl_zip(task)
        ffdl_manifest = self._create_manifest(task)

        command = 'curl -X POST "' + ffdl_endpoint + '" ' \
                  '-H "accept: application/json" ' \
                  '-H "Authorization: ' + ffdl_authorization + '" ' \
                  '-H "X-Watson-Userinfo: ' + ffdl_userinfo + '" ' \
                  '-H "Content-Type: multipart/form-data" ' \
                  '-F "model_definition=@' + ffdl_zip + ';type=application/zip" ' \
                  '-F "manifest=@' + ffdl_manifest + '"'

        try:
            p = Popen([command ], stdout=PIPE, stderr=PIPE, shell=True, cwd=self.runtimedir)
            p.wait()
            #print(p.stdout.read())
            #print(p.stderr.read())
        finally:
            if(p.stderr):
                p.stderr.close()
            if(p.stdout):
                p.stdout.close()

    def _create_manifest(self, task):
        file_name = 'manifest-' + str(task['id'])[:8]
        file_location = self.workdir + '/' + file_name + ".yml"

        manifest_dict = dict(
            name=file_name,
            description='Train Jupyter Notebook model in FfDL',
            version="1.0",
            gpus=task['gpus'],
            cpus=task['cpus'],
            memory=task['memory'],
            learners=1,
            data_stores= [dict(
                id='sl-internal-os',
                type='mount_cos',
                training_data= dict(
                    container='tf_training_data'
                ),
                training_results= dict(
                    container='tf_trained_model'
                ),
                connection= dict(
                    auth_url=task['cos_endpoint'],
                    user_name=task['cos_user'],
                    password=task['cos_password']
                )
            )],
            framework= dict(
                name=task['framework'],
                version='1.5.0-py3',
                command='./start.sh'    ## Run the start script for EG and kernel
            #),
            #evaluation_metrics=dict(
            #    type=''
            )
        )

        with open(file_location, 'w') as outfile:
            yaml.dump(manifest_dict, outfile, default_flow_style=False)

        return file_location

    def _create_ffdl_zip(self, task):
        unique_id = 'ffdl-' + str(task['id'])[:8]
        task_directory = os.path.join(self.workdir, unique_id)
        os.makedirs(task_directory)

        self._write_file(task_directory, "notebook.ipynb", json.dumps(task['notebook']))

        copyfile(os.path.join(self.runtimedir, "start.sh"),
                 os.path.join(task_directory, "start.sh"))

        copyfile(os.path.join(self.runtimedir, "run_notebook.py"),
                 os.path.join(task_directory, "run_notebook.py"))

        zip_file = os.path.join(self.workdir, '{}.zip'.format(unique_id))
        #print('>>> {}'.format(zip_file))
        #print('>>> {}'.format(task_directory))
        zip_directory(zip_file, task_directory)

        return zip_file


    @staticmethod
    def _write_file(directory, filename, contents):
        filename = os.path.join(directory, filename)
        with open(filename, 'w') as f:
            f.write(str(contents))
