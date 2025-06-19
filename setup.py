from setuptools import setup, find_packages

setup(
    name="momo_analysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here or read from requirements.txt
        'flask',
        'waitress',
        'pandas',
        'lxml',
    ],
    python_requires='>=3.7',
)
