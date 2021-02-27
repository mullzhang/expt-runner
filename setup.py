import os
from setuptools import setup, find_packages


def read_requirements():
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements


setup(
    name='expt-runner',
    version='0.0.1',
    description='Python module to run numerical experiments flexibly',
    long_description='README.md',
    author='mullzhang',
    install_requires=['omegaconf'],
    url='https://github.com/mullzhang/expt-runner',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests'
)
