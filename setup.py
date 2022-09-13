"""Install script for the Sparv SBX metadata plugin."""

import os.path

import setuptools


def get_readme(readme_path):
    """Get the contents of the README file."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, readme_path), encoding="utf-8") as f:
        return f.read()


setuptools.setup(
    name="sparv-sbx-metadata",
    version="1.0.1",
    description="Sparv plugin for SBX specific export of metadata",
    long_description=get_readme("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/spraakbanken/sparv-sbx-metadata/",
    author="Språkbanken",
    author_email="sb-info@svenska.gu.se",
    license="MIT",
    packages=["sbx_metadata"],
    python_requires=">=3.6.2",
    install_requires=[
        "langcodes[data]>=2.1.0",
        "sparv-pipeline>=5.0.1.dev0",
    ],
    entry_points={"sparv.plugin": ["sbx_metadata = sbx_metadata"]}
)
