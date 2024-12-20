from setuptools import setup, find_packages
            
setup(
    name='moduleimplant',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'torch',
        'ultralytics',
    ],
    description='A custom module implant system for Ultralytics models',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='acelych',
    author_email='acelych@foxmail.com',
    url='https://github.com/Gelinzh/moduleimplant',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'moduleimplant=moduleimplant.modify:main',
        ],
    },
)
