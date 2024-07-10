from setuptools import setup, find_packages

setup(
    name='model',
    version='0.1.0',
    packages=find_packages(include=['model', 'model.*']),
    install_requires=[
        # List your dependencies here, e.g., 'numpy', 'scipy', etc.
    ],
    author='Rudy Alkarem',
    author_email='rudy.alkarem@nrel.gov',
    description='A library for modeling the stiffness and response of mooring lines for floating offshore wind turbines linearly.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Yuksel-Rudy/LSM.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)