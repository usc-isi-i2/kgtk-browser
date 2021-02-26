# Example KGTK browser configuration

# location of a KGTK graph cache (for now we assume Wikidata):
DB_GRAPH_CACHE        = './wikidataos-v4.sqlite3.db'
DB_INDEX_MODE         = 'none'

# input file names or aliases for various aspects of the KG we are working with:
DB_EDGES_GRAPH        = 'claims'
DB_QUALIFIERS_GRAPH   = 'qualifiers'
DB_LABELS_GRAPH       = 'labels'
DB_ALIASES_GRAPH      = 'aliases'
DB_DESCRIPTIONS_GRAPH = 'descriptions'
