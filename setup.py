from setuptools import setup, find_packages

setup(
    name="foody",
    version="0.1.0",
    description="Foody restaurant management application",
    author="Foody Team",
    packages=find_packages(),
    install_requires=[
        "kivy>=2.1.0",
        "kivymd>=1.1.1",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "langchain>=0.0.208",
        "requests>=2.28.0",  # For OpenRouter API calls
        "faiss-cpu>=1.7.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "foody=foody.main:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)