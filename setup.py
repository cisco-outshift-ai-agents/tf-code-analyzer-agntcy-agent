from setuptools import setup, find_packages

setup(
    name="tf-code-analyzer-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "agp-api>=0.0.6",  # Latest version from piwheels
        "requests",
        "aiohttp",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.5",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "requests>=2.31.0",
            "aiohttp>=3.9.3",
        ],
        "agp": [
            "agp-api",  # Optional AGP API dependency
        ],
    },
) 