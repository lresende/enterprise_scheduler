import os
import json
import tempfile
import time
import yaml
import requests
import nbformat

from ffdl.client import Config, FfDLClient
from shutil import copyfile
from requests.auth import HTTPBasicAuth
from enterprise_gateway.client.gateway_client import GatewayClient
from enterprise_scheduler.util import zip_directory
from urllib.parse import urlparse


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

        launcher = GatewayClient(task['endpoint'])
        kernel = launcher.start_kernel(task['kernelspec'])

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
            launcher.shutdown_kernel(kernel)

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
        config = Config(api_endpoint=task['endpoint'],
                        user=task['user'],
                        password="temporary",
                        user_info=task['userinfo'])

        ffdl_zip = self._create_ffdl_zip(task)
        ffdl_manifest = self._create_manifest(task)
        ffdl_ui_port = "32263"  ## FFDL UI hosting can vary

        files = {'model_definition': ffdl_zip,
                 'manifest': ffdl_manifest }

        try:
            client = FfDLClient(config)

            result = client.post('/models', **files)

            if 'models' not in result:
                print("FFDL Job Submission Request Failed: {}".format(result['message']))
            elif result['models']:
                print("Training URL : http://{}:{}/#/trainings/{}/show"
                      .format(urlparse(config.api_endpoint).netloc.split(":")[0],
                              ffdl_ui_port,
                              result['model_id']))
            else:
                print("FFDL Job Submission Failed")
        except requests.exceptions.Timeout:
            print("FFDL Job Submission Request Timed Out....")
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects were detected during job submission")
        except requests.exceptions.ConnectionError:
            print("Connection Error: Could not connect to {}".format(task['endpoint']))
        except requests.exceptions.HTTPError as http_err:
            print("HTTP Error - {} ".format(http_err))
        except requests.exceptions.RequestException as err:
            print(err)

    def _create_manifest(self, task):
        file_name = 'manifest-' + str(task['id'])[:8]
        file_location = self.workdir + '/' + file_name + ".yml"

        task_description = 'Train Jupyter Notebook'
        if 'notebook_name' in task:
            task_description += ': ' + task['notebook_name']

        manifest_dict = dict(
            name=file_name,
            description=task_description,
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

        if 'dependencies' in task:
            for dependency in task['dependencies']:
                self._write_file(task_directory, dependency, task['dependencies'][dependency])

        copyfile(os.path.join(self.runtimedir, "start.sh"),
                 os.path.join(task_directory, "start.sh"))

        copyfile(os.path.join(self.runtimedir, "run_notebook.py"),
                 os.path.join(task_directory, "run_notebook.py"))

        zip_file = os.path.join(self.workdir, '{}.zip'.format(unique_id))
        # print('>>> {}'.format(zip_file))
        # print('>>> {}'.format(task_directory))
        zip_directory(zip_file, task_directory)

        return zip_file

    @staticmethod
    def _write_file(directory, filename, contents):
        filename = os.path.join(directory, filename)
        with open(filename, 'w') as f:
            f.write(str(contents))
