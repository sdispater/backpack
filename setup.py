# -*- coding: utf-8 -*-

import os
import sys
from setuptools import find_packages
from distutils.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension
from distutils.version import StrictVersion
from distutils.errors import (CCompilerError, DistutilsExecError,
                              DistutilsPlatformError)


here = os.path.abspath(os.path.dirname(__file__))

def get_version():
    with open(os.path.join(here, 'backpack/version.py')) as f:
        variables = {}
        exec(f.read(), variables)

        version = variables.get('VERSION')
        if version:
            return version

    raise RuntimeError('No version info found.')


__version__ = get_version()

with open('%s/requirements.txt' % here) as f:
    requirements = f.readlines()


# Optional C extensions

if sys.platform == 'win32':
    build_ext_errors = (CCompilerError, DistutilsExecError,
            DistutilsPlatformError, IOError)
else:
    build_ext_errors = (CCompilerError, DistutilsExecError,
            DistutilsPlatformError)

class BuildExtFailed(Exception):
    pass

with_extensions = os.environ.get('BACKPACK_EXTENSIONS', None)

if with_extensions:
    if with_extensions.lower() == 'true':
        with_extensions = True
    elif with_extensions.lower() == 'false':
        with_extensions = False
    else:
        with_extensions = None

if hasattr(sys, 'pypy_version_info'):
    with_extensions = False

extensions = (
    ('backpack.collections._collection', ('backpack/collections/_collection.pyx',
                                          'backpack/collections/_collection.c')),
    ('backpack._utils._helpers', ('backpack/_utils/_helpers.pyx',
                                  'backpack/_utils/_helpers.c')),
)

ext_modules = None
if with_extensions is True or with_extensions is None:
    cython_min = '0.22.1'
    try:
        from Cython.Distutils import build_ext
        from Cython import __version__ as cython_ver
    except ImportError:
        cython_installed = False
    else:
        cython_installed = StrictVersion(cython_ver) >= StrictVersion(cython_min)

    ext_modules = [Extension(module, [pyx if cython_installed else c], extra_compile_args=['-Wno-unused-function'])
                   for module, (pyx, c) in extensions]


class optional_build_ext(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildExtFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except build_ext_errors:
            raise BuildExtFailed()



setup_kwargs = dict(
    name='backpack',
    license='MIT',
    version=__version__,
    description='Useful utilities for Python.',
    long_description=open('README.rst').read(),
    author='Sébastien Eustace',
    author_email='sebastien@eustace.io',
    url='https://github.com/sdispater/backpack',
    download_url='https://github.com/sdispater/backpack/archive/%s.tar.gz' % __version__,
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    tests_require=['pytest'],
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

def run_setup(ext_modules=None):
    setup_kwargs_tmp = dict(setup_kwargs)

    if ext_modules:
        setup_kwargs_tmp['ext_modules'] = ext_modules
        setup_kwargs_tmp['cmdclass'] = {'build_ext': optional_build_ext}

    setup(**setup_kwargs_tmp)


try:
    run_setup(ext_modules)
except BuildExtFailed:
    run_setup()
