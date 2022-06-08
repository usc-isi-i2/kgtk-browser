# KGTK browser configuration
import os
import json
import sys
from pathlib import Path
from kgtk.io.kgtkreader import KgtkReader, KgtkReaderMode

PROFILED_PROPERTY_METADATA = {}


def read_sorting_metadata_ajax(metadata_file, metadata_supplementary_file):
    sorting_metadata = read_metadata_file(metadata_file)
    sorting_metadata.update(read_metadata_file(metadata_supplementary_file))
    return sorting_metadata


def read_metadata_file(metadata_file):
    kr: KgtkReader = KgtkReader.open(Path(metadata_file),
                                     error_file=sys.stderr,
                                     mode=KgtkReaderMode.EDGE
                                     )

    node1_idx = kr.column_name_map['node1']
    node2_idx = kr.column_name_map['node2']
    label_idx = kr.column_name_map['label']
    sorting_metadata = {}

    for row in kr:
        node1 = row[node1_idx]
        label = row[label_idx]
        node2 = row[node2_idx]

        if label == 'P7482' and node2 == 'Q108739856':
            PROFILED_PROPERTY_METADATA[node1] = 1

        if node1 not in sorting_metadata and '-' not in node1:
            sorting_metadata[node1] = dict()

        if '-' in node1:
            node1 = node1.split('-')[0]
            if label == 'datatype':
                label = 'qualifier_datatype'

        prop_val_dict = sorting_metadata.get(node1, None)
        if prop_val_dict is not None:
            prop_val_dict[label] = node2
    return sorting_metadata


# Basic configuration section:

VERSION = '0.1.0'
if 'KGTK_BROWSER_GRAPH_ID' in os.environ and os.environ['KGTK_BROWSER_GRAPH_ID'] is not None:
    GRAPH_ID = os.environ['KGTK_BROWSER_GRAPH_ID']
else:
    GRAPH_ID = 'my-knowledge-graph'

if 'KGTK_BROWSER_GRAPH_CACHE' in os.environ and os.environ['KGTK_BROWSER_GRAPH_CACHE'] is not None:
    GRAPH_CACHE = os.environ['KGTK_BROWSER_GRAPH_CACHE']
else:
    GRAPH_CACHE = './wikidata.sqlite3.db'

if 'KGTK_BROWSER_CLASS_VIZ_DIR' in os.environ and os.environ['KGTK_BROWSER_CLASS_VIZ_DIR'] is not None:
    CLASS_VIZ_DIR = os.environ['KGTK_BROWSER_CLASS_VIZ_DIR']
else:
    CLASS_VIZ_DIR = "/data/class_viz_files"

# Color for nodes and edges
ORANGE_NODE_HEX = '#FF8C00'
BLUE_NODE_HEX = '#1874CD'
RED_EDGE_HEX = '#CD2626'
BLUE_EDGE_HEX = '#1874CD'

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
KG_ABSTRACT_LABEL = 'Pshort_abstract'
KG_INSTANCE_COUNT = 'Pinstance_count'
KG_INSTANCE_COUNT_STAR = 'Pinstance_count_star'
KG_SUBCLASS_COUNT_STAR = 'Psubclass_count_star'
KG_HIDE_PROPERTIES_RELATED_ITEMS = ["Pproperty_domain"]
KG_WIKIPEDIA_URL_LABEL = 'wikipedia_sitelink'

# number of parallel kypher api objects
KYPHER_OBJECTS_NUM = 5

# Data server limits
VALUELIST_MAX_LEN: int = 100
PROPERTY_VALUES_COUNT_LIMIT: int = 10

KGTK_BROWSER_SORTING_METADATA = 'kgtk_browser_sorting_metadata.tsv'
KGTK_BROWSER_SORTING_METADATA_SUPPLEMENTARY = 'kgtk_browser_sorting_metadata_supplementary.tsv'

PROPERTIES_SORT_METADATA = json.load(open('sync_properties_sort_metadata.json'))
SYNC_PROPERTIES_SORT_METADATA = PROPERTIES_SORT_METADATA['sync_properties']
AJAX_PROPERTIES_SORT_METADATA = read_sorting_metadata_ajax(KGTK_BROWSER_SORTING_METADATA,
                                                           KGTK_BROWSER_SORTING_METADATA_SUPPLEMENTARY)
