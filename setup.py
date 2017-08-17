import os

import setuptools


def read_requirements(name):
    requirements = []
    with open(os.path.join('requires', name)) as f:
        for line in f:
            if '#' in line:
                line = line[:line.index('#')]
            line = line.strip()
            if line.startswith('-r'):
                requirements.extend(read_requirements(line[2:].strip()))
            elif line and not line.startswith('-'):
                requirements.append(line)
    return requirements


setuptools.setup(
    name='firebasemock',
    version='0.0.1',
    url='https://github.com/nvllsvm/firebase-mock',
    packages=['firebasemock'],
    test_suite='nose.collector',
    install_requires=read_requirements('installation.txt'),
    entry_points={'console_scripts':
                  ['firebasemock=firebasemock.app:run']},
)
