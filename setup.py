from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymetadata',
    version='1.0.2',
    author = 'm8r0wn',
    author_email = 'm8r0wn@protonmail.com',
    description = 'Web scraper to download and extract file metadata',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/m8r0wn/pymeta',
    license='GPLv3',
    platforms=["Unix"],
    packages=find_packages(include=["pymeta", "pymeta.*"]),
    package_data={'pymeta': ['resources/*']},
    install_requires=[
        'bs4',
        'requests',
    ],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Topic :: Security"
    ],
    entry_points= {
        'console_scripts': ['pymeta=pymeta:main', 'pymetadata=pymeta:main']
    }
)