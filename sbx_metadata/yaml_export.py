"""Export corpus metadata to YAML (SBX specific)."""

import re
from datetime import datetime
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
    util,
)

from . import metadata_utils

logger = get_logger(__name__)

# Max length for short_description (if exceeded, a warning will be issued)
MAX_SHORT_DESC_LEN = 250


@exporter("YAML export of corpus metadata")
def yaml_export(
    out: Export = Export("sbx_metadata/[metadata.id].yaml"),
    corpus_id: Corpus = Corpus(),
    language: Language = Language(),
    metadata: dict = Config("metadata"),
    sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
    tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
    # korp_protected: bool = Config("korp.protected"),
    korp_modes: list = Config("korp.modes"),
    md_language: bool = Config("sbx_metadata.language"),
    md_trainingdata: bool = Config("sbx_metadata.trainingdata"),
    md_in_collections: list = Config("sbx_metadata.in_collections"),
    md_unlisted: bool = Config("sbx_metadata.unlisted"),
    md_annotation: dict = Config("sbx_metadata.annotation"),
    md_keywords: list = Config("sbx_metadata.keywords"),
    md_caveats: dict = Config("sbx_metadata.caveats"),
    md_creators: list = Config("sbx_metadata.creators"),
    md_standard_reference: str = Config("sbx_metadata.standard_reference"),
    md_other_references: list = Config("sbx_metadata.other_references"),
    md_intended_uses: dict = Config("sbx_metadata.intended_uses"),
    md_xml_export: str = Config("sbx_metadata.xml_export"),
    md_stats_export: bool = Config("sbx_metadata.stats_export"),
    md_korp: bool = Config("sbx_metadata.korp"),
    md_downloads: list = Config("sbx_metadata.downloads"),
    md_interface: list = Config("sbx_metadata.interface"),
    md_contact: dict = Config("sbx_metadata.contact_info"),
    md_created: str = Config("sbx_metadata.created"),
    md_updated: str = Config("sbx_metadata.updated"),
):
    """Export corpus metadata to YAML format."""
    md_obj = {"name": metadata.get("name", {})}

    # Set short description
    set_long_description = True
    if metadata.get("short_description"):
        md_obj["short_description"] = metadata.get("short_description", {})
    # Only long description available, use it for short_description!
    elif metadata.get("description"):
        set_long_description = False
        md_obj["short_description"] = metadata.get("description", {})

    for lang, short_description in md_obj.get("short_description", {}).items():
        # Warn if short description seems to contain HTML
        if re.search(r"<([a-z][a-z0-9]+)\b[^>]*>", short_description):
            logger.warning(
                f"'short_description' ({lang}) seems to contain HTML."
                if set_long_description
                else f"No 'short_description' available and 'description' ({lang}) seems to contain HTML."
            )
        # Warn if short description is too long
        if len(short_description) > MAX_SHORT_DESC_LEN:
            logger.warning(
                f"'short_description' ({lang}) is longer than {MAX_SHORT_DESC_LEN} characters."
                if set_long_description
                else f"No 'short_description' available and 'description' ({lang}) is longer than {MAX_SHORT_DESC_LEN} "
                "characters."
            )

    md_obj["type"] = "corpus"
    md_obj["trainingdata"] = md_trainingdata
    md_obj["unlisted"] = md_unlisted
    md_obj["successors"] = []
    md_obj["language_codes"] = [str(md_language) if md_language else str(language)]

    # Set size
    md_obj["size"] = {"tokens": int(tokens.read()), "sentences": int(sentences.read())}

    md_obj["in_collections"] = md_in_collections

    # Set downloads
    downloads = [
        metadata_utils.make_standard_xml_export(md_xml_export, corpus_id),
        metadata_utils.make_standard_stats_export(md_stats_export, corpus_id),
        *md_downloads,
    ]
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

    md_obj["annotation"] = md_annotation
    md_obj["keywords"] = md_keywords
    md_obj["caveats"] = md_caveats
    md_obj["creators"] = md_creators
    md_obj["standard_reference"] = md_standard_reference
    md_obj["other_references"] = md_other_references
    md_obj["intended_uses"] = md_intended_uses
    md_obj["created"] = md_created or datetime.now().strftime("%Y-%m-%d")  # Use today's date as default
    md_obj["updated"] = md_updated or datetime.now().strftime("%Y-%m-%d")  # Use today's date as default

    # Set description
    if set_long_description and metadata.get("description"):
        md_obj["description"] = metadata.get("description", {})
    else:
        md_obj["description"] = {"swe": "", "eng": ""}

    # Write YAML to file
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open(mode="w", encoding="utf-8") as yaml_file:
        yaml_file.write(
            "# This file was automatically generated by Sparv. Do not make changes directly to this file as they will "
            "get overwritten.\n"
        )
        yaml_file.write(util.misc.dump_yaml(md_obj))

    logger.info("Exported: %s", out)


@installer("Copy YAML metadata to remote host", uninstaller="sbx_metadata:uninstall_yaml")
def install_yaml(
    yamlfile: ExportInput = ExportInput("sbx_metadata/[metadata.id].yaml"),
    marker: OutputMarker = OutputMarker("sbx_metadata.install_yaml_export_marker"),
    uninstall_marker: MarkerOptional = MarkerOptional("sbx_metadata.uninstall_yaml_export_marker"),
    export_path: str = Config("sbx_metadata.yaml_export_path"),
    host: str = Config("sbx_metadata.yaml_export_host"),
):
    """Copy YAML metadata to remote host."""
    if not host:
        raise SparvErrorMessage("'sbx_metadata.yaml_export_host' not set! YAML export not installed.")
    filename = Path(yamlfile).name
    remote_file_path = Path(export_path) / filename
    util.install.install_path(yamlfile, host, remote_file_path)
    uninstall_marker.remove()
    marker.write()


@uninstaller("Uninstall YAML metadata")
def uninstall_yaml(
    corpus_id: Corpus = Corpus(),
    marker: OutputMarker = OutputMarker("sbx_metadata.uninstall_yaml_export_marker"),
    install_marker: MarkerOptional = MarkerOptional("sbx_metadata.install_yaml_export_marker"),
    export_path: str = Config("sbx_metadata.yaml_export_path"),
    host: str = Config("sbx_metadata.yaml_export_host"),
):
    """Uninstall YAML metadata."""
    if not host:
        raise SparvErrorMessage("'sbx_metadata.yaml_export_host' not set! YAML export not uninstalled.")
    remote_file_path = Path(export_path) / f"{corpus_id}.yaml"
    util.install.uninstall_path(remote_file_path, host)
    install_marker.remove()
    marker.write()
