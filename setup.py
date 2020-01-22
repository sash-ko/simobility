from setuptools import setup

setup(
    name="simobility",
    description="Lightweight mobility simulation for quick " "algorithm prototyping",
    author="Oleksandr Lysenko",
    author_email="sashkolysenko@gmail.com",
    packages=[
        "simobility",
        "simobility.core",
        "simobility.metrics",
        "simobility.models",
        "simobility.routers",
    ],
    python_requires=">=3.7.*",
    install_requires=[
        "pandas>=0.24.1",
        "scipy>=1.2.1",
        "haversine",
        "geojson",
        "transitions"
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