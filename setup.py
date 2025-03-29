from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="nlp_knowledge_base",
    version="0.1.0",
    author="NLP Knowledge Base Creator",
    author_email="your.email@example.com",
    description="A tool to collect and categorize NLP-related posts from Stack Overflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nlp_knowledge_base",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nlp-kb=nlp_knowledge_base.src.main:main",
        ],
    },
) 
