from setuptools import setup
from simobility import __version__


setup(
    name="simobility",
    description="Lightweight mobility simulation for quick " "algorithm prototyping",
    author="Oleksandr Lysenko",
    author_email="sashkolysenko@gmail.com",
    version=__version__,
    packages=[
        "simobility",
        "simobility.core",
        "simobility.metrics",
        "simobility.routers",
        "simobility.simulator",
    ],
    python_requires=">=3.7.*",
    install_requires=[
        "pandas>=0.24.1",
        "scipy>=1.2.1",
        "haversine",
        "geojson",
        "transitions",
        "geopandas",
        "shapely",
        "requests",
        "pyarrow"
    ],
    extras_require={
        "dev": [
            "ipdb",
            "jupyter",
            "jupyterlab",
            "flake8",
            "nose",
            "coverage",
            "pytest",
            "pip-tools",
        ]
    },
    zip_safe=False,
)
