# KGTK browser configuration
import json

# Basic configuration section:

VERSION = '0.1.0'
GRAPH_ID = 'my-knowledge-graph'
GRAPH_CACHE = './wikidata.sqlite3.db'
LOG_LEVEL = 0
INDEX_MODE = 'auto'
MAX_RESULTS = 10000
MAX_CACHE_SIZE = 1000
DEFAULT_LANGUAGE = 'en'

# input names for various aspects of the KG referenced in query section below:
KG_EDGES_GRAPH = 'claims'
KG_QUALIFIERS_GRAPH = 'qualifiers'
KG_LABELS_GRAPH = 'label'
KG_ALIASES_GRAPH = 'alias'
KG_DESCRIPTIONS_GRAPH = 'description'
KG_IMAGES_GRAPH = 'claims'
KG_FANOUTS_GRAPH = 'datatypes'
KG_DATATYPES_GRAPH = 'datatypes'

# edge labels for various edges referenced in query section below:
KG_LABELS_LABEL = 'label'
KG_ALIASES_LABEL = 'alias'
KG_DESCRIPTIONS_LABEL = 'description'
KG_IMAGES_LABEL = 'P18'
KG_FANOUTS_LABEL = 'count_distinct_properties'
KG_DATATYPES_LABEL = 'datatype'

# number of parallel kypher api objects
KYPHER_OBJECTS_NUM = 5

# Data server limits
VALUELIST_MAX_LEN: int = 100
PROPERTY_VALUES_COUNT_LIMIT: int = 10

SORT_METADATA = json.load(open('sort_metadata.json'))
