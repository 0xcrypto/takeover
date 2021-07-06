import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "takeover.py",
    version = "0.0.10",
    author = "Vikrant Singh Chauhan",
    author_email = "vi@hackberry.xyz",
    description = ("This small script tries to detect subdomain takeovers from a list of domains. Fingerprints are taken from https://github.com/EdOverflow/can-i-take-over-xyz."),
    license = "WTFPL",
    keywords = "subdomain takeover",
    url = "http://github.com/0xcrypto/takeover",
    packages=['takeover'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Security",
        "License :: Public Domain",
    ],
    install_requires=[
        'requests', 'dnspython', 'discord.py'
    ],
    entry_points = {
        'console_scripts': ['takeover=takeover.takeover:main'],
    }
)
