# KGTK browser configuration
import os
import json
import sys
from pathlib import Path
from kgtk.io.kgtkreader import KgtkReader, KgtkReaderMode

PROFILED_PROPERTY_METADATA = {}

"""
The file wikidata_language_mapping.json is created by running the following query:
https://query.wikidata.org/#SELECT%0A%20%20%3Fitem%20%0A%20%20%3Fc%20%28CONTAINS%28%3Fc%2C%22-%22%29%20as%20%3Fsubtag%29%0A%20%20%3Fwdlabelen%0A%20%20%28CONCAT%28%22%5B%5B%3Aen%3A%22%2C%3Fenwikipeda%2C%22%5Cu007C%22%2C%3Fenwikipeda%2C%22%5D%5D%22%29%20as%20%3Fwikipedia_link_en%29%0A%20%20%3Flang%0A%20%20%3Fwdlabelinlang%0A%20%20%28CONCAT%28%22%5B%5B%3A%22%2C%3Flang%2C%22%3A%22%2C%3Fwikipeda%2C%22%5Cu007C%22%2C%3Fwikipeda%2C%22%5D%5D%22%29%20as%20%3Fwikipedia_link%29%0AWHERE%0A%7B%0A%20%20VALUES%20%3Flang%20%7B%20%22fr%22%20%7D%0A%20%20%3Fitem%20wdt%3AP424%20%3Fc%20.%0A%20%20hint%3APrior%20hint%3ArangeSafe%20true%20.%0A%20%20MINUS%7B%3Fitem%20wdt%3AP31%20wd%3AQ47495990%7D%0A%20%20MINUS%7B%3Fitem%20wdt%3AP31%2Fwdt%3AP279%2a%20wd%3AQ14827288%7D%20%23exclude%20Wikimedia%20projects%0A%20%20MINUS%7B%3Fitem%20wdt%3AP31%2Fwdt%3AP279%2a%20wd%3AQ17442446%7D%20%23exclude%20Wikimedia%20internal%20stuff%0A%20%20OPTIONAL%20%7B%20%3Fitem%20rdfs%3Alabel%20%3Fwdlabelinlang%20.%20FILTER%28%20lang%28%3Fwdlabelinlang%29%3D%20%22fr%22%20%29%20%7D%0A%20%20OPTIONAL%20%7B%20%3Fitem%20rdfs%3Alabel%20%3Fwdlabelen%20.%20FILTER%28lang%28%3Fwdlabelen%29%3D%22en%22%29%20%7D%0A%20%20OPTIONAL%20%7B%20%5B%5D%20schema%3Aabout%20%3Fitem%20%3B%20schema%3AinLanguage%20%3Flang%3B%20schema%3AisPartOf%20%2F%20wikibase%3AwikiGroup%20%22wikipedia%22%20%3B%20schema%3Aname%20%3Fwikipeda%20%7D%20%0A%20%20OPTIONAL%20%7B%20%5B%5D%20schema%3Aabout%20%3Fitem%20%3B%20schema%3AinLanguage%20%22en%22%3B%20schema%3AisPartOf%20%2F%20wikibase%3AwikiGroup%20%22wikipedia%22%20%3B%20schema%3Aname%20%3Fenwikipeda%20%7D%20%0A%7D%0AORDER%20BY%20%3Fc
"""


def read_wikidata_language_metadata(wikidata_language_metadata_file):
    wikidata_languages = {}
    with open(wikidata_language_metadata_file, 'r') as f:
        wikidata_language_metadata = json.load(f)

    for wikidata_language in wikidata_language_metadata:
        wikidata_languages[wikidata_language['c']] = wikidata_language.get('wdlabelen', wikidata_language['c'])

    return wikidata_languages


def read_sorting_metadata_ajax(metadata_file, metadata_supplementary_file):
    sorting_metadata = read_metadata_file(metadata_file)
    sorting_metadata.update(read_metadata_file(metadata_supplementary_file))
    return sorting_metadata


def read_url_formatter_templates(url_formatter_template_file: str) -> dict:
    url_formatter_template_dict = {}
    kr: KgtkReader = KgtkReader.open(Path(url_formatter_template_file),
                                     error_file=sys.stderr,
                                     mode=KgtkReaderMode.EDGE
                                     )
    node1_idx = kr.column_name_map['node1']
    node2_idx = kr.column_name_map['node2']

    for row in kr:
        node1 = row[node1_idx]
        node2 = row[node2_idx]
        if node1 not in url_formatter_template_dict:
            # print(node1, node2, url_formatter_template_dict[node1])
            # raise Exception('Duplicate url formatter template')
            url_formatter_template_dict[node1] = []
        url_formatter_template_dict[node1].append(node2)

    return url_formatter_template_dict


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
INDEX_MODE = 'none'
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
KG_SUBCLASS_LABEL = "P279"
KG_SUBCLASSSTAR_LABEL = "P279star"

MATCH_LABEL_IS_CLASS = False
MATCH_LABEL_INSTANCE_OF = None

# number of parallel kypher api objects
KYPHER_OBJECTS_NUM = 5

# Data server limits
VALUELIST_MAX_LEN: int = 100
PROPERTY_VALUES_COUNT_LIMIT: int = 10

KGTK_BROWSER_SORTING_METADATA = 'kgtk_browser_sorting_metadata.tsv'
KGTK_BROWSER_SORTING_METADATA_SUPPLEMENTARY = 'kgtk_browser_sorting_metadata_supplementary.tsv'
KGTK_URL_FORMATTER_TEMPLATES_FILE = 'formatter_url_templates.tsv.gz'

PROPERTIES_SORT_METADATA = json.load(open('sync_properties_sort_metadata.json'))
SYNC_PROPERTIES_SORT_METADATA = PROPERTIES_SORT_METADATA['sync_properties']
AJAX_PROPERTIES_SORT_METADATA = read_sorting_metadata_ajax(KGTK_BROWSER_SORTING_METADATA,
                                                           KGTK_BROWSER_SORTING_METADATA_SUPPLEMENTARY)

WIKIDATA_LANGUAGES = read_wikidata_language_metadata('wikidata_language_mapping.json')

KGTK_URL_FORMATTER_TEMPLATES = read_url_formatter_templates(KGTK_URL_FORMATTER_TEMPLATES_FILE)
