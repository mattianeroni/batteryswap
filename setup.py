from setuptools import setup

setup(
    name='batteryswap',
    version='0.0.1',
    description='A discrete event simulation showing that the future for electric vehicles is batteries sharing.',
    author='Mattia Neroni, Ph.D, Eng.',
    author_email='mattianeroni@yahoo.it',
    url='https://github.com/mattianeroni/batteryswap',
    packages=[
        "simulation"
    ],
    #package_dir = [
    #    "simulation" : "simulation",
    #],
    python_requires='>=3.9',
    classifiers=[
        "Development Status :: 3 - Alpha"
    ]
)
