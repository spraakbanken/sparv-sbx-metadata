"""Metadata export (SBX specific)."""

import re

from sparv.api import Config, wizard

from . import json_export, metashare

__config__ = [
    Config("sbx_metadata.script", default="Latn",
           description="Writing system used to represent the language of the corpus (ISO-15924)"),
    # Config("sbx_metadata.linguality", default="monolingual", description="Indicates whether the corpus includes"
    #        "one, two or more languages (monolingual, bilingual or multilingual)"),
    Config("sbx_metadata.xml_export", default="scrambled", description="Whether XML export may be published."
           "Values: scrambled, original, false"),
    Config("sbx_metadata.stats_export", default=True, description="Whether token frequency export may be published"),
    Config("sbx_metadata.korp", default=True, description="Whether the corpus will be published in Korp"),
    Config("sbx_metadata.downloads", default=[], description="Downloadable files belonging to the corpus"),
    Config("sbx_metadata.interface", default=[], description="List of interfaces where the corpus is available"),
    Config("sbx_metadata.contact_info", default="sbx-default",
           description="Object containing information about the contact person"
           "for the resource"),
    Config("sbx_metadata.trainingdata", default=False, description="Whether the corpus is intended as training data"),
    Config("sbx_metadata.in_collections", default=False,
           description="List of material collections that this corpus is a part of"),
    Config("sbx_metadata.metashare_host", "fksparv@bark.spraakdata.gu.se",
           description="Remote host to copy META-SHARE export to."),
    Config("sbx_metadata.metashare_path", "/home/fksparv/metadata/meta-share/corpus",
           description="Path on remote host to copy META-SHARE export to."),
    Config("sbx_metadata.json_export_host", "fksparv@bark.spraakdata.gu.se",
           description="Remote host to copy JSON metadata export to."),
    Config("sbx_metadata.json_export_path", "/home/fksparv/metadata/json/corpus",
           description="Path on remote host to copy JSON metadata export to.")
]


@wizard(config_keys=[
    "sbx_metadata.xml_export",
    "sbx_metadata.stats_export",
    "sbx_metadata.korp",
    "sbx_metadata.trainingdata",
    "sbx_metadata.contact_info",
])
def setup_wizard(corpus_config: dict):
    """Return wizard steps for setting sbx-metadata variables."""
    # Set correct default value for contact information
    if corpus_config.get("sbx_metadata", {}).get("contact_info", "sbx-default") == "sbx-default":
        contact_default = {"value": "sbx-default", "name": "No, use the standard SBX contact info"}
    else:
        contact_default = {"value": {}, "name": "Yes"}

    questions = [
        {
            "type": "select",
            "name": "sbx_metadata.xml_export",
            "message": "Does this corpus have a public XML export?",
            "choices": [{"value": "scrambled", "name": "Yes, but the corpus will be scrambled"},
                        {"value": "original", "name": "Yes, in its original order"},
                        {"value": False, "name": "No"}],
            "default": {"value": "scrambled", "name": "Yes, but the corpus will be scrambled"}
        },
        {
            "type": "select",
            "name": "sbx_metadata.stats_export",
            "message": "May the token frequency export be published for this corpus?",
            "choices": [{"value": True, "name": "Yes"},
                        {"value": False, "name": "No"}],
            "default": {"value": True, "name": "Yes"}
        },
        {
            "type": "select",
            "name": "sbx_metadata.korp",
            "message": "Will this corpus be published in Korp?",
            "choices": [{"value": True, "name": "Yes"},
                        {"value": False, "name": "No"}],
            "default": {"value": True, "name": "Yes"}
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
                        {"value": {"name": "somali"}, "name": "Somali"}]
        },
        {
            "type": "select",
            "name": "sbx_metadata.trainingdata",
            "message": "Is this corpus intended to be used as trainingdata?",
            "choices": [{"value": True, "name": "Yes"},
                        {"value": False, "name": "No"}],
            "default": {"value": False, "name": "No"}
        },
        {
            "type": "select",
            "name": "sbx_metadata.contact_info",
            "message": "Do you want to appoint a contact person for this corpus?",
            "choices": [{"value": "sbx-default", "name": "No, use the standard SBX contact info"},
                        {"value": {}, "name": "Yes"}],
            "default": contact_default
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.givenName",
            "message": "First name of contact person:"
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.surname",
            "message": "Surname of contact person:"
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.email",
            "message": "Email address of contact person:",
            "validate": lambda x: bool(re.match(r"^\S+@+\S+\.\S+$", x.strip()))
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.affiliation.organisation",
            "message": "Name of the organisation the contact person is working for:",
            "default": {"value": "Språkbanken", "name": "Språkbanken"}
        },
        {
            "when": lambda x: x.get("sbx_metadata.contact_info") != "sbx-default",
            "type": "text",
            "name": "sbx_metadata.contact_info.affiliation.email",
            "message": "Email address of the organisation the contact person is working for:",
            "default": {"value": "sb-info@svenska.gu.se", "name": "sb-info@svenska.gu.se"},
            "validate": lambda x: bool(re.match(r"^\S+@+\S+\.\S+$", x.strip()))
        }
    ]
    return questions
