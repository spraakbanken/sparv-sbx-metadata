# sparv-sbx-metadata

Sparv plugin for SBX specific export of metadata, including resource metadata and analysis metadata.

## Prerequisites

* [Sparv](https://github.com/spraakbanken/sparv) v5.3 or newer
* [Python 3.10](https://python.org/) or newer

## Installation

Install the latest stable version from GitHub:

```sh
sparv plugins install https://github.com/spraakbanken/sparv-sbx-metadata/archive/main.zip
```

## Usage

### Corpus Metadata Export

Use the `sbx_metadata` section in your corpus configuration file to specify additional metadata about the corpus. For a
list of available configuration options, run `sparv modules sbx_metadata` in your terminal. For more information about
the types of values for the different fields, refer to the [metadata documentation and
templates](https://github.com/spraakbanken/metadata/).

### Analysis Metadata Export

Refer to the [separate documentation](docs/analysis-metadata.md) for detailed information on analysis metadata export.
