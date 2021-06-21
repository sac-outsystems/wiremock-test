"""
Setup file to package the API
"""
from setuptools import find_packages, setup


setup(
    name="simple-soap-tests",
    version="1.0.0",
    description="Simple soap tests",
    long_description="Nothing fancy",
    url="https://localhost",
    install_requires=[
    ],
    keywords="utilities",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: MATURE",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
