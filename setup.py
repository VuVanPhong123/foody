from setuptools import setup, find_packages

setup(
    name="FOODY_cus",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "kivy>=2.1.0",
        "kivymd>=1.1.1", 
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "requests>=2.28.0",
        "faiss-cpu>=1.7.0",
        "fastapi>=0.78.0",
        "uvicorn>=0.17.0",
        "pydantic>=1.9.0",
        "passlib>=1.7.4",
        "bcrypt>=3.2.0",
        "google-genai>=0.6.0",
        "scikit-learn>=1.2.2",
        "aiosqlite>=0.17.0",
    ],
    python_requires=">=3.8",  # Add Python version requirement
)