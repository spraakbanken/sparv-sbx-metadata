"""Metadata utilities."""

from sparv.api import SparvErrorMessage


KORP_URL = "https://spraakbanken.gu.se/korp"
MENINGSMANGDER_URL = "https://spraakbanken.gu.se/lb/resurser/meningsmangder"
STATS_URL = "https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens"
METASHARE_URL = "https://svn.spraakdata.gu.se/sb-arkiv/pub/metadata/corpus"

STANDARD_LICENSE = "CC BY 4.0"


SBX_DEFAULT_CONTACT = {
    "name": "Markus Forsberg",
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
            "url": f"{MENINGSMANGDER_URL}/{corpus_id}.xml.bz2",
            "type": "corpus",
            "format": "XML",
            "info": "this file contains a scrambled version of the corpus" if xml_export == "scrambled" else "",
            "licence": STANDARD_LICENSE,
            "restriction": "attribution"
        }
        return item
    elif not xml_export:
        return
    else:
        raise SparvErrorMessage(f"Invalid config value for sbx_metadata.xml_export: '{xml_export}'. "
                                "Possible values: 'scrambled', 'original', False")


def make_standard_stats_export(stats_export: bool, corpus_id: str):
    """Make license info object for standard token stats export."""
    if stats_export:
        return {"url": f"{STATS_URL}/stats_{corpus_id}.csv",
                "type": "token frequencies",
                "format": "CSV",
                "info": "",
                "licence": STANDARD_LICENSE,
                "restriction": "attribution"
                }


def make_korp(korp: bool, corpus_id: str, korp_modes: dict):
    """Make license info object for standard Korp interface."""
    if korp:
        item = {"licence": STANDARD_LICENSE,
                "restriction": "attribution"}
        for mode in korp_modes:
            if mode.get("name") == "default":
                item["access"] = f"{KORP_URL}/#?corpus={corpus_id}"
                return item
        korp_mode = korp_modes[0].get("name")
        item["access"] = f"{KORP_URL}/?mode={korp_mode}#corpus={corpus_id}"
        return item


def make_metashare(corpus_id: str):
    """Make downloadable object pointing to META-SHARE file."""
    return {"url": f"{METASHARE_URL}/{corpus_id}.xml",
            "type": "metadata",
            "format": "METASHARE",
            "licence": STANDARD_LICENSE,
            "restriction": "attribution"
            }
