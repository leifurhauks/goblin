from setuptools import setup, find_packages

version = open('goblin/VERSION', 'r').readline().strip()

develop_requires = ['Sphinx==1.3.5',
                    'tornado==4.3',
                    'factory-boy==2.6.0',
                    'gremlinclient==0.2.6',
                    'inflection==0.3.1',
                    'ipaddress==1.0.16',
                    'newrelic==2.60.0.46',
                    'nose==1.3.7',
                    'pyformance==0.3.2',
                    'pyparsing==2.1.0',
                    'pytz==2015.7',
                    'six==1.10.0',
                    'sphinx-rtd-theme==0.1.9',
                    'tox==2.3.1',
                    'Twisted==15.5.0',
                    'watchdog==0.8.3']

long_desc = """
Object-Graph Mapper (OGM) for the TinkerPop 3 Gremlin Server

`Documentation <https://github.com/ZEROFAIL/goblin>`_

`Report a Bug <https://github.com/ZEROFAIL/goblin/issues>`_

Goblin uses @davebshow gremlinclient for asynchronous websocket based communication with the Gremlin Server,
and is therefore designed to be multi-platform, allowing the user to choose between Tornado, Trollius, or Asyncio.

It aims to provide full support for all TinkerPop3 enabled graph databases;
however, it is currently only tested against Titan:db 1.x.

This project is under active development.
"""

setup(
    name='goblin',
    version=version,
    description='Object-Graph Mapper (OGM) for the TinkerPop 3 Gremlin Server',
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='tinkerpop,titan,ogm,goblin,gremlin',
    install_requires=['pyparsing>=2.0.2',
                      'pytz>=2015.7',
                      'gremlinclient>=0.2.6',
                      'inflection>=0.3.1',
                      'ipaddress>=1.0.16',
                      'six>=1.10.0',
                      'factory-boy>=2.6.0'],
    extras_require={
        'develop': develop_requires,
        'newrelic': ['newrelic>=2.60.0.46'],
        'docs': ['Sphinx>=1.2.2', 'sphinx-rtd-theme>=0.1.6', 'watchdog>=0.8.3', 'newrelic>=2.60.0.46']
    },
    test_suite='nose.collector',
    tests_require=develop_requires,
    author='Cody Lee',
    author_email='codylee@wellaware.us',
    maintainer='David Brown',
    maintainer_email='davebshow@gmail.com',
    url='https://github.com/ZEROFAIL/goblin',
    license='Apache Software License 2.0',
    include_package_data=True,
    packages=find_packages()
)
