"""Metadata utilities."""
from typing import Optional

KORP_URL = "https://spraakbanken.gu.se/korp"
MENINGSMANGDER_URL = "https://spraakbanken.gu.se/lb/resurser/meningsmangder"
STATS_URL = "https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens"

STANDARD_LICENSE = "CC BY 4.0"

DEFAULT_CODE_LICENSE = "MIT License"

SBX_DEFAULT_CONTACT = {
    "name": "Markus Forsberg",
    "email": "sb-info@svenska.gu.se",
    "affiliation": {"organization": "Språkbanken Text", "email": "sb-info@svenska.gu.se"},
}


def make_standard_xml_export(xml_export: str, corpus_id: str) -> Optional[dict]:
    """Make license info object for standard XML export.

    Args:
        xml_export: Type of XML export.
        corpus_id: Corpus ID.

    Returns:
        License info object or None.
    """
    if xml_export in {"scrambled", "original"}:
        return {
            "url": f"{MENINGSMANGDER_URL}/{corpus_id}.xml.bz2",
            "type": "corpus",
            "format": "XML",
            "description": "this file contains a scrambled version of the corpus" if xml_export == "scrambled" else "",
            "license": STANDARD_LICENSE,
        }
    return None


def make_standard_stats_export(stats_export: bool, corpus_id: str) -> Optional[dict]:
    """Make license info object for standard token stats export.

    Args:
        stats_export: Whether token stats export is enabled.
        corpus_id: Corpus ID.

    Returns:
        License info object or None.
    """
    if stats_export:
        return {
            "url": f"{STATS_URL}/stats_{corpus_id}.csv",
            "type": "token frequencies",
            "format": "CSV",
            "description": "",
            "license": STANDARD_LICENSE,
        }
    return None


def make_korp(korp: bool, corpus_id: str, korp_modes: dict) -> Optional[dict]:
    """Make license info object for standard Korp interface.

    Args:
        korp: Whether the corpus is available in Korp.
        corpus_id: Corpus ID.
        korp_modes: The Korp modes where the corpus is available.

    Returns:
        License info object or None.
    """
    if korp:
        item = {"license": STANDARD_LICENSE}
        for mode in korp_modes:
            if mode.get("name") == "default":
                item["access"] = f"{KORP_URL}/#?corpus={corpus_id}"
                return item
        korp_mode = korp_modes[0].get("name")
        item["access"] = f"{KORP_URL}/?mode={korp_mode}#?corpus={corpus_id}"
        return item
    return None
