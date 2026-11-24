from setuptools import find_packages, setup

setup(
    name="live-api-mock",
    version="0.2.0",
    description="Offline mock of Ableton Live's Python API (the `Live` module), generated from the LiveAPI stubs",
    packages=find_packages(include=["Live", "Live.*"]),
    python_requires=">=3.7",
)
