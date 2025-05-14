import glob
import os
import lxml.etree as ET
from tqdm import tqdm
from slugify import slugify
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext, get_xmlid
from acdh_xml_pyutils.xml import NSMAP as nsmap

print("better listperson part I")

listperson_file = os.path.join("data", "indices", "listperson.xml")
files = sorted(glob.glob("data/editions/*.xml"))
data = {}
for x in tqdm(files):
    doc = TeiReader(x)
    try:
        marc_id = extract_fulltext(
            doc.any_xpath(
                ".//tei:table[@xml:id='bomber_table']/tei:row[@role='data']/tei:cell"
            )[0]
        )
    except IndexError:
        marc_id = "not provided"
    try:
        squad = extract_fulltext(
            doc.any_xpath(
                ".//tei:table[@xml:id='bomber_table']/tei:row[@role='data']/tei:cell"
            )[4]
        )
    except:
        squad = "not provided"
    labels = doc.any_xpath(
        ".//tei:table[@xml:id='crew_table']/tei:row[@role='label']//tei:cell"
    )
    relation_labels = doc.any_xpath(
        ".//tei:cell/tei:table/tei:row[@role='label'][1]//tei:cell"
    )
    for crew in doc.any_xpath(
        ".//tei:table[@xml:id='crew_table']/tei:row[@role='data']"
    ):
        item = {}
        item["marc-id"] = marc_id
        item["squad"] = squad
        for i, y in enumerate(crew.xpath("./tei:cell", namespaces=nsmap)[:9]):
            abbr = slugify(
                extract_fulltext(labels[i].xpath(".//tei:abbr", namespaces=nsmap)[0])
            )
            item[abbr] = extract_fulltext(y)
        stations = []
        for n, z in enumerate(crew.xpath(".//tei:row[@role='data']", namespaces=nsmap)):
            station_data = {}
            for i, y in enumerate(z.xpath("./tei:cell", namespaces=nsmap)):
                station_abbr = slugify(
                    extract_fulltext(
                        relation_labels[i].xpath(".//tei:abbr", namespaces=nsmap)[0]
                    )
                )
                station_data[station_abbr] = extract_fulltext(y)
            stations.append(station_data)
        item["stations"] = stations
        xmlid = item["interne-id"]
        data[f"person__{xmlid}"] = item
    for x in doc.any_xpath(".//tei:person[@xml:id]"):
        xmlid = get_xmlid(x)

        occupation = ET.SubElement(x, "{http://www.tei-c.org/ns/1.0}occupation")
        occupation.text = data[xmlid]["funktion-im-flugzeug"]
        if data[xmlid]["dienstgrad"]:
            occupation.attrib["role"] = data[xmlid]["dienstgrad"]

        affiliation = ET.SubElement(
            x, "{http://www.tei-c.org/ns/1.0}affiliation", attrib={"type": "squad"}
        )
        org_name = ET.SubElement(affiliation, "{http://www.tei-c.org/ns/1.0}orgName")
        org_name.text = data[xmlid]["squad"]

        idno = ET.SubElement(
            x, "{http://www.tei-c.org/ns/1.0}idno", attrib={"type": "marc-id"}
        )
        idno.text = data[xmlid]["marc-id"]

        idno = ET.SubElement(
            x, "{http://www.tei-c.org/ns/1.0}idno", attrib={"type": "dog-tag"}
        )
        idno.text = data[xmlid]["kennnummer"]

        note = ET.SubElement(
            x, "{http://www.tei-c.org/ns/1.0}note", attrib={"type": "eintrag-macr"}
        )
        note.text = data[xmlid]["eintrag-macr"]

        note = ET.SubElement(
            x, "{http://www.tei-c.org/ns/1.0}note", attrib={"type": "schicksal"}
        )
        note.text = data[xmlid]["schicksal"]

        for event in data[xmlid]["stations"]:
            if event["art-der-verbindung"] == "starb in":
                death = ET.SubElement(x, "{http://www.tei-c.org/ns/1.0}death")
                if event["von"]:
                    death_date = ET.SubElement(
                        death, "{http://www.tei-c.org/ns/1.0}date"
                    )
                    death_date.attrib["when-iso"] = event["von"]
                    death_date.text = event["von"]
                if event["ort"]:
                    place = ET.SubElement(
                        death, "{http://www.tei-c.org/ns/1.0}placeName"
                    )
                    place.text = event["ort"]
            if (
                event["art-der-verbindung"] == "wurde inhaftiert in"
                and event["institution"]
            ):
                residence = ET.SubElement(
                    x,
                    "{http://www.tei-c.org/ns/1.0}residence",
                    attrib={"type": "prison"},
                )
                org_name = ET.SubElement(
                    residence, "{http://www.tei-c.org/ns/1.0}orgName"
                )
                org_name.text = event["institution"]
                if event["von"] != "":
                    residence.attrib["from-iso"] = event["von"]
                    residence.text = event["von"]
                if event["bis"] != "":
                    residence.attrib["from-iso"] = event["bis"]
                    residence.text = event["bis"]

        try:
            data[xmlid]["node"] = x
        except KeyError:
            print(f"upsi daisy; {xmlid} is missing")

doc = TeiReader(listperson_file)

for x in doc.any_xpath(".//tei:person[@xml:id]"):
    x.getparent().remove(x)

list_person = doc.any_xpath(".//tei:listPerson")[0]

for key, value in data.items():
    list_person.append(value["node"])

doc.tree_to_file(listperson_file)
