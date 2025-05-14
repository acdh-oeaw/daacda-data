#!/bin/bash

uv run organize_data.py
uv run create_listperson.py
uv run enrich_listperson.py