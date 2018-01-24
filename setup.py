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
    version='0.0.11',
    url='https://github.com/nvllsvm/firebase-mock',
    packages=setuptools.find_packages(exclude=['tests.*']),
    test_suite='nose.collector',
    install_requires=read_requirements('installation.txt'),
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-cov'
    ],
    entry_points={'console_scripts':
                  ['firebasemock=firebasemock.app:run']},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha']
)
