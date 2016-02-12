from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name="tryagain",
    version=__import__('tryagain').__version__,
    license='MIT',
    description="A lightweight and pythonic retry helper",
    long_description=readme,
    author="Thomas Feldmann",
    author_email="mail@tfeldmann.de",
    url="https://github.com/tfeldmann/tryagain",
    py_modules=["tryagain"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['retry', 'unstable', 'try again', 'tryagain', 'redo'],
)
