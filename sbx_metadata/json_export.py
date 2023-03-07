"""Export corpus metadata to JSON (SBX specific)."""

import json
import os
from pathlib import Path

from sparv.api import (
    AnnotationCommonData,
    Config,
    Corpus,
    Export,
    ExportInput,
    Language,
    MarkerOptional,
    OutputMarker,
    SparvErrorMessage,
    exporter,
    get_logger,
    installer,
    uninstaller,
    util
)

from . import metadata_utils

logger = get_logger(__name__)


@exporter("JSON export of corpus metadata")
def json_export(out: Export = Export("sbx_metadata/[metadata.id].json"),
                corpus_id: Corpus = Corpus(),
                lang: Language = Language(),
                metadata: dict = Config("metadata"),
                sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
                tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
                # korp_protected: bool = Config("korp.protected"),
                korp_modes: list = Config("korp.modes"),
                md_trainingdata: bool = Config("sbx_metadata.trainingdata"),
                md_in_collections: list = Config("sbx_metadata.in_collections"),
                md_xml_export: str = Config("sbx_metadata.xml_export"),
                md_stats_export: bool = Config("sbx_metadata.stats_export"),
                md_korp: bool = Config("sbx_metadata.korp"),
                md_downloads: list = Config("sbx_metadata.downloads"),
                md_interface: list = Config("sbx_metadata.interface"),
                md_contact: dict = Config("sbx_metadata.contact_info")):
    """Export corpus metadata to JSON format."""
    md_obj = {}
    md_obj["name"] = metadata.get("name", {})

    # Set short description
    set_long_description = True
    if metadata.get("short_description"):
        md_obj["short_description"] = metadata.get("short_description", {})
    # Only long description available, use it for short_description!
    elif metadata.get("description"):
        set_long_description = False
        md_obj[f"short_description"] = metadata.get("description", {})

    md_obj["type"] = "corpus"
    md_obj["trainingdata"] = md_trainingdata
    md_obj["unlisted"] = False
    md_obj["successors"] = []
    md_obj["language_codes"] = [lang]

    # Set size
    md_obj["size"] = {
        "tokens": tokens.read(),
        "sentences": sentences.read()
    }

    md_obj["in_collections"] = md_in_collections or []

    # Set downloads
    downloads = []
    downloads.append(metadata_utils.make_standard_xml_export(md_xml_export, corpus_id))
    downloads.append(metadata_utils.make_standard_stats_export(md_stats_export, corpus_id))
    downloads.extend(md_downloads)
    md_obj["downloads"] = [d for d in downloads if d]

    # Set interface
    interface = []
    interface.append(metadata_utils.make_korp(md_korp, corpus_id, korp_modes))
    interface.extend(md_interface)
    md_obj["interface"] = [d for d in interface if d]

    # Set contact info
    if md_contact == "sbx-default":
        md_obj["contact_info"] = metadata_utils.SBX_DEFAULT_CONTACT
    else:
        md_obj["contact_info"] = md_contact

    # Set description
    if set_long_description and metadata.get("description"):
        md_obj[f"description"] = metadata.get("description", {})

    # Write JSON to file
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json_str = json.dumps(md_obj, ensure_ascii=False, indent=2)
    with open(out, "w", encoding="utf-8") as f:
        f.write(json_str)
    logger.info("Exported: %s", out)


@installer("Copy JSON metadata to remote host", uninstaller="sbx_metadata:uninstall_json")
def install_json(
    jsonfile: ExportInput = ExportInput("sbx_metadata/[metadata.id].json"),
    marker: OutputMarker = OutputMarker("sbx_metadata.install_json_export_marker"),
    uninstall_marker: MarkerOptional = MarkerOptional("sbx_metadata.uninstall_json_export_marker"),
    export_path: str = Config("sbx_metadata.json_export_path"),
    host: str = Config("sbx_metadata.json_export_host")
):
    """Copy JSON metadata to remote host."""
    if not host:
        raise SparvErrorMessage("'sbx_metadata.json_export_host' not set! JSON export not installed.")
    filename = Path(jsonfile).name
    remote_file_path = os.path.join(export_path, filename)
    util.install.install_path(jsonfile, host, remote_file_path)
    uninstall_marker.remove()
    marker.write()


@uninstaller("Uninstall JSON metadata")
def uninstall_json(
    corpus_id: Corpus = Corpus(),
    marker: OutputMarker = OutputMarker("sbx_metadata.uninstall_json_export_marker"),
    install_marker: MarkerOptional = MarkerOptional("sbx_metadata.install_json_export_marker"),
    export_path: str = Config("sbx_metadata.json_export_path"),
    host: str = Config("sbx_metadata.json_export_host")
):
    """Uninstall JSON metadata."""
    if not host:
        raise SparvErrorMessage("'sbx_metadata.json_export_host' not set! JSON export not uninstalled.")
    remote_file_path = os.path.join(export_path, f"{corpus_id}.json")
    util.install.uninstall_path(remote_file_path, host)
    install_marker.remove()
    marker.write()
