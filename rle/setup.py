#! /usr/bin/env python3

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from Cython.Build import cythonize


setup(
    ext_modules = cythonize("crle.pyx", annotate=True),
    zip_safe=False,
)
