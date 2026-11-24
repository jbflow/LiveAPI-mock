from setuptools import setup, find_packages

setup(
    name="live-api-mock",
    version="0.1.0",
    description="Mock of Ableton Live API for offline testing",
    author="Mantra Team",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pytest>=6.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
)
