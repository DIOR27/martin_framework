from setuptools import setup, find_packages

setup(
    name="martin",
    version="0.1.0",
    description="Build webs with Python, Flutter-style",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    packages=find_packages(),
    entry_points={"console_scripts": ["martin=martin.cli:main"]},
    extras_require={"dev": ["watchdog>=3.0"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
