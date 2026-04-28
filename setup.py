from setuptools import setup, find_packages

setup(
    name="xtcv3utils",
    version="1.1.0",
    description="XTC V3 API Encryption/Decryption Utils",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pycryptodome>=3.10",
    ],
    python_requires=">=3.8",
    author="xtcv3utils contributors",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Security :: Cryptography",
    ],
    url="https://github.com/yourusername/xtcv3utils",
)
