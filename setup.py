__docformat__ = "restructuredtext en"
"""
:summary: Setup script for rundeckrun

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
from setuptools import setup, find_packages
from rundeck import VERSION

setup(
    name='rundeckrun',
    license='http://creativecommons.org/licenses/by-sa/3.0/',
    version=VERSION,
    packages=find_packages(),
    description='Rundeck API Python client',
    long_description='A lightweight wrapper written in Python to interact' + \
        ' with the Rundeck API.',
    url='https://github.com/marklap/rundeckrun',
    author='rundeckrun@mindmind.com',
    author_email='rundeckrun@mindmind.com',
    maintainer='rundeckrun@mindmind.com',
    maintainer_email='rundeckrun@mindmind.com',
    install_requires=['requests>=1.2.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
