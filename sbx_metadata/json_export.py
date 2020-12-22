"""Export corpus metadata to JSON (SBX specific)."""

import json
import os
import time

from iso639 import languages
from langcodes import Language
from sparv import AnnotationCommonData, Config, Export, exporter, util

from . import metadata_utils

logger = util.get_logger(__name__)


@exporter("JSON export of corpus metadata")
def json_export(out: Export = Export("sbx_metadata/[metadata.id].json"),
                metadata: dict = Config("metadata"),
                sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
                tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
                korp_protected: bool = Config("korp.protected"),
                korp_mode: bool = Config("korp.mode"),
                md_trainingdata: bool = Config("sbx_metadata.trainingdata"),
                md_xml_export: str = Config("sbx_metadata.xml_export"),
                md_stats_export: bool = Config("sbx_metadata.stats_export"),
                md_korp: bool = Config("sbx_metadata.korp"),
                md_downloads: list = Config("sbx_metadata.downloads"),
                md_interface: list = Config("sbx_metadata.interface"),
                md_contact: dict = Config("sbx_metadata.contact_info")):
    """Export corpus metadata to JSON format."""
    md_obj = {}
    md_obj["id"] = metadata["id"]
    md_obj["type"] = "corpus"
    md_obj["trainingdata"] = md_trainingdata

    # Set language info
    lang = metadata["language"]
    md_obj["lang"] = [{
        "code": lang,
        "name_en": languages.get(part3=lang).name if lang in languages.part3 else lang,
        "name_sv": Language.get(lang).display_name("swe"),
    }]

    # Set name and description
    md_obj["name_en"] = metadata.get("name", {}).get("eng")
    md_obj["name_sv"] = metadata.get("name", {}).get("swe")
    md_obj["description_en"] = metadata.get("description", {}).get("eng")
    md_obj["description_sv"] = metadata.get("description", {}).get("swe")

    # Set downloads
    downloads = []
    downloads.append(metadata_utils.make_standard_xml_export(md_xml_export, metadata["id"]))
    downloads.append(metadata_utils.make_standard_stats_export(md_stats_export, metadata["id"]))
    downloads.append(metadata_utils.make_metashare(metadata["id"]))
    downloads.extend(md_downloads)
    md_obj["downloads"] = [d for d in downloads if d]

    # Set interface
    interface = []
    interface.append(metadata_utils.make_korp(md_korp, metadata["id"], korp_mode))
    interface.extend(md_interface)
    md_obj["interface"] = [d for d in interface if d]

    # Set contact info
    if md_contact == "sbx-default":
        md_obj["contact_info"] = metadata_utils.SBX_DEFAULT_CONTACT
    else:
        md_obj["contact_info"] = md_contact

    # Set size
    md_obj["size"] = {
        "tokens": tokens.read(),
        "sentences": sentences.read()
    }

    # Write JSON to file
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json_str = json.dumps(md_obj, ensure_ascii=False, indent=4)
    with open(out, "w") as f:
        f.write(json_str)
    logger.info("Exported: %s", out)
