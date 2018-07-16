#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'requests',
    'python-dateutil==2.7.3',
    'python-dotenv==0.8.2',
    'marshmallow==2.15.3'
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="MJ Berends",
    author_email='mjr.berends@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="This is an implementation oof the Active Campaign takehome exercise.",
    entry_points={
        'console_scripts': [
            'activecampaign_takehome=activecampaign_takehome.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='activecampaign_takehome',
    name='activecampaign_takehome',
    packages=find_packages(include=['activecampaign_takehome']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/approximatelylinear/activecampaign_takehome',
    version='0.1.0',
    zip_safe=False,
)
