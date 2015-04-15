# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


__version__ = '1.0.0'


if __name__ == '__main__':
    setup(
        name='noseapp_alchemy',
        url='https://github.com/trifonovmixail/noseapp_alchemy',
        version=__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='SqlAlchemy extension for noseapp lib',
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=[
            'noseapp>=1.0.9',
            'sqlalchemy==0.9.8',
        ],
    )
