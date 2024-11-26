"""Metadata export (SBX specific)."""

import re
from typing import Dict, List

from sparv.api import Config, wizard

from . import yaml_export

__config__ = [
    Config(
        "sbx_metadata.script",
        default="Latn",
        description="Writing system used to represent the language of the corpus (ISO-15924)",
        datatype=str,
    ),
    Config(
        "sbx_metadata.language",
        default="",
        description="Language of source files (ISO 639-3). Use this to override metadata.language, for "
                    "language codes not supported by Sparv.",
        datatype=str,
    ),
    # Config(
    #     "sbx_metadata.linguality",
    #     default="monolingual",
    #     description="Indicates whether the corpus includes one, two or more languages (monolingual, bilingual or "
    #                 "multilingual)"
    # ),
    Config(
        "sbx_metadata.xml_export",
        default="scrambled",
        description="Whether XML export may be published. Values: scrambled, original, false",
        datatype=str,
        choices=("scrambled", "original", "false"),
    ),
    Config(
        "sbx_metadata.stats_export",
        default=True,
        description="Whether token frequency export may be published",
        datatype=bool,
    ),
    Config(
        "sbx_metadata.korp", default=True, datatype=bool, description="Whether the corpus will be published in Korp"
    ),
    Config(
        "sbx_metadata.downloads", default=[], datatype=list, description="Downloadable files belonging to the corpus"
    ),
    Config(
        "sbx_metadata.interface",
        default=[],
        description="List of interfaces where the corpus is available",
        datatype=list,
    ),
    Config(
        "sbx_metadata.contact_info",
        default="sbx-default",
        description="Object containing information about the contact person for the resource",
    ),
    Config(
        "sbx_metadata.trainingdata",
        default=False,
        description="Whether the corpus is intended as training data",
        datatype=bool,
    ),
    Config(
        "sbx_metadata.unlisted",
        default=False,
        description="If set to 'true', the resource won't be listed on the "
        "Språkbanken Text web page, but it will be accessible via its URL",
        datatype=bool,
    ),
    Config(
        "sbx_metadata.in_collections",
        default=[],
        description="List of material collections that this corpus is a part of",
        datatype=list,
    ),
    Config(
        "sbx_metadata.annotation",
        datatype=Dict[str, str],
        default={"swe": "", "eng": ""},
        description="Anything worth to note about the annotations in this corpus. Especially important for corpora "
        "with gold annotations.",
    ),
    Config(
        "sbx_metadata.keywords",
        default=[],
        description="List of keywords (in English) that may be used for filering. Keep them short!",
        datatype=List[str],
    ),
    Config(
        "sbx_metadata.caveats",
        default={"swe": "", "eng": ""},
        description="Caveats and disclaimers",
        datatype=Dict[str, str],
    ),
    Config(
        "sbx_metadata.creators",
        default=[],
        description="List of people that created the resource (format: lastname, firstname)",
        datatype=List[str],
    ),
    Config(
        "sbx_metadata.standard_reference",
        default="",
        description="A standard reference or link to a publication describing the resource",
        datatype=str,
    ),
    Config(
        "sbx_metadata.other_references",
        default=[],
        description="List of references or links to publications describing the resource",
        datatype=list,
    ),
    Config(
        "sbx_metadata.intended_uses",
        default={"swe": "", "eng": ""},
        description="The intended uses for this resource",
        datatype=Dict[str, str],
    ),
    Config(
        "sbx_metadata.yaml_export_host",
        "fksparv@bark.spraakdata.gu.se",
        description="Remote host to copy YAML metadata export to.",
    ),
    Config(
        "sbx_metadata.yaml_export_path",
        "/home/fksparv/metadata/yaml/corpus",
        description="Path on remote host to copy YAML metadata export to.",
    ),
    Config(
        "sbx_metadata.created",
        description="Corpus creation date (YYYY-MM-DD). Today's date will be used by default.",
        pattern=r"^\d{4}-\d{2}-\d{2}|$",
        default="",
        datatype=str,
    ),
    Config(
        "sbx_metadata.updated",
        description="Corpus update date (YYYY-MM-DD). Today's date will be used by default.",
        pattern=r"^\d{4}-\d{2}-\d{2}|$",
        default="",
        datatype=str,
    ),
]


@wizard(
    config_keys=[
        "sbx_metadata.xml_export",
        "sbx_metadata.stats_export",
        "sbx_metadata.korp",
        "sbx_metadata.trainingdata",
        "sbx_metadata.contact_info",
    ]
)
def setup_wizard(corpus_config: dict):
    """Return wizard steps for setting sbx-metadata variables."""
    # Set correct default value for contact information
    if corpus_config.get("sbx_metadata", {}).get("contact_info", "sbx-default") == "sbx-default":
        contact_default = {"value": "sbx-default", "name": "No, use the standard SBX contact info"}
    else:
        contact_default = {"value": {}, "name": "Yes"}

    return [
        {
            "type": "select",
            "name": "sbx_metadata.xml_export",
            "message": "Does this corpus have a public XML export?",
            "choices": [
                {"value": "scrambled", "name": "Yes, but the corpus will be scrambled"},
                {"value": "original", "name": "Yes, in its original order"},
                {"value": False, "name": "No"},
            ],
            "default": {"value": "scrambled", "name": "Yes, but the corpus will be scrambled"},
        },
        {
            "type": "select",
            "name": "sbx_metadata.stats_export",
            "message": "May the token frequency export be published for this corpus?",
            "choices": [{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
            "default": {"value": True, "name": "Yes"},
        },
        {
            "type": "select",
            "name": "sbx_metadata.korp",
            "message": "Will this corpus be published in Korp?",
            "choices": [{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
            "default": {"value": True, "name": "Yes"},
        },
        {
            "when": lambda x: x.get("sbx_metadata.korp") is True,
            "type": "checkbox",
            "name": "korp.modes",
            "message": "List of Korp modes that the corpus will be visible in:",
            "choices": [
                {"value": {"name": "default"}, "name": "Modern (default mode)", "checked": True},
                {"value": {"name": "parallel"}, "name": "Parallel"},
                {"value": {"name": "old_swedish"}, "name": "Old Swedish"},
                {"value": {"name": "lb"}, "name": "Litteraturbanken"},
                {"value": {"name": "kubhist"}, "name": "Kubhist"},
                {"value": {"name": "all_hist"}, "name": "Old texts"},
                {"value": {"name": "spf"}, "name": "Spf 1800–1900"},
                {"value": {"name": "fisk1800"}, "name": "Older Finland Swedish"},
                {"value": {"name": "faroe"}, "name": "Faroese"},
                {"value": {"name": "siberian_german"}, "name": "Siberian German"},
                {"value": {"name": "kioping_books"}, "name": "Kiöping's book of travel"},
                {"value": {"name": "runeberg"}, "name": "Runeberg journal"},
                {"value": {"name": "bible"}, "name": "Biblical texts"},
                {"value": {"name": "law"}, "name": "Habeas Corpus"},
                {"value": {"name": "spanish"}, "name": "Spanish"},
                {"value": {"name": "interfra"}, "name": "InterFra"},
                {"value": {"name": "bellman"}, "name": "Bellman's collected works"},
                {"value": {"name": "eddan"}, "name": "Poetic Edda"},
                {"value": {"name": "lsi"}, "name": "Linguistic Survey of India"},
                {"value": {"name": "dream"}, "name": "DReaM"},
                {"value": {"name": "somali"}, "name": "Somali"},
            ],
        },
        {
            "type": "select",
            "name": "sbx_metadata.trainingdata",
            "message": "Is this corpus intended to be used as trainingdata?",
            "choices": [{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
            "default": {"value": False, "name": "No"},
        },
        {
            "type": "select",
            "name": "sbx_metadata.contact_info",
            "message": "Do you want to appoint a contact person for this corpus?",
            "choices": [
                {"value": "sbx-default", "name": "No, use the standard SBX contact info"},
                {"value": {}, "name": "Yes"},
            ],
            "default": contact_default,
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.name",
            "message": "Name of contact person:",
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.email",
            "message": "Email address of contact person:",
            "validate": lambda x: bool(re.match(r"^\S+@+\S+\.\S+$", x.strip())),
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.affiliation.organisation",
            "message": "Name of the organisation the contact person is working for:",
            "default": {"value": "Språkbanken Text", "name": "Språkbanken Text"},
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.affiliation.email",
            "message": "Email address of the organisation the contact person is working for:",
            "default": {"value": "sb-info@svenska.gu.se", "name": "sb-info@svenska.gu.se"},
            "validate": lambda x: bool(re.match(r"^\S+@+\S+\.\S+$", x.strip())),
        },
    ]
