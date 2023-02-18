import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "takeover.py",
    version = "1.0.0",
    author = "Vikrant Singh Chauhan",
    author_email = "vi@hackberry.xyz",
    description = ("This small script tries to detect subdomain takeovers from a list of domains. Fingerprints are taken from https://github.com/EdOverflow/can-i-take-over-xyz."),
    license = "MIT",
    keywords = "subdomain takeover",
    url = "http://github.com/0xcrypto/takeover",
    packages=['takeover'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'requests', 'dnspython', 'click', 'selenium'
    ],
    entry_points = {
        'console_scripts': ['takeover=takeover.takeover:main'],
    }
)
