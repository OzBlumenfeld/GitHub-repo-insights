from setuptools import setup, find_packages

setup(
    name='github_data_extractor_OzB',
    version='0.2',
    packages=find_packages(),
    description='github data extractor that reveals some insights about a github repository',
    author='OzB',
    url='https://github.com/OzBlumenfeld/GitHub-repo-insights',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'requests',
        'typing_extensions',
        'pydot==2.0.0',
        'graphviz==0.20.3'
    ],
)