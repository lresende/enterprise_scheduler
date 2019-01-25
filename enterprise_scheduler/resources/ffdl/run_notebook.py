#!/usr/bin/env python

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
