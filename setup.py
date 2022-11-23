import os.path
import platform

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON_AVAILABLE = False
else:
    CYTHON_AVAILABLE = True


class BuildExtWithCompilerArgs(build_ext):
    def build_extensions(self):
        for ext in self.extensions:
            if self.compiler.compiler_type == 'msvc':
                ext.extra_compile_args = ['/std:c++17']
            else:
                ext.extra_compile_args = ['-std=c++17']
        build_ext.build_extensions(self)


root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), 'rb') as readme:
    long_description = readme.read().decode('utf-8')

system = platform.system()


if os.getenv('BUILD_WITH_CYTHON') and not CYTHON_AVAILABLE:
    print(
        'BUILD_WITH_CYTHON environment variable is set, but cython'
        ' is not available. Falling back to pre-cythonized version if'
        ' available.'
    )

if os.getenv('BUILD_WITH_CYTHON') and CYTHON_AVAILABLE:
    macros = []
    compiler_directives = {
        'embedsignature': True
    }

    if os.getenv('BUILD_FOR_DEBUG'):
        # Enable line tracing, which also enables support for coverage
        # reporting.
        macros = [
            ('CYTHON_TRACE', 1),
            ('CYTHON_TRACE_NOGIL', 1)
        ]
        compiler_directives['linetrace'] = True

    force = bool(os.getenv('FORCE_REBUILD'))

    extensions = cythonize([
        Extension(
            'cstrstrdict',
            [
                'strstrdict/cstrstrdict.pyx'
            ],
            define_macros=macros,
        )
    ], compiler_directives=compiler_directives, force=force)
else:
    extensions = [
        Extension(
            'cstrstrdict',
            [
                'strstrdict/cstrstrdict.cpp',
            ],
            language='c++'
        )
    ]

setup(
    name='strstrdict',
    packages=find_packages(),
    version='0.0.1',
    description='lower memory alternative to string-to-string dict',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Edgars Irmejs',
    author_email='edgars.irmejs@gmail.com',
    url='https://github.com/edgarsi/strstrdict',
    keywords=[
        'dict', 'str', 'cache', 'memory', 'overhead', 'string', 'hash',
        'drop-in', 'alternative', 'replacement', 'dictionary'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
    ],
    python_requires='>3.5',
    extras_require={
        # Dependencies for package release.
        'release': [
            'sphinx',
            'bumpversion'
        ],
        # Dependencies for running tests.
        'test': [
            'pytest',
            'flake8',
        ],
        # Dependencies for running benchmarks.
        'benchmark': [
            'memory_profiler',
            'tabulate',
            'sqlitedict',
            'gmpy2',
        ],
    },
    cmdclass={ 'build_ext': BuildExtWithCompilerArgs},
    ext_modules=extensions,
    package_data={
        'strstrdict': [
            'strstrdict/*.pxd',
            '__init__.py',
            'py.typed'
        ]
    }
)
