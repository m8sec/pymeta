from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymetasec',
    version='1.1.1',
    author = 'm8sec',
    description = 'Web scraper to download and extract file metadata',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/m8sec/pymeta',
    license='GPLv3',
    platforms=["Unix"],
    packages=find_packages(include=["pymeta", "pymeta.*"]),
    package_data={'pymeta': ['resources/*']},
    install_requires=[
        'bs4',
        'requests'
    ],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Topic :: Security"
    ],
    entry_points= {
        'console_scripts': ['pymeta=pymeta:main', 'pymetasec=pymeta:main']
    }
)
