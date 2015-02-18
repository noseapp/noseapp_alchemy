# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

import noseapp_alchemy_ex


if __name__ == '__main__':
    setup(
        name='noseapp_alchemy_ex',
        version=noseapp_alchemy_ex.__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='SqlAlchemy extension for noseapp lib',
        install_requires=[
            'sqlalchemy==0.9.8',
            'wtforms==2.0.2',
            'WTForms-Alchemy==0.13.0',
        ],
    )
