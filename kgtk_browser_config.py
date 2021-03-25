# Example KGTK browser configuration

# location of a KGTK graph cache (for now we assume Wikidata):
DB_GRAPH_CACHE        = './wikidata-20210215-dwd-browser.sqlite3.db'
#DB_GRAPH_CACHE        = './wikidataos-v4.sqlite3.db'
DB_LOG_LEVEL          = 1

# input file names (or aliases) for various aspects of the KG:
DB_EDGES_GRAPH        = 'claims'
DB_QUALIFIERS_GRAPH   = 'qualifiers'
DB_LABELS_GRAPH       = 'labels'
DB_ALIASES_GRAPH      = 'aliases'
DB_DESCRIPTIONS_GRAPH = 'descriptions'
DB_IMAGES_GRAPH       = 'claims'
DB_FANOUTS_GRAPH      = 'metadata'

# edge labels for various specific info we are retrieving
# (TO DO: generalize this towards full-fledged queries):
DB_LABELS_LABEL       = 'label'
DB_ALIASES_LABEL      = 'alias'
DB_DESCRIPTIONS_LABEL = 'description'
DB_IMAGES_LABEL       = 'P18'
DB_FANOUTS_LABEL      = 'count_distinct_properties'
