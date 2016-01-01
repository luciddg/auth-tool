from codecs import open
from setuptools import setup, find_packages
from os import path
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))
install_reqs = parse_requirements(path.join(here, 'requirements.txt'))
reqs = [str(ir.req) for ir in install_reqs]

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='auth-tool',

    version='1.0.0',

    description='AuthTool',
    long_description=long_description,

    url='https://github.com/luciddg/auth-tool',

    author='Lucid Operations',
    author_email='ops@luciddg.com',

    license='MIT',

    packages=find_packages(exclude=['tests']),

    include_package_data=True,
    package_data={
        'auth-tool': [
            'public/*',
            'template/*',
        ],
    },

    data_files=[
        ('config', ['conf/app.cfg', 'conf/server.cfg']),
    ],

    install_requires=reqs,

    setup_requires=[
        'nose>=1.0'
    ],

    extras_require={
        'test': [
            'nose',
            'coverage',
            'mock',
            'mockldap',
        ],
    },

)
