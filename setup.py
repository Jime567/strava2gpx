from setuptools import setup, find_packages

setup(
    name="strava2gpx",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'aiofiles',
    ],
    tests_require=['unittest'],
    author="James Phelps",
    author_email="jamesphelpsmail@gmail.com",
    description="A package to convert Strava activities to GPX format",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/jime567/strava2gpx",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)