from setuptools import setup, find_packages
import sys

requirements = [
    'pytest',
    'pympi-ling',
    'numpy',
    'langid',
    'nltk',
    'praatio',
    'pydub',
    'regex',
    'pyparsing',
]

include_package_data = True

setup(
    name='kaldi_helpers',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/CoEDL/kaldi-helpers',
    install_requires=requirements,
    include_package_data=True,
    license='',
    author='',
    author_email='n.lambourne@uq.edu.au',
    description='Scripts for preparing language data for use with Kaldi ASR',
    entry_points={
        # 'console_scripts': [
        #     'kaldi_helpers_ = kadli_helpers.__main__:main',
        # ],
    },
)
