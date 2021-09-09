#! /bin/tcsh

echo "Exporting the claims"
time kgtk query -i claims --graph-cache wikidata.sqlite3.db  --out wikidata.claims.tsv.gz

echo "Exporting the labels"
time kgtk query -i labels --graph-cache wikidata.sqlite3.db  --out wikidata.labels.tsv.gz

echo "Exporting the aliases"
time kgtk query -i aliases --graph-cache wikidata.sqlite3.db  --out wikidata.aliases.tsv.gz

echo "Exporting the descriptions"
time kgtk query -i descriptions --graph-cache wikidata.sqlite3.db  --out wikidata.descriptions.tsv.gz

echo "Exporting the qualifiers"
time kgtk query -i qualifiers --graph-cache wikidata.sqlite3.db  --out wikidata.qualifiers.tsv.gz

echo "Exporting the metadata"
time kgtk query -i metadata --graph-cache wikidata.sqlite3.db  --out wikidata.metadata.tsv.gz
