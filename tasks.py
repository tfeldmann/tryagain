import os
from invoke import task


@task
def test():
    os.system('coverage run --source tryagain -m py.test')
    os.system('coverage report')


@task
def release(test=True):
    target = 'pypitest' if test else 'pypi'
    os.system('python3 setup.py register -r %s' % target)


@task
def upload(test=True):
    target = 'pypitest' if test else 'pypi'
    os.system('python3 setup.py bdist_wheel upload -r %s' % target)
