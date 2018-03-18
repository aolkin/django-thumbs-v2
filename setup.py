#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os

README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name='django-thumbs-v2',
    version='0.4.1',
    description='The easiest way to create thumbnails for your images with Django. Works with any storage backend.',
    author='Ravi Raja Merugu',
    author_email='rrmerugu@gmail.com',
    long_description=open(README, 'r').read(),
    packages=['django_thumbs'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url='https://github.com/rrmerugu/django-thumbs',
)
