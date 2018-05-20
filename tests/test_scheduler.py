#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `enterprise_scheduler` package."""

import asyncio
import os
import json
import unittest
import time
from pprint import pprint

from enterprise_scheduler.scheduler import Scheduler
from enterprise_scheduler.util import fix_asyncio_event_loop_policy

RESOURCES = os.path.join(os.path.dirname(__file__), 'resources')

DEFAULT_GATEWAY = "lresende-elyra:8888"
DEFAULT_KERNELSPEC = "python2"


class TestEnterpriseScheduler(unittest.TestCase):
    """Tests for `enterprise_scheduler` package."""
    scheduler = None

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, if any."""
        fix_asyncio_event_loop_policy(asyncio)

        cls.scheduler = Scheduler()
        cls.scheduler.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures, if any."""
        cls.scheduler.stop()
        cls.scheduler = None

    def test_execute_jupyter_task_with_embedded_notebook(self):
        notebook = self._read_notebook('simple.ipynb')

        task = {}
        task['executor'] = 'jupyter'
        task['host'] = DEFAULT_GATEWAY
        task['kernelspec'] = DEFAULT_KERNELSPEC
        task['notebook'] = notebook

        TestEnterpriseScheduler.scheduler.schedule_task(task)

    def test_execute_jupyter_task_with_remote_notebook(self):
        task = {}
        task['executor'] = 'jupyter'
        task['host'] = DEFAULT_GATEWAY
        task['kernelspec'] = DEFAULT_KERNELSPEC
        task['notebook_location'] = 'http://home.apache.org/~lresende/notebooks/notebook-brunel.ipynb'

        TestEnterpriseScheduler.scheduler.schedule_task(task)

    def test_execute_ffdl_task_with_embedded_notebook(self):
        notebook = self._read_notebook('simple.ipynb')

        task = {}
        task['executor'] = 'ffdl'
        task['host'] = DEFAULT_GATEWAY
        task['kernelspec'] = DEFAULT_KERNELSPEC
        task['notebook'] = notebook

        TestEnterpriseScheduler.scheduler.schedule_task(task)


    def _read_notebook(self, filename):
        filename = os.path.join(RESOURCES, filename)
        with open(filename, 'r') as f:
           return json.load(f)
