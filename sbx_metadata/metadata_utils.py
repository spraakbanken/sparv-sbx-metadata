"""Metadata utilities."""

from sparv.api import get_logger

KORP_URL = "https://spraakbanken.gu.se/korp"
MINK_URL = "https://spraakbanken.gu.se/mink"
MENINGSMANGDER_URL = "https://spraakbanken.gu.se/resurser/meningsmangder"
STATS_URL = "https://svn.spraakbanken.gu.se/sb-arkiv/pub/frekvens"

STANDARD_LICENSE = "CC BY 4.0"

DEFAULT_CODE_LICENSE = "MIT License"

SBX_DEFAULT_CONTACT = {
    "name": "Markus Forsberg",
    "email": "sb-info@svenska.gu.se",
    "affiliation": {"organization": "Språkbanken Text", "email": "sb-info@svenska.gu.se"},
}

logger = get_logger(__name__)


def make_standard_xml_export(corpus_id: str, scrambled: bool | None) -> dict | None:
    """Make license info object for standard XML export.

    Args:
        corpus_id: Corpus ID.
        scrambled: Whether the corpus is scrambled.

    Returns:
        License info object or None.
    """
    if scrambled is None:
        return None
    return {
        "url": f"{MENINGSMANGDER_URL}/{corpus_id}.xml.bz2",
        "type": "corpus",
        "format": "XML",
        "description": "this file contains a scrambled version of the corpus" if scrambled else "",
        "license": STANDARD_LICENSE,
    }


def make_standard_stats_export(corpus_id: str, stats_export: bool | None, installations: list | None) -> dict | None:
    """Make license info object for standard token stats export.

    Args:
        corpus_id: Corpus ID.
        stats_export: Whether token stats export is enabled.
        installations: List of selected installations.

    Returns:
        License info object or None.
    """
    stats_installation = installations and any(i.startswith("stats_export:") for i in installations)
    if stats_export and not stats_installation:
        logger.warning(
            "'sbx_metadata.stats_export' is enabled but no stats export installation is selected. "
            "Please check your configuration."
        )
    elif stats_export is False and stats_installation:
        logger.warning(
            "A stats export installation is selected but 'sbx_metadata.stats_export' is disabled. "
            "Please check your configuration."
        )
    if stats_export or stats_installation:
        return {
            "url": f"{STATS_URL}/stats_{corpus_id}.csv.zip",
            "type": "token frequencies",
            "format": "CSV",
            "description": "",
            "license": STANDARD_LICENSE,
        }
    return None


def make_korp(korp: bool, corpus_id: str, korp_modes: list[dict]) -> dict | None:
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
                item["url"] = f"{KORP_URL}/#?corpus={corpus_id}"
                return item
        korp_mode = korp_modes[0].get("name")
        item["url"] = f"{KORP_URL}/?mode={korp_mode}#?corpus={corpus_id}"
        return item
    return None
