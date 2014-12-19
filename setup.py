from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
  long_description = f.read()

setup(
    name='passmgr',

    version='0.2.0',
    
    description='Lucid Password/Key Utility',
    long_description=long_description,

    url='https://repos.office.luciddg.com/',

    author='Lucid Operations',
    author_email='sysadmin@luciddg.com',

    license='MIT',

    packages=find_packages(exclude=['tests']),

    include_package_data=True,
    package_data={
      'passmgr': ['js/*', 
        'css/*',
        'images/*',
        'templates/*',
      ],
    },

    data_files=[
      ('conf', ['conf/passmgr.wsgi']),
    ],

    install_requires=[
      'CherryPy', 
      'Genshi',
      'TurboMail',
      'python-ldap',
      'simplejson',
      'smbpasswd',
      'wsgiref',
    ],

    setup_requires=[
      'nose>=1.0'
    ],

    extras_require= {
      'test': [
        'nose', 
        'coverage', 
        'mock',
        'mockldap',
      ],
    },

)
