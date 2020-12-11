"""Export corpus metadata to META-SHARE format (SBX specific)."""

import os
import time
import xml.etree.ElementTree as etree

from sparv import AnnotationCommonData, Config, Export, Model, ModelOutput, exporter, modelbuilder, util

logger = util.get_logger(__name__)

META_SHARE_URL = "http://www.ilsp.gr/META-XMLSchema"
META_SHARE_NAMESPACE = f"{{{META_SHARE_URL}}}"
SBX_SAMPLES_LOCATION = "https://spraakbanken.gu.se/en/resources/"


@exporter("META-SHARE export of corpus metadata")
def metashare(out: Export = Export("sbx_metadata/[metadata.id].xml"),
              template: Model = Model("sbx_metadata/sbx-metashare-template.xml"),
              metadata: dict = Config("metadata"),
              sentences: AnnotationCommonData = AnnotationCommonData("misc.<sentence>_count"),
              tokens: AnnotationCommonData = AnnotationCommonData("misc.<token>_count"),
              md_language: str = Config("sbx_metadata.language_name"),
              md_linguality: str = Config("sbx_metadata.linguality"),
              md_script: str = Config("sbx_metadata.script"),
              protected: bool = Config("korp.protected"),
              md_downloads: list = Config("sbx_metadata.downloads"),
              md_interface: list = Config("sbx_metadata.interface"),
              md_contact: dict = Config("sbx_metadata.contact_info")
              ):
    """Export corpus metadata to META-SHARE format."""
    # Create export dir
    os.makedirs(os.path.dirname(out), exist_ok=True)

    xml = etree.parse(template.path).getroot()

    # Prevent etree from printing namespaces in the resulting xml file
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
    xml.find(".//" + ns + "availability").text = "available-restrictedUse" if protected else "available-unrestrictedUse"

    # Set licenceInfos
    # TODO: standard locations for meningsmängder and stats?
    distInfo = xml.find(".//" + ns + "distributionInfo")
    _set_licence_info(md_downloads, distInfo)
    # TODO: automatically generate Korp link? How to handle modes?
    _set_licence_info(md_interface, distInfo, download=False)

    # Set contactPerson
    _set_contact_info(md_contact, xml.find(".//" + ns + "contactPerson"))

    # Set samplesLocation
    xml.find(".//" + ns + "samplesLocation").text = f"{SBX_SAMPLES_LOCATION}{metadata['id']}"

    # Set lingualityType
    xml.find(".//" + ns + "lingualityType").text = md_linguality

    # Set languageInfo (languageId, languageName, languageScript)
    xml.find(".//" + ns + "languageId").text = metadata["language"]
    xml.find(".//" + ns + "languageName").text = md_language.get("language_name", {}).get("eng", "Swedish")
    xml.find(".//" + ns + "languageScript").text = md_script

    # Set sizeInfo
    sizeInfos = xml.findall(".//" + ns + "sizeInfo")
    sizeInfos[0].find(ns + "size").text = tokens.read()
    sizeInfos[1].find(ns + "size").text = sentences.read()

    # TODO: Set annotationInfo. Make dependent on sentence, token, baseform and pos class!

    # Write XML to file
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
        # Prettify element
        util.indent_xml(affiliation, level=2)
        # More indentation hacking
        contactPerson.find(ns + "communicationInfo").tail = contactPerson.find(ns + "communicationInfo").tail + "  "
        affiliation.tail = "\n  "

        contactPerson.append(affiliation)
