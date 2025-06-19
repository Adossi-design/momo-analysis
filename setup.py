from setuptools import setup, find_packages

setup(
    name="momo_analysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask>=2.0.0',
        'waitress>=2.0.0',
        'lxml>=4.0.0'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'momo-analysis=momo_analysis:main',
        ],
    },
)
