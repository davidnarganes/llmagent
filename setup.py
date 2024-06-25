from setuptools import setup, find_packages

setup(
    name='llmagent',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            # Define any CLI commands here
        ],
    },
)
