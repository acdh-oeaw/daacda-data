#!/bin/bash

uv run organize_data.py
uv run create_listperson.py
uv run enrich_listperson.py

add-attributes -g "./data/editions/*.xml" -b "https://daacda.acdh.oeaw.ac.at"
add-attributes -g "./data/meta/*.xml" -b "https://daacda.acdh.oeaw.ac.at"
add-attributes -g "./data/indices/*.xml" -b "https://daacda.acdh.oeaw.ac.at"
