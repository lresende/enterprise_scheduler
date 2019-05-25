#!/usr/bin/env python
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
import time
import nbformat

import papermill as pm


print('')
print('Start notebook execution...')

try:
    input = 'notebook.ipynb'
    output = os.environ['RESULT_DIR'] + '/result.ipynb'

    pm.execute_notebook(
        input,
        output
    )

    time.sleep(10)

    with open(output, 'r') as file:
        print(file.read())

except BaseException as base:
    print('Error executing notebook cells: {}'.format(base))

print('Notebook execution done')
print('')
