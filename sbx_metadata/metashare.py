"""Export corpus metadata to META-SHARE format (SBX specific)."""

import io
import os
import time
import xml.etree.ElementTree as etree
from pathlib import Path

from iso639 import languages
from sparv.api import (AnnotationCommonData, Config, Corpus, Export, ExportAnnotations, ExportInput, Language, Model,
                       ModelOutput, OutputCommonData, SparvErrorMessage, exporter, get_logger, installer, modelbuilder,
                       util)

from . import metadata_utils

logger = get_logger(__name__)

META_SHARE_URL = "http://www.ilsp.gr/META-XMLSchema"
META_SHARE_NAMESPACE = f"{{{META_SHARE_URL}}}"
SBX_SAMPLES_LOCATION = "https://spraakbanken.gu.se/en/resources/"

AUTO_TOKEN = ["segment.token", "stanza.token", "freeling.token", "stanford.token"]
AUTO_SENT = ["segment.sentence", "stanza.sentence", "freeling.sentence", "stanfort.sentence"]
AUTO_POS = ["hunpos.pos", "hunpos.msd", "hunpos.msd_hist", "hist.homograph_set", "stanza.pos", "stanza.msd",
            "stanza.upos", "misc.upos", "flair.pos", "flair.msd", "freeling.pos", "stanford.pos"]
AUTO_BASEFORM = ["saldo.baseform", "hist.baseform", "freeling.baseform", "treetagger.baseform", "stanford.baseform"]


@exporter("META-SHARE export of corpus metadata")
def metashare(out: Export = Export("sbx_metadata/[metadata.id].xml"),
              template: Model = Model("sbx_metadata/sbx-metashare-template.xml"),
              corpus_id: Corpus = Corpus(),
              lang: Language = Language(),
              metadata: dict = Config("metadata"),
              sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
              tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
              annotations: ExportAnnotations = ExportAnnotations("xml_export.annotations", is_input=False),
              korp_protected: bool = Config("korp.protected"),
              korp_mode: bool = Config("korp.mode"),
              # md_linguality: str = Config("sbx_metadata.linguality"),
              md_script: str = Config("sbx_metadata.script"),
              md_xml_export: str = Config("sbx_metadata.xml_export"),
              md_stats_export: bool = Config("sbx_metadata.stats_export"),
              md_korp: bool = Config("sbx_metadata.korp"),
              md_downloads: list = Config("sbx_metadata.downloads"),
              md_interface: list = Config("sbx_metadata.interface"),
              md_contact: dict = Config("sbx_metadata.contact_info")):
    """Export corpus metadata to META-SHARE format."""
    # Parse template and handle META SHARE namespace
    xml = etree.parse(template.path).getroot()
    etree.register_namespace("", META_SHARE_URL)
    ns = META_SHARE_NAMESPACE

    # Set idenfification info
    identificationInfo = xml.find(ns + "identificationInfo")
    for i in identificationInfo.findall(ns + "resourceShortName"):
        i.text = corpus_id
    identificationInfo.find(ns + "identifier").text = corpus_id
    _set_texts(identificationInfo.findall(ns + "resourceName"), metadata.get("name", {}))
    _set_texts(identificationInfo.findall(ns + "description"), metadata.get("description", {}))

    # Set metadata creation date in metadataInfo
    xml.find(".//" + ns + "metadataCreationDate").text = str(time.strftime("%Y-%m-%d"))

    # Set availability
    if korp_protected:
        xml.find(".//" + ns + "availability").text = "available-restrictedUse"
    else:
        xml.find(".//" + ns + "availability").text = "available-unrestrictedUse"

    # Set licenceInfos
    distInfo = xml.find(".//" + ns + "distributionInfo")
    _set_licence_info([metadata_utils.make_standard_xml_export(md_xml_export, corpus_id)], distInfo)
    _set_licence_info([metadata_utils.make_standard_stats_export(md_stats_export, corpus_id)], distInfo)
    _set_licence_info([metadata_utils.make_korp(md_korp, corpus_id, korp_mode)], distInfo, download=False)
    _set_licence_info([metadata_utils.make_metashare(corpus_id)], distInfo)
    # Add non-standard licenseInfos
    _set_licence_info(md_downloads, distInfo)
    _set_licence_info(md_interface, distInfo, download=False)

    # Set contactPerson
    _set_contact_info(md_contact, xml.find(".//" + ns + "contactPerson"))

    # Set samplesLocation
    xml.find(".//" + ns + "samplesLocation").text = f"{SBX_SAMPLES_LOCATION}{corpus_id}"

    # Set lingualityType
    xml.find(".//" + ns + "lingualityType").text = "monolingual"

    # Set languageInfo (languageId, languageName, languageScript)
    xml.find(".//" + ns + "languageId").text = lang
    xml.find(".//" + ns + "languageName").text = languages.get(part3=lang).name if lang in languages.part3 else lang
    xml.find(".//" + ns + "languageScript").text = md_script

    # Set sizeInfo
    sizeInfos = xml.findall(".//" + ns + "sizeInfo")
    sizeInfos[0].find(ns + "size").text = tokens.read()
    sizeInfos[1].find(ns + "size").text = sentences.read()

    # Set annotationInfo
    corpusTextInfo = xml.find(".//" + ns + "corpusTextInfo")
    _set_annotation_info(annotations, corpusTextInfo)

    # Dump XML and hack in Sparv comment (etree cannot do this for us :( )
    # We use write() instead of tostring() here to be able to get an XML declaration in Python 3.6
    stream = io.StringIO()
    etree.ElementTree(xml).write(stream, encoding="unicode", method="xml", xml_declaration=True)
    xml_string = stream.getvalue()
    xml_lines = xml_string.split("\n")
    xml_lines.insert(1, "<!-- This file was automatically generated by Sparv. Do not make changes directly to this file"
                     " as they will get overwritten. -->")

    # Write XML to file
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, mode="w") as outfile:
        outfile.write("\n".join(xml_lines))
    logger.info("Exported: %s", out)


@installer("Copy META-SHARE file to remote host")
def install_metashare(xmlfile: ExportInput = ExportInput("sbx_metadata/[metadata.id].xml"),
                      out: OutputCommonData = OutputCommonData("sbx_metadata.install_metashare_marker"),
                      export_path: str = Config("sbx_metadata.metashare_path"),
                      host: str = Config("sbx_metadata.metashare_host")):
    """Copy META-SHARE file to remote host."""
    if not host:
        raise SparvErrorMessage("'sbx_metadata.metashare_host' not set! META-SHARE export not installed.")
    filename = Path(xmlfile).name
    remote_file_path = os.path.join(export_path, filename)
    util.install.install_file(xmlfile, host, remote_file_path)
    out.write("")


@modelbuilder("Download the SBX META-SHARE template")
def metashare_template(model: ModelOutput = ModelOutput("sbx_metadata/sbx-metashare-template.xml")):
    """Download the SBX META-SHARE template."""
    model.download("https://raw.githubusercontent.com/spraakbanken/sparv-sbx-metadata/main/data/sbx-metashare-template.xml")


def _set_texts(elems, yaml_elem):
    """Set texts for elems to value in yaml_elem and respect language."""
    for i in elems:
        if i.attrib["lang"] == "eng":
            i.text = yaml_elem.get("eng", "")
        if i.attrib["lang"] == "swe":
            i.text = yaml_elem.get("swe", "")


def _set_licence_info(items, distInfo, download=True):
    """Create licenceInfo trees for each item and append them to distInfo."""
    ns = META_SHARE_NAMESPACE
    for item in items:
        if item is None:
            continue
        # Create licenseInfo element
        licenseInfo = etree.Element(ns + "licenceInfo")
        licence = etree.SubElement(licenseInfo, ns + "licence")
        licence.text = item.get("licence", metadata_utils.STANDARD_LICENSE)
        restrictionsOfUse = etree.SubElement(licenseInfo, ns + "restrictionsOfUse")
        restrictionsOfUse.text = item.get("restriction", "attribution")
        if download:
            distributionAccessMedium = etree.SubElement(licenseInfo, ns + "distributionAccessMedium")
            distributionAccessMedium.text = "downloadable"
            downloadLocation = etree.SubElement(licenseInfo, ns + "downloadLocation")
            downloadLocation.text = item.get("download", "")
        else:
            distributionAccessMedium = etree.SubElement(licenseInfo, ns + "distributionAccessMedium")
            distributionAccessMedium.text = "accessibleThroughInterface"
            executionLocation = etree.SubElement(licenseInfo, ns + "executionLocation")
            executionLocation.text = item.get("access", "")
        if item.get("info", None):
            attributionText = etree.SubElement(licenseInfo, ns + "attributionText")
            attributionText.text = item.get("info", "")
        # Prettify element
        util.misc.indent_xml(licenseInfo, level=2)
        # Insert in position 1 or after last licenceInfo
        if distInfo.find(ns + "licenceInfo") is None:
            distInfo.insert(1, licenseInfo)
        else:
            # Get index of last licenceInfo
            i = distInfo.getchildren().index(distInfo.findall(ns + "licenceInfo")[-1])
            distInfo.insert(i + 1, licenseInfo)


def _set_contact_info(contact, contactPerson):
    """Set contact info in contactPerson element."""
    if contact == "sbx-default":
        contact = metadata_utils.SBX_DEFAULT_CONTACT

    ns = META_SHARE_NAMESPACE
    contactPerson.find(ns + "surname").text = contact.get("surname", "")
    contactPerson.find(ns + "givenName").text = contact.get("givenName", "")
    contactPerson.find(ns + "communicationInfo" + "/" + ns + "email").text = contact.get("email", "")
    # Create affiliation element if needed
    if contact.get("affiliation") and any(i in contact.get("affiliation", {}) for i in ["organisation", "email"]):
        affiliation = etree.Element(ns + "affiliation")
        if contact["affiliation"].get("organisation"):
            organizationName = etree.SubElement(affiliation, ns + "organizationName")
            organizationName.text = contact["affiliation"].get("organisation", "")
        if contact["affiliation"].get("email"):
            communicationInfo = etree.SubElement(affiliation, ns + "communicationInfo")
            email = etree.SubElement(communicationInfo, ns + "email")
            email.text = contact["affiliation"].get("email", "")
        _append_pretty(contactPerson, affiliation)


def _set_annotation_info(annotations, corpusTextInfo):
    """Set annotationInfo dependent on sentence, token, baseform and pos class."""
    ns = META_SHARE_NAMESPACE

    def append_rest(corpusTextInfo, annotationInfo, auto=True):
        """Append the stuff that occurs in all annotationInfos."""
        annotationFormat = etree.SubElement(annotationInfo, ns + "annotationFormat")
        annotationFormat.text = "text/xml"
        annotationMode = etree.SubElement(annotationInfo, ns + "annotationMode")
        annotationMode.text = "automatic" if auto else "manual"
        _append_pretty(corpusTextInfo, annotationInfo)

    #TODO: We do not know anything about manual annotations since we don't know the classes of input annotations.
    annotations = [a.name for a, _ in annotations]
    auto_token = any(x for x in AUTO_TOKEN if [a for a in annotations if x in a])
    auto_sent = any(x for x in AUTO_SENT if [a for a in annotations if x in a])
    auto_baseform = any(x for x in AUTO_BASEFORM if [a for a in annotations if x in a])
    auto_pos = any(x for x in AUTO_POS if [a for a in annotations if x in a])

    if auto_token or auto_sent:
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "segmentation"
        if auto_sent:
            segmentationLevel = etree.SubElement(annotationInfo, ns + "segmentationLevel")
            segmentationLevel.text = "sentence"
        if auto_token:
            segmentationLevel = etree.SubElement(annotationInfo, ns + "segmentationLevel")
            segmentationLevel.text = "word"
        append_rest(corpusTextInfo, annotationInfo, auto=True)

    if auto_baseform:
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "lemmatization"
        append_rest(corpusTextInfo, annotationInfo, auto=True)

    if auto_pos:
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "morphosyntacticAnnotation-posTagging"
        append_rest(corpusTextInfo, annotationInfo, auto=True)


def _append_pretty(parent, child):
    """Append child to parent and hack indentation."""
    # Calculate indentation level for child (NB: works only if child has siblings!)
    level = int(len((parent.getchildren()[-1].tail).strip("\n")) / 2 + 1)
    util.misc.indent_xml(child, level)
    parent.getchildren()[-1].tail = "\n" + "  " * level
    child.tail = "\n" + "  " * (level - 1)
    parent.append(child)
