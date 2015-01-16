from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

version_ns = {}
with open('contentful/cda/version.py') as f:
    exec(f.read(), version_ns)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    default_args = ['test/']

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        args = self.pytest_args
        if isinstance(args, str):
            args = args.split()
        errno = pytest.main(self.default_args + args)
        sys.exit(errno)

deps = [
    'enum34==1.0.4',
    'requests==2.4.3',
    'six==1.8.0',
    'python-dateutil==2.3'
]

test_deps = [
    'mock==1.0.1',
    'vcrpy==1.1.3',
    'pytest==2.6.4'
]

with open('README.rst') as f:
    readme = f.read()

setup(
    name='contentful.py',
    version=version_ns['__version__'],
    packages=['contentful', 'contentful.cda'],
    url='https://github.com/contentful/contentful.py',
    license='Apache 2.0',
    author='Contentful GmbH',
    author_email='python@contentful.com',
    description='Python SDK for Contentful\'s Content Delivery API',
    long_description=readme,
    install_requires=deps,
    tests_require=test_deps,
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)
