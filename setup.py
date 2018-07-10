#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'click>=6.0',
    'bumpversion>=0.5.3',
    'wheel>=0.30.0',
    'watchdog>=0.8.3',
    'flake8>=3.5.0',
    'tox>=2.9.1',
    'coverage>=4.5.1',
    'Sphinx>=1.7.1',
    'twine>=1.10.0',
    'nbconvert>=5.3.1',
    'requests >= 2.8, < 3.0',
    'flask-restful>=0.3.6'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Luciano Resende",
    author_email='lresende@apache.org',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        'console_scripts': [
            'enterprise_scheduler=enterprise_scheduler.scheduler_application:main',
        ],
    },
    install_requires=requirements,
    license="Apache license",
    long_description=readme,
    include_package_data=True,
    keywords='enterprise_scheduler',
    name='enterprise_scheduler',
    packages=find_packages(include=['enterprise_scheduler']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lresende/enterprise_scheduler',
    version='0.1.0.dev1',
    zip_safe=False,
)
