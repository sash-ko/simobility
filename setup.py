from setuptools import setup
from simobility import __version__

setup(
    name="simobility",
    description="Lightweight mobility simulation for quick algorithm prototyping",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Oleksandr Lysenko",
    author_email="sashkolysenko@gmail.com",
    version=__version__,
    license="MIT",
    url="https://github.com/sash-ko/simobility",
    download_url="https://github.com/sash-ko/simobility/archive/v0.4.0.tar.gz",
    packages=[
        "simobility",
        "simobility.core",
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
        "pyarrow",
        "pyyaml",
        "h3"
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
            "pytest-cov"
        ]
    },
    zip_safe=False,
)
