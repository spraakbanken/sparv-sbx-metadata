"""Metadata export (SBX specific)."""

from sparv import Config

from . import metashare, json_export

__config__ = [
    Config("sbx_metadata.script", default="Latn",
           description="Writing system used to represent the language of the corpus (ISO-15924)"),
    # Config("sbx_metadata.linguality", default="monolingual", description="Indicates whether the corpus includes"
    #        "one, two or more languages (monolingual, bilingual or multilingual)"),
    Config("sbx_metadata.xml_export", default=False, description="Whether XML export may be published."
           "Values: scrambled, original, false"),
    Config("sbx_metadata.stats_export", default=False, description="Whether token frequency export may be published"),
    Config("sbx_metadata.korp", default=True, description="Whether the corpus will be published in Korp"),
    Config("sbx_metadata.downloads", default=[], description="Downloadable files belonging to the corpus"),
    Config("sbx_metadata.interface", default=[], description="List of interfaces where the corpus is available"),
    Config("sbx_metadata.contact_info", default="sbx-default", description="Object containing information about the contact person"
           "for the resource"),
    Config("sbx_metadata.trainingdata", default=False, description="Whether the corpus is intended as training data"),
    Config("sbx_metadata.metashare_host", "bark", description="Remote host to copy META-SHARE export to."),
    Config("sbx_metadata.metashare_path", "/home/fksparv/sb-metadata/meta-share/corpus",
           description="Path on remote host to copy META-SHARE export to."),
    Config("sbx_metadata.json_export_host", "bark", description="Remote host to copy JSON metadata export to."),
    Config("sbx_metadata.json_export_path", "/home/fksparv/sb-metadata/json/corpus",
           description="Path on remote host to copy JSON metadata export to.")
]
