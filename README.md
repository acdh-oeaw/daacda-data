# daadca-data

data was locally generated from https://daacda.acdh.oeaw.ac.at/ database and checked into this repo

to create index files run

```python
uv run organize_data.py
uv run create_listperson.py
uv run enrich_listperson.py
```


derives list*.xml files and moved them into `data/indices/*`
