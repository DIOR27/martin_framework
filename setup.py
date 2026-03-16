from setuptools import setup, find_packages

setup(
    name="martin-framework",
    version="0.3.0",
    description="Build webs with pure Python",
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
