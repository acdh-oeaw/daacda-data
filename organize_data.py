import glob
import os
import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid


print("make basic index files")


editions = os.path.join("data", "editions")
indices = os.path.join("data", "indices")
os.makedirs(editions, exist_ok=True)
os.makedirs(indices, exist_ok=True)

files = sorted(glob.glob("./data/editions/*.xml"))
template = "tei_template.xml"

person_nodes = {}
place_nodes = {}
org_nodes = {}
for x in files:
    doc = TeiReader(x)
    for y in doc.any_xpath(".//tei:person[@xml:id]"):
        xmlid = get_xmlid(y)
        person_nodes[xmlid] = y
    for y in doc.any_xpath(".//tei:org[@xml:id]"):
        xmlid = get_xmlid(y)
        org_nodes[xmlid] = y
    for y in doc.any_xpath(".//tei:place[@xml:id]"):
        xmlid = get_xmlid(y)
        place_nodes[xmlid] = y

doc = TeiReader(template)
title = doc.any_xpath(".//tei:title[1]")[0]
title.text = "Index of persons"
body = doc.any_xpath(".//tei:body")[0]
list_nodes = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
for key, value in person_nodes.items():
    list_nodes.append(value)
body.append(list_nodes)

doc.tree_to_file(os.path.join(indices, "listperson.xml"))

doc = TeiReader(template)
title = doc.any_xpath(".//tei:title[1]")[0]
title.text = "Index of places"
body = doc.any_xpath(".//tei:body")[0]
list_nodes = ET.Element("{http://www.tei-c.org/ns/1.0}listPlace")
for key, value in place_nodes.items():
    list_nodes.append(value)
body.append(list_nodes)

doc.tree_to_file(os.path.join(indices, "listplace.xml"))


doc = TeiReader(template)
title = doc.any_xpath(".//tei:title[1]")[0]
title.text = "Index of Organisations"
body = doc.any_xpath(".//tei:body")[0]
list_nodes = ET.Element("{http://www.tei-c.org/ns/1.0}listOrg")
for key, value in org_nodes.items():
    list_nodes.append(value)
body.append(list_nodes)

doc.tree_to_file(os.path.join(indices, "listorg.xml"))
