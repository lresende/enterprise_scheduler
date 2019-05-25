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
import os
import json
import tempfile
import time
import yaml
import requests
import nbformat
import shlex
import pkg_resources

from ffdl.client import Config
from ffdl.client import FfDLClient
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
        self.runtimedir = pkg_resources.resource_filename('enterprise_scheduler', 'resources/ffdl')
        print('Resources dir: {} '.format(self.runtimedir))

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

        client = FfDLClient(config)

        result = client.post('/models', **files)

        if 'model_id' in result:
            print("Training URL : http://{}:{}/#/trainings/{}/show"
                  .format(urlparse(config.api_endpoint).netloc.split(":")[0],
                          ffdl_ui_port,
                          result['model_id']))
        elif 'message' in result:
            # Catches server-side FFDL errors returned with a 200 code
            print("FFDL Job Submission Request Failed: {}".format(
                result['message']))
        elif 'error' in result:
            # Catches HTTP errors returned by the FFDL server
            print("FFDL Job Submission Request Failed: {}".format(
                result['error']))
        else:
            # Cases with no error but the submission was unsuccessful
            print("FFDL Job Submission Failed")

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
                    container=task['cos_bucket_in']
                ),
                training_results= dict(
                    container=task['cos_bucket_out']
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

        self._create_env_sh(task, task_directory)

        copyfile(os.path.join(self.runtimedir, "start.sh"),
                 os.path.join(task_directory, "start.sh"))

        copyfile(os.path.join(self.runtimedir, "run_notebook.py"),
                 os.path.join(task_directory, "run_notebook.py"))

        zip_file = os.path.join(self.workdir, '{}.zip'.format(unique_id))
        # print('>>> {}'.format(zip_file))
        # print('>>> {}'.format(task_directory))
        zip_directory(zip_file, task_directory)

        return zip_file

    def _create_env_sh(self, task, task_directory):
        lines = ["#!/usr/bin/env bash\n"]
        for key, value in task['env'].items():
            lines.append("export {}={}".format(shlex.quote(key),
                                               shlex.quote(value)))

        contents = "\n".join(lines) + "\n"
        self._write_file(task_directory, "env.sh", contents)

    @staticmethod
    def _write_file(directory, filename, contents):
        filename = os.path.join(directory, filename)
        with open(filename, 'w') as f:
            f.write(str(contents))
