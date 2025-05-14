import os
import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid, extract_fulltext
from acdh_xml_pyutils.xml import NSMAP
from slugify import slugify


print("better listperson part II")

listperson_file = os.path.join("data", "indices", "listperson.xml")
org_doc = TeiReader("data/indices/listorg.xml")
lookup_dict = {}

for x in org_doc.any_xpath(".//tei:org"):
    xmlid = get_xmlid(x)
    label = x.xpath("./tei:orgName", namespaces=NSMAP)[0].text
    item = {
        "id": get_xmlid(x),
    }
    try:
        item["bomb_group"] = x.xpath("./tei:orgName", namespaces=NSMAP)[1].text
    except IndexError:
        item["bomb_group"] = None
    try:
        item["airforce"] = x.xpath("./tei:orgName", namespaces=NSMAP)[2].text
    except IndexError:
        item["airforce"] = None
    try:
        item["location"] = ET.tostring(
            x.xpath("./tei:location", namespaces=NSMAP)[0]
        ).decode("utf-8")
    except IndexError:
        item["location"] = None
    lookup_dict[label] = item

doc = TeiReader(listperson_file)

for x in doc.any_xpath(".//tei:person//tei:orgName"):
    label = extract_fulltext(x)
    try:
        match = lookup_dict[label]
    except KeyError:
        continue
    x.attrib["key"] = f"{match['id']}"
    if match["bomb_group"]:
        bg_label = match["bomb_group"]
        bg_key = slugify(bg_label)
        bomb_group_a = ET.Element(
            "{http://www.tei-c.org/ns/1.0}affiliation", attrib={"type": "bomb-group"}
        )
        bomb_group_org = ET.SubElement(
            bomb_group_a,
            "{http://www.tei-c.org/ns/1.0}orgName",
            attrib={"key": bg_key, "type": "bomb-group"},
        )
        bomb_group_org.text = bg_label
        x.getparent().getparent().append(bomb_group_a)
    if match["airforce"]:
        bg_label = match["airforce"]
        bg_key = slugify(bg_label)
        bomb_group_a = ET.Element(
            "{http://www.tei-c.org/ns/1.0}affiliation", attrib={"type": "airforce"}
        )
        bomb_group_org = ET.SubElement(
            bomb_group_a,
            "{http://www.tei-c.org/ns/1.0}orgName",
            attrib={"key": bg_key},
        )
        bomb_group_org.text = bg_label
        x.getparent().getparent().append(bomb_group_a)
    if match["location"]:
        x.getparent().append(ET.fromstring(match["location"]))
doc.tree_to_file(listperson_file)

place_lookup = {}
doc = TeiReader("./data/indices/listplace.xml")
for x in doc.any_xpath(".//tei:place[@xml:id]"):
    xmlid = get_xmlid(x)
    label = x.xpath("./tei:placeName", namespaces=NSMAP)[0].text
    item = {
        "id": get_xmlid(x),
    }
    place_lookup[label] = item
    try:
        item["location"] = ET.tostring(
            x.xpath("./tei:location", namespaces=NSMAP)[0]
        ).decode("utf-8")
    except IndexError:
        item["location"] = None
    place_lookup[label] = item

doc = TeiReader(listperson_file)
for x in doc.any_xpath(".//tei:person/tei:death/tei:placeName | .//tei:person/tei:birth/tei:placeName"):
    label = extract_fulltext(x)
    try:
        match = place_lookup[label]
    except KeyError:
        continue
    x.attrib["key"] = match["id"]
    if match["location"]:
        x.getparent().append(ET.fromstring(match["location"]))

doc.tree_to_file(listperson_file)
