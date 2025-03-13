from setuptools import find_packages, setup

setup(
    name="static_analyzer_agent",
    version="1.0.0",  # ✅ Required for dirctl version detection
    python_requires=">=3.8",  # ✅ Required for dirctl to detect Python version
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
)
