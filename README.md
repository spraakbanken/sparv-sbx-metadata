# sparv-sbx-metadata
Sparv plugin for SBX specific export of metadata


## Prerequisites

* [Sparv pipeline](https://github.com/spraakbanken/sparv-pipeline)
* [Python 3.6.1](http://python.org/) or newer

## Installation

**Option 1:** Installation from pypi with [pipx](https://pipxproject.github.io/pipx/):
```bash
pipx inject sparv-pipeline sparv-sbx-metadata
```

**Option 2:** Installation from GitHub with [pipx](https://pipxproject.github.io/pipx/):
```bash
pipx inject sparv-pipeline https://github.com/spraakbanken/sparv-sbx-metadata/archive/latest.tar.gz
```

**Option 3:** Manual download of plugin and installation in your sparv-pipeline virtual environment:
```bash
source [path to sparv-pipeline virtual environment]/bin/activate
pip install [path to the downloaded sparv-sbx-metadata directory]
```


## Example config
```yaml
metadata:
  id: gp-test
  language: swe
  name:
    eng: GP test corpus
    swe: GP testkorpus
  description:
    eng: A small test corpus with texts from Göteborgsposten
    swe: En liten testkorpus med texter från Göteborgsposten

sbx_metadata:
  language_name:
    eng: Swedish
    swe: svenska
  # script: Latn # default
  # linguality: monolingual # default
  downloads:
    - licence: CC-BY
      restriction: attribution
      download: http://spraakbanken.gu.se/lb/resurser/meningsmangder/gp-test.xml.bz2
      info: this file contains a scrambled version of the corpus
      type: corpus
      format: XML
    - licence: CC-BY
      restriction: attribution
      download: https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens/gp-test.csv
      type: corpus
      format: XML
  interface:
    - licence: other
      restriction: other
      access: http://spraakbanken.gu.se/korp/#?corpus=gp-test
  # Move to some default config?
  contact_info:
    surname: Forsberg
    givenName: Markus
    email: sb-info@svenska.gu.se
    affiliation: 
      organisation: Språkbanken
      email: sb-info@svenska.gu.se
```
