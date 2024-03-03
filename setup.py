from setuptools import setup, find_packages

setup(
    name="rocket",  # Replace with your package name
    version="0.1.0",  # Package version
    package_dir={"": "src"},  # Tells setuptools where your packages are
    packages=find_packages(where="src"),  # Automatically find packages under src
    # Add other parameters as needed, such as 'install_requires' for dependencies
)
