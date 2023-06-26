from setuptools import setup

setup(
    name="SWAPI-ETL",
    version="0.1.0",
    packages=[""],
    url="https://github.com/isaacimholt/SWAPI-ETL",
    license="MIT",
    author="Isaac Imholt",
    author_email="isaacimholt@gmail.com",
    description="Star Wars API ETL",
    install_requires=[
        "aiohttp[speedups]",
        "async_lru",
        "pandas",
        "pydantic",
        "tenacity",
        "tqdm",
    ],
    # we could generate separate requirements for test/prod
    # but for simplicity in this project I make a single requirements.txt
    extras_require={
        "dev": [
            "pip-tools",
            "pytest",
        ]
    },
    python_requires=">=3.11",
)
