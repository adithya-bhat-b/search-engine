import setuptools
from os import path 

ROOT = path.abspath(path.dirname(__file__))

# Get requirements from file
with open(path.join(ROOT, "requirements.txt")) as f:
    requirements = [line.strip() for line in f.readlines() if not line.startswith("#")]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="search-engine", # Replace with your own username
    version="0.0.1",
    author="Adithya Bhat",
    author_email="adithyabhat.b@gmail.com",
    description="Repo for search utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    python_requires=">=3, <4",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)