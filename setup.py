# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.1'

setup(
        name='misc-utils',
        author='david_ding',
        author_email='chengjie.ding@gmail.com',
        version=version,
        packages=find_packages('src'),
        package_dir={'': 'src'},
        package_data={
            # 任何包中含有.txt文件，都包含它
            '': ['*.txt'],
            # 包含misc_utils.data文件夹中的 *.dat文件
            'misc_utils': ['data/*.dat'],
        },
        install_requires=['pymongo>=3.2'],
)
