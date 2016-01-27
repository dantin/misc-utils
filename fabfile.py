# -*- coding: utf-8 -*-
""" Fabric build scripts
"""
from fabric.api import *
from fabvenv import *

# The main module name, which is equal to repository name
env.name = 'misc-utils'
# Git repository url
env.repository = 'git@github.com:dantin/%s.git' % env.name
# Default Git branch
env.branch = 'master'

# Custom settings for different environments
# path：项目部署目录
env.settings = {
    # 开发环境
    'dev-tier': {
        'tier': 'dev',
        'hosts': ['10.3.1.241:22'],
        'path': '',
        'user': 'sem',
        'password': '',
        'activate': '/home/sem/venv/scrapyd/',
        'src': '/aztechx/sem/code/%s' % env.name,
        'env.repository': 'https://github.com/dantin/%s.git' % env.name
    },
    # 本地环境
    'local-tier': {
        'tier': 'local',
        'hosts': ['localhost'],
        'path': '',
        'user': '',
        'password': '',
        'activate': '/Users/david/Documents/venv/text/',  # 虚拟环境
        'src': '/Users/david/Documents/code/cosmos/%s' % env.name  # 源码路径
    }
}

env.hosts = ['']
env.src = ''
env.tier = 'dev'

version = '0.0.1'  # 版本


def cmd(__script, venv_path=None):
    """ Running cmd
    :param __script: cmd script
    :param venv_path: virtual environment path
    :return: None
    """
    if env.tier == 'local':
        local(__script)
    else:
        if venv_path:
            with virtualenv(venv_path):
                run(__script)
        else:
            run(__script)


def tier(__id):
    """ Environment switch
    :param __id: tier ID
    :return: None
    """
    env.update(env.settings['%s-tier' % __id])
    env.configured = True


def fetch():
    """ Git fetch
    """

    with(cd(env.src)):
        cmd('git fetch')


def update():
    """ Git update src files
    """
    with(cd(env.src)):
        cmd('git pull')


def checkout(branch=None):
    """ Git checkout to branch
    :param branch: target branch
    :return: None
    """
    if not branch:
        branch = env.branch
    with(cd(env.src)):
        cmd('git checkout %s' % branch)


def install():
    """ Install
    :return: None
    """
    cmd('pip install %s/dist/%s-%s.tar.gz' % (env.src, env.name, version), venv_path=env.activate)


def upgrade():
    """ Upgrade
    :return: None
    """
    cmd('pip install --upgrade dist/%s-%s.tar.gz' % (env.name, version), venv_path=env.activate)


def uninstall():
    """ Uninstall
    :return: None
    """
    cmd('pip uninstall %s' % env.name, venv_path=env.activate)


def build(branch='master'):
    """ Build source on remote machine, fab tier:dev build
    :param branch: branch name
    """
    fetch()
    checkout(branch)
    update()
    with(cd(env.src)):
        cmd('python setup.py sdist')
