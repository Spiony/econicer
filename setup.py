from setuptools import setup
from setuptools import find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="econicer",
    version="0.23",
    author="spiony",
    author_email="glumt@protonmail.com",
    description="A small program to analyse financial transactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Spiony/econicer",
    projects_urls={
        "Bug Tracker": "https://github.com/Spiony/econicer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'matplotlib>=3.4.1',
        'PyLaTeX>=1.4.1',
        'pandas>=1.2.3',
    ],
    include_package_data=True,
)
