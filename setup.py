'''
Copyright: University of Queensland, 2019
Contributors:
             Nicholas Lambourne - (University of Queensland, 2018)
'''

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

package_data = {
    'kaldi_helpers/inference_scripts': ['*'],
    'inference_scripts': ['*']
}

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='kaldi_helpers',
    version='0.23',
    packages=find_packages(),
    url='https://github.com/CoEDL/kaldi_helpers',
    install_requires=requirements,
    include_package_data=True,
    license='',
    author='CoEDL',
    author_email='n.lambourne@uq.edu.au',
    description='Scripts for preparing language data for use with Kaldi ASR',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Linguistic",
        "Operating System :: OS Independent",
    ],
    entry_points={
    },
)
