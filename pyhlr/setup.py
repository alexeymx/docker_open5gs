from setuptools import setup, find_packages

setup(
    name="pyhlr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "asyncio>=3.4.3",
        "httpx>=0.24.0",
        "construct>=2.10.68",
        "pydantic>=1.8.0,<2.0.0",
        "python-dotenv>=0.19.0"
    ],
    python_requires=">=3.7",
    author="Your Name",
    author_email="your.email@example.com",
    description="HLR (Home Location Register) service with GSUP protocol support",
    keywords="hlr, gsup, mobile, telecom",
) 