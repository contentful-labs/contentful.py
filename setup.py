from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


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
    'PyYAML==3.11',
    'SQLAlchemy==0.9.8',
    'contextlib2==0.4.0',
    'enum34==1.0.4',
    'requests==2.4.3',
    'six==1.8.0',
    'wrapt==1.10.2',
    'python-dateutil==2.3',
    'six==1.8.0'
]

test_deps = [
    'mock==1.0.1',
    'vcrpy==1.1.3',
    'pytest==2.6.4'
]

setup(
    name='contentful.py',
    version='0.9.0',
    packages=['test', 'test.lib', 'contentful', 'contentful.cda'],
    url='https://github.com/contentful/contentful.py',
    license='Apache 2.0',
    author='Contentful GmbH',
    author_email='info@contentful.com',
    description='Python SDK for Contentful\'s Content Delivery API',
    install_requires=deps,
    tests_require=test_deps,
    cmdclass={'test': PyTest}
)
