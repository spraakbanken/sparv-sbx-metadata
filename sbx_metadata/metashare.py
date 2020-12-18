"""Export corpus metadata to META-SHARE format (SBX specific)."""

import os
import time
import xml.etree.ElementTree as etree

from iso639 import languages

from sparv import (AnnotationCommonData, Config, Export, ExportAnnotations, Model, ModelOutput, exporter, modelbuilder,
                   util)

logger = util.get_logger(__name__)

META_SHARE_URL = "http://www.ilsp.gr/META-XMLSchema"
META_SHARE_NAMESPACE = f"{{{META_SHARE_URL}}}"
SBX_SAMPLES_LOCATION = "https://spraakbanken.gu.se/en/resources/"
KORP_URL = "http://spraakbanken.gu.se/korp"
SBX_DEFAULT_CONTACT = {
    "surname": "Forsberg",
    "givenName": "Markus",
    "email": "sb-info@svenska.gu.se",
    "affiliation": {
        "organisation": "Språkbanken",
        "email": "sb-info@svenska.gu.se"
    }
}


@exporter("META-SHARE export of corpus metadata")
def metashare(out: Export = Export("sbx_metadata/[metadata.id].xml"),
              template: Model = Model("sbx_metadata/sbx-metashare-template.xml"),
              metadata: dict = Config("metadata"),
              sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
              tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
              annotations: list = Config("xml_export.annotations"),
              korp_protected: bool = Config("korp.protected"),
              korp_mode: bool = Config("korp.mode"),
              md_linguality: str = Config("sbx_metadata.linguality"),
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
        i.text = metadata["id"]
    identificationInfo.find(ns + "identifier").text = metadata["id"]
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
    _set_standard_xml_export(md_xml_export, metadata["id"], distInfo)
    _set_standard_stats_export(md_stats_export, metadata["id"], distInfo)
    _set_korp(md_korp, metadata["id"], korp_mode, distInfo)
    # Add non-standard licenseInfos
    _set_licence_info(md_downloads, distInfo)
    _set_licence_info(md_interface, distInfo, download=False)

    # Set contactPerson
    _set_contact_info(md_contact, xml.find(".//" + ns + "contactPerson"))

    # Set samplesLocation
    xml.find(".//" + ns + "samplesLocation").text = f"{SBX_SAMPLES_LOCATION}{metadata['id']}"

    # Set lingualityType
    xml.find(".//" + ns + "lingualityType").text = md_linguality

    # Set languageInfo (languageId, languageName, languageScript)
    lang = metadata["language"]
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

    # Write XML to file
    os.makedirs(os.path.dirname(out), exist_ok=True)
    etree.ElementTree(xml).write(out, encoding="unicode", method="xml", xml_declaration=True)
    logger.info("Exported: %s", out)


@modelbuilder("Download the SBX META-SHARE template")
def stanza_pos_model(model: ModelOutput = ModelOutput("sbx_metadata/sbx-metashare-template.xml")):
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
        # Create licenseInfo element
        licenseInfo = etree.Element(ns + "licenceInfo")
        licence = etree.SubElement(licenseInfo, ns + "licence")
        licence.text = item.get("licence", "CC-BY")
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
        util.indent_xml(licenseInfo, level=2)
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
        contact = SBX_DEFAULT_CONTACT

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


def _set_standard_xml_export(xml_export, corpus_id: str, distInfo):
    """Add license info for standard XML export."""
    if xml_export in ("scrambled", "original"):
        item = {
            "licence": "CC-BY",
            "restriction": "attribution",
            "download": f"http://spraakbanken.gu.se/lb/resurser/meningsmangder/{corpus_id}.xml.bz2",
            "type": "corpus",
            "format": "XML"
        }
        if xml_export == "scrambled":
            item["info"] = "this file contains a scrambled version of the corpus"
        _set_licence_info([item], distInfo)
    elif not xml_export:
        return
    else:
        raise util.SparvErrorMessage(f"Invalid config value for sbx_metadata.xml_export: '{xml_export}'. "
                                     "Possible values: 'scrambled', 'original', false")


def _set_standard_stats_export(stats_export: bool, corpus_id: str, distInfo):
    """Add license info for standard token stats export."""
    if stats_export:
        _set_licence_info(
            [{
                "licence": "CC-BY",
                "restriction": "attribution",
                "download": f"https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens/{corpus_id}.csv",
                "type": "token frequencies",
                "format": "CSV"
            }], distInfo)


def _set_korp(korp: bool, corpus_id: str, korp_mode, distInfo):
    """Add license info for standard Korp interface."""
    if korp:
        item = {"licence": "other",
                "restriction": "other"}
        if korp_mode == "modern":
            item["access"] = f"{KORP_URL}/#?corpus={corpus_id}"
        else:
            item["access"] = f"{KORP_URL}/?mode={korp_mode}#corpus={corpus_id}"
        _set_licence_info([item], distInfo, download=False)


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

    #TODO: How do we know whether annotation was done automatically or manually?
    #TODO: What if annotations contain explicit annotations instead of classes?
    if any("<token>" in a for a in annotations) or any("<sentence>" in a for a in annotations):
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "segmentation"
        if any("<sentence>" in a for a in annotations):
            segmentationLevel = etree.SubElement(annotationInfo, ns + "segmentationLevel")
            segmentationLevel.text = "sentence"
        if any("<token>" in a for a in annotations):
            segmentationLevel = etree.SubElement(annotationInfo, ns + "segmentationLevel")
            segmentationLevel.text = "word"
        append_rest(corpusTextInfo, annotationInfo)

    if any("<baseform>" in a for a in annotations):
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "lemmatization"
        append_rest(corpusTextInfo, annotationInfo)

    if any("<pos>" in a for a in annotations):
        annotationInfo = etree.Element(ns + "annotationInfo")
        annotationType = etree.SubElement(annotationInfo, ns + "annotationType")
        annotationType.text = "morphosyntacticAnnotation-posTagging"
        append_rest(corpusTextInfo, annotationInfo)


def _append_pretty(parent, child):
    """Append child to parent and hack indentation."""
    # Calculate indentation level for child (NB: works only if child has siblings!)
    level = int(len((parent.getchildren()[-1].tail).strip("\n")) / 2 + 1)
    util.indent_xml(child, level)
    parent.getchildren()[-1].tail = "\n" + "  " * level
    child.tail = "\n" + "  " * (level - 1)
    parent.append(child)
