"""
Copyright: University of Queensland, 2019
Contributors:
             Nicholas Lambourne - (University of Queensland, 2018)
"""

from setuptools import setup, find_packages

requirements = [
    'pytest',
    'pympi-ling',
    'numpy',
    'langid',
    'nltk',
    'praatio',
    'pydub',
]

include_package_data = True

setup(
    name='kaldi_helpers',
    version='0.2',
    packages=find_packages(),
    url='https://github.com/CoEDL/kaldi-helpers',
    install_requires=requirements,
    include_package_data=True,
    license='',
    author='CoEDL',
    author_email='n.lambourne@uq.edu.au',
    description='Scripts for preparing language data for use with Kaldi ASR',
    entry_points={
    },
)
