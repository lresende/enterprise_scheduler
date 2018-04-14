#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `enterprise_scheduler` package."""


import unittest
from click.testing import CliRunner

from enterprise_scheduler import enterprise_scheduler
from enterprise_scheduler import scheduler_application


class TestEnterprise_scheduler(unittest.TestCase):
    """Tests for `enterprise_scheduler` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(scheduler_application.main)
        assert result.exit_code == 0
        assert 'enterprise_scheduler.cli.main' in result.output
        help_result = runner.invoke(scheduler_application.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
