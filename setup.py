from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymetadata',
    version='1.2.0',
    author='m8sec',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/m8r0wn/pymeta',
    license='GPLv3',
    packages=find_packages(include=["pymeta", "pymeta.*"]),
    install_requires=[
        'requests>=2.28.1',
        'bs4>=0.0.1'
    ],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Security"
    ],
    entry_points= {
        'console_scripts': ['pymeta=pymeta:main', 'pymetadata=pymeta:main']
    }
)
