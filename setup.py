from pathlib import Path

from setuptools import setup

INSTALL_REQUIRE = ["pydantic>=2.10.6", "django"]


setup(
    name="django-pydantic-models",
    version="0.0.1",
    license="MIT",
    author="Smartwa",
    maintainer="Smartwa",
    author_email="simatwacaleb@proton.me",
    description=(
        """A lightweight utility that converts Django models into fully-typed Pydantic models,
          supporting automatic field mapping, validation constraint and nested model generation 
          for related fields"""
    ),
    packages=["django_pydantic_models"],
    url="https://github.com/Simatwa/django-pydantic-models",
    project_urls={
        "Bug Report": "https://github.com/Simatwa/django-pydantic-models/issues/new",
        "Homepage": "https://github.com/Simatwa/django-pydantic-models",
        "Source Code": "https://github.com/Simatwa/django-pydantic-models",
        "Issue Tracker": "https://github.com/Simatwa/django-pydantic-models/issues",
        "Download": "https://github.com/Simatwa/django-pydantic-models/releases",
        "Documentation": "https://github.com/Simatwa/django-pydantic-models/blob/main/docs",
    },
    install_requires=INSTALL_REQUIRE,
    python_requires=">=3.10",
    keywords=["django", "pydantic"],
    long_description=Path.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
