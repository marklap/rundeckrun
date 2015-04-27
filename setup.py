__docformat__ = "restructuredtext en"
"""
:summary: Setup script for rundeckrun

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
"""
import os
from setuptools import setup, find_packages
from rundeck import VERSION

project = 'rundeckrun'
install_requires = ['requests>=1.2.0']

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'README.rst'), 'r') as fp:
    long_description = fp.read()

setup(
    name=project,
    license='http://creativecommons.org/licenses/by-sa/3.0/',
    version=VERSION,
    packages=find_packages(),
    description='Rundeck API Python client',
    long_description=long_description,
    url='https://github.com/marklap/{0}'.format(project),
    author='{0}@mindmind.com'.format(project),
    author_email='{0}@mindmind.com'.format(project),
    maintainer='{0}@mindmind.com'.format(project),
    maintainer_email='{0}@mindmind.com'.format(project),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
