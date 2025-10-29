from setuptools import setup, find_packages

setup(
    name="akademik_atif_kontrol",
    version="0.1.0",
    description="Akademik atıf doğrulama sistemi",
    author="Gülbahar",
    packages=["modules"],
    install_requires=[
        "streamlit",
        "pandas",
        "altair",
        "requests",
        "python-docx",
        "PyMuPDF",
        "beautifulsoup4",
        "python-dotenv"
    ],
    python_requires=">=3.8",
)