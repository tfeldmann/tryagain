try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="tryagain",
    version="0.1",
    description="A simple and pythonic retry helper",
    author="Thomas Feldmann",
    author_email="info@tfeldmann.de",
    packages=["tryagain"],
    url="https://github.com/tfeldmann/tryagain",
)
