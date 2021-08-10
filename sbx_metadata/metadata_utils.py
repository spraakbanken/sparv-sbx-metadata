"""Metadata utilities."""

from sparv.api import SparvErrorMessage


KORP_URL = "https://spraakbanken.gu.se/korp"
MENINGSMANGDER_URL = "https://spraakbanken.gu.se/lb/resurser/meningsmangder"
STATS_URL = "https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens"
METASHARE_URL = "https://svn.spraakdata.gu.se/sb-arkiv/pub/metadata/corpus"

STANDARD_LICENSE = "CC BY 4.0"


SBX_DEFAULT_CONTACT = {
    "surname": "Forsberg",
    "givenName": "Markus",
    "email": "sb-info@svenska.gu.se",
    "affiliation": {
        "organisation": "Språkbanken",
        "email": "sb-info@svenska.gu.se"
    }
}


def make_standard_xml_export(xml_export, corpus_id: str):
    """Make license info object for standard XML export."""
    if xml_export in ("scrambled", "original"):
        item = {
            "licence": STANDARD_LICENSE,
            "restriction": "attribution",
            "download": f"{MENINGSMANGDER_URL}/{corpus_id}.xml.bz2",
            "type": "corpus",
            "format": "XML"
        }
        if xml_export == "scrambled":
            item["info"] = "this file contains a scrambled version of the corpus"
        return item
    elif not xml_export:
        return
    else:
        raise SparvErrorMessage(f"Invalid config value for sbx_metadata.xml_export: '{xml_export}'. "
                                "Possible values: 'scrambled', 'original', False")


def make_standard_stats_export(stats_export: bool, corpus_id: str):
    """Make license info object for standard token stats export."""
    if stats_export:
        return {"licence": STANDARD_LICENSE,
                "restriction": "attribution",
                "download": f"{STATS_URL}/stats_{corpus_id}.csv",
                "type": "token frequencies",
                "format": "CSV"
                }


def make_korp(korp: bool, corpus_id: str, korp_modes: list):
    """Make license info object for standard Korp interface."""
    if korp:
        item = {"licence": STANDARD_LICENSE,
                "restriction": "attribution"}
        if "default" in korp_modes:
            item["access"] = f"{KORP_URL}/#?corpus={corpus_id}"
        else:
            korp_mode = korp_modes[0]
            item["access"] = f"{KORP_URL}/?mode={korp_mode}#corpus={corpus_id}"
        return item


def make_metashare(corpus_id: str):
    """Make downloadable object pointing to META-SHARE file."""
    return {"licence": STANDARD_LICENSE,
            "restriction": "attribution",
            "download": f"{METASHARE_URL}/{corpus_id}.xml",
            "type": "metadata",
            "format": "METASHARE"
            }
