#!/usr/bin/env python

import time
import nbformat

from enterprise_scheduler.kernel_client import KernelLauncher

print('')
print('Waiting Enterprise Gateway to load...')

time.sleep(10)

print('')
print('Start notebook execution...')

try:
    # start notebook
    print('reading notebook contents')
    notebook = None
    with open('notebook.ipynb', 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)

    if not notebook:
        raise RuntimeError('Error reading notebook file')

    print('Starting kernel...')

    launcher = KernelLauncher('localhost:8888')
    kernel = launcher.launch(notebook['metadata']['kernelspec']['name'])

    time.sleep(10)

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
