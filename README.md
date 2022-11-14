# sparv-sbx-metadata
Sparv plugin for SBX specific export of metadata


## Prerequisites

* [Sparv pipeline](https://github.com/spraakbanken/sparv-pipeline)
* [Python 3.6.2](http://python.org/) or newer

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
  #   - licence: CC BY 4.0
  #     restriction: attribution
  #     download: http://spraakbanken.gu.se/lb/resurser/meningsmangder/gp-test.xml.bz2
  #     info: this file contains a scrambled version of the corpus
  #     type: corpus
  #     format: XML
  #   - licence: CC BY 4.0
  #     restriction: attribution
  #     download: https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens/gp-test.csv
  #     type: token frequencies
  #     format: XML
  # interface:
  #   - licence: other
  #     restriction: other
  #     access: http://spraakbanken.gu.se/korp/#?corpus=gp-test

  ## 'contact_info' is only needed if somebody else is the contact person for the corpus
  # contact_info:
  #   surname: Forsberg
  #   givenName: Markus
  #   email: sb-info@svenska.gu.se
  #   affiliation:
  #     organisation: Språkbanken
  #     email: sb-info@svenska.gu.se
```
