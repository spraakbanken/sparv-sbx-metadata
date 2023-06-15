# sparv-sbx-metadata
Sparv plugin for SBX specific export of metadata


## Prerequisites

* [Sparv pipeline](https://github.com/spraakbanken/sparv-pipeline)
* [Python 3.8](https://python.org/) or newer

## Installation

**Option 1:** Installation from GitHub with [pipx](https://pipxproject.github.io/pipx/):
```bash
pipx inject sparv-pipeline https://github.com/spraakbanken/sparv-sbx-metadata/archive/latest.tar.gz
```

**Option 2:** Manual download of plugin and installation in your sparv-pipeline virtual environment:
```bash
source [path to sparv-pipeline virtual environment]/bin/activate
pip install [path to the downloaded sparv-sbx-metadata directory]
```


## Example config
```yaml
metadata:
  id: test
  language: swe
  name:
    eng: Test corpus
    swe: Testkorpus
  short_description:
    eng: A small test corpus for testing purposes
    swe: En liten testkorpus för att testa
  description:
    eng: This is an optional longer description that may contain HTML and multiple sentences.
    eng: Detta är en längre beskrivning som kan innehålla HTML och flera meningar.

korp:
  modes:
    - default # default setting

sbx_metadata:
  xml_export: scrambled # scrambled/original/false
  stats_export: true  # true/false
  korp: true  # true/false
  # script: Latn  # default setting

  ## 'downloads' and 'interface' are not needed for standard corpora
  # downloads:
  #   - url: http://spraakbanken.gu.se/lb/resurser/meningsmangder/gp-test.xml.bz2
  #     type: corpus
  #     format: XML
  #     info: this file contains a scrambled version of the corpus
  #     licence: CC BY 4.0
  #     restriction: attribution
  #   - url: https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens/gp-test.csv
  #     type: token frequencies
  #     format: XML
  #     info: ""
  #     licence: CC BY 4.0
  #     restriction: attribution
  # interface:
  #   - access: http://spraakbanken.gu.se/korp/#?corpus=gp-test
  #     licence: CC BY 4.0
  #     restriction: attribution

  ## 'contact_info' is only needed if somebody else is the contact person for the corpus
  # contact_info:
  #   name: Markus Forsberg
  #   email: sb-info@svenska.gu.se
  #   affiliation:
  #     organisation: Språkbanken
  #     email: sb-info@svenska.gu.se
```
