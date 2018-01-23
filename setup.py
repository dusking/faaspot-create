import os
import codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

setup(
    name='faascli',
    version="0.0.1",
    author='Omer Duskin',
    author_email='dusking@gmail.com',
    license='LICENSE',
    platforms='All',
    description='FaaSpot App Creator',
    long_description=read('README.md'),
    entry_points={
        'console_scripts':
            ['faascli = faascli.main:main']
    },
    packages=[
        'faascli',
        'faascli.cli',
        'faascli.client',
        'faascli.commands',
    ],
    package_data={
        'faascli': [
            'VERSION'
        ]
    },
    install_requires=[
        'PyYAML==3.10',
        'boto3==1.5.9'
    ]
)
