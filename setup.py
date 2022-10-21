from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent

setup(
    name="MyListAnalyzerDash",
    version="0.0.2",
    description="A sample Python project",
    url="https://github.com/RahulARanger/MyListAnalyzer-Dash.git",
    author="RahulARanger",
    author_email="saihanumarahul66@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: MyAnimeList Users",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(where=str(here)),
    python_requires=">=3.7, <4"
)
