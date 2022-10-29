from setuptools import setup, find_packages
import pathlib
from MyListAnalyzer import __version__

here = pathlib.Path(__file__).parent
req = here / "requirements.txt"
setup(
    name="MyListAnalyzerDash",
    version=__version__,
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
    python_requires=">=3.7, <4",
    install_requires=req.read_text(),
    package_data={
        "": ["assets/MAL/*"]
    }
)
