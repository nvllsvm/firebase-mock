import setuptools


setuptools.setup(
    name='firebasemock',
    version='0.0.11',
    author='Andrew Rabert',
    description=(
        'Mock HTTP implementations of Google Firebase and '
        'Google Instance ID.'
    ),
    url='https://github.com/nvllsvm/firebase-mock',
    packages=setuptools.find_packages(exclude=['tests.*']),
    test_suite='nose.collector',
    install_requires=['tornado<5'],
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
