import os
from invoke import task


@task
def test():
    os.system('coverage run --source tryagain -m py.test')
    os.system('coverage report')


@task
def register(production=False):
    target = 'pypi' if production else 'pypitest'
    os.system('python3 setup.py register -r %s' % target)


@task
def upload(production=False):
    target = 'pypi' if production else 'pypitest'
    os.system('python3 setup.py bdist_wheel upload -r %s' % target)
