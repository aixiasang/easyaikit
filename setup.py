from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easyaikit",
    version="0.1.1",
    author="xiasang",
    author_email="aixiasang@163.com",
    description="一个简单易用的 AI API 工具包，让 AI 调用更轻松",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aixiasang/easyaikit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    keywords="ai, openai, api, chatgpt, llm, wrapper, toolkit",
    entry_points={
        "console_scripts": [
            "easyai=easyaikit.cli:main",
        ],
    },
) 