from setuptools import setup

setup(
    name="jarfly",
    version="0.1dev",
    packages=['jarfly'],
    license='GPL',
    long_description=open('README.txt').read(),
    maintainer="Shannon Mitchell",
    maintainer_email="shannon.mitchell@rackspace.com",
    entry_points = {
        'console_scripts': [
            'jarflyd = jarfly.jarflyd:main',
        ],
    },
)
