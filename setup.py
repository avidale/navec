
from setuptools import setup, find_packages

setup(
    name='navec',
    version='0.1.0',
    install_requires=['numpy'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'navec-train=navec.train.__main__:main'
        ]
    }
)