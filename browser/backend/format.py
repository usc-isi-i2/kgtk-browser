"""
KGTK browser node data formatters.
"""

from   kgtk.exceptions import KGTKException


ID_COLUMN    = 'id'
NODE1_COLUMN = 'node1'
LABEL_COLUMN = 'label'
NODE2_COLUMN = 'node2'
KGTK_EDGE_COLUMNS = [ID_COLUMN, NODE1_COLUMN, LABEL_COLUMN, NODE2_COLUMN]

NODE_LABEL_COLUMN       = 'node_label'
NODE_ALIAS_COLUMN       = 'node_alias'
NODE_DESCRIPTION_COLUMN = 'node_description'
NODE_IMAGE_COLUMN       = 'node_image'
NODE_FANOUT_COLUMN      = 'node_fanout'   


class NodeDataFormat(object):
    """Convert node data into a set of JSON objects that encode edges as
    list of triples with qualifiers, plus label, image and fanout dictionaries.
    """

    def format_node_data(self, node_data):
        """Abstract top-level entry point.  Convert all of 'node_data'
        into the respective format and return the result.
        """
        raise KGTKException('not implemented')


class JsonTripleFormat(NodeDataFormat):
    """Convert node data into a set of JSON objects that encode edges as
    list of triples with qualifiers, plus label, image and fanout dictionaries.
    """

    JSON_ID_COLUMN    = '@id'
    JSON_NODE1_COLUMN = 's'
    JSON_LABEL_COLUMN = 'p'
    JSON_NODE2_COLUMN = 'o'
    JSON_EDGE_COLUMNS = [JSON_ID_COLUMN, JSON_NODE1_COLUMN, JSON_LABEL_COLUMN, JSON_NODE2_COLUMN]
    KGTK_TO_JSON_EDGE_COLUMN_MAP = {k: v for k, v in zip(KGTK_EDGE_COLUMNS, JSON_EDGE_COLUMNS)}
    
    def edges_df_to_json(self, edges_df):
        """Convert an edges data frame 'edges_df' into a corresponding JSON list of dicts.
        Assumes 'edges_df' has been projected onto its four core columns.  Renames triple
        columns to 's/p/o' to save some space.
        """
        orig_columns = edges_df.columns
        edges_df.rename(self.KGTK_TO_JSON_EDGE_COLUMN_MAP, inplace=True)
        # add JSON-LD @type field:
        json_edges = edges_df.to_records_dict()
        for edge in json_edges:
            edge['@type'] = 'kgtk_edge'
        edges_df.columns = orig_columns
        return json_edges

    def value_df_to_json(self, values_df):
        """Convert a single-valued 'values_df' data frame into a corresponding JSON dict.
        Assumes 'values_df' is a binary key/value frame where each key has exactly 1 value.
        """
        return values_df.to_value_dict()

    def values_df_to_json(self, values_df):
        """Convert a multi-valued 'values_df' data frame into a corresponding JSON dict.
        Assumes 'values_df' is a binary key/value frame where each key can have multiple values.
        """
        return values_df.to_values_dict()

    def node_data_core_to_json(self, node_data):
        """Convert core node components of 'node_data' into a JSONLD 'kgtk_node' object.
        """
        node = node_data['node']
        core_data = {
            '@type': 'kgtk_node',
            '@id':   node,
            'label': node_data['labels'].project(NODE_LABEL_COLUMN).to_list(),
            'alias': node_data['aliases'].project(NODE_ALIAS_COLUMN).to_list(),
            'description':
                     node_data['descriptions'].project(NODE_DESCRIPTION_COLUMN).to_list(),
            'image': node_data['images'].project(NODE_IMAGE_COLUMN).to_list(),
            'edges': self.edges_df_to_json(node_data['edges'])
        }
        # adding qualifiers to edge dicts is a bit messy, maybe abstract this better:
        qualifiers = self.edges_df_to_json(node_data['qualifiers'])
        if qualifiers:
            edge_index = {edge[self.JSON_ID_COLUMN]: edge for edge in core_data['edges']}
            for qual in qualifiers:
                edge_id = qual[self.JSON_NODE1_COLUMN]
                edge_index[edge_id].setdefault('qualifiers', []).append(qual)
        return core_data

    def node_data_labels_to_json(self, node_data):
        """Convert label components of 'node_data' into a JSONLD 'kgtk_object_labels' dict.
        """
        node = node_data['node']
        labels_data = {
            '@type': 'kgtk_object_labels',
            '@id': 'kgtk_object_labels_%s' % node,
            'labels': self.values_df_to_json(node_data['all_labels']),
        }
        return labels_data

    def node_data_images_to_json(self, node_data):
        """Convert image components of 'node_data' into a JSONLD 'kgtk_object_images' dict.
        """
        node = node_data['node']
        images = node_data['all_images']
        images_data = {
            '@type': 'kgtk_object_images',
            '@id': 'kgtk_object_images_%s' % node,
            'images': images is not None and self.values_df_to_json(images) or {},
        }
        return images_data

    def node_data_fanouts_to_json(self, node_data):
        """Convert image components of 'node_data' into a JSONLD 'kgtk_object_fanouts' dict.
        """
        node = node_data['node']
        fanouts = node_data['all_fanouts']
        fanouts_data = {
            '@type': 'kgtk_object_fanouts',
            '@id': 'kgtk_object_fanouts_%s' % node,
            'fanouts': fanouts is not None and self.value_df_to_json(fanouts) or {},
        }
        # coerce fanout values to ints:
        fanouts = fanouts_data['fanouts']
        for n, f in fanouts.items():
            fanouts[n] = int(f)
        return fanouts_data

    def node_data_to_json(self, node_data):
        """Convert all of 'node_data' into a JSONLD 'kgtk_object_collection' object
        including (dummy) context and meta information.
        """
        objects = []
        objects.append(self.node_data_core_to_json(node_data))
        objects.append(self.node_data_labels_to_json(node_data))
        if node_data['all_images'] is not None:
            objects.append(self.node_data_images_to_json(node_data))
        if node_data['all_fanouts'] is not None:
            objects.append(self.node_data_fanouts_to_json(node_data))
        node_data = {
            "@type": "kgtk_object_collection",
            # @context and meta info are not used and just for illustration for now:
            "@context": [
                "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
            ],
            "meta": {
                "@type": "kgtk_meta_info",
                # if we do want to support this again, we should pass it in as part of 'node_data':
                #"database": os.path.basename(self.api.sql_store.dbfile),
                "version": "2021-08-19",
            },
            "objects": objects,
        }
        return node_data

    def format_node_data(self, node_data):
        """Top-level entry point.  Convert all of 'node_data' into a JSONLD
        'kgtk_object_collection' object including (dummy) context and meta information.
        """
        return self.node_data_to_json(node_data)


"""
# Data format deliberations (Hans' variant of Pedro's data model sketch):
#
# (0) we use something that intentionally looks JSON-LD-ish (after our OPERA data model),
#     in case we ever want to exploit that, but doesn't actually require JSON-LD
# (1) we keep all literals with their encoding delimiters for now, stuck insinde JSON strings,
#     that way things like language qualifiers, etc. can easily be accessed
# (2) we avoid Wikidata-ish terminology such as "claims" to keep things more general
#     and applicable to non-Wikidata domains
# (3) we keep a typed object model for nodes, edges, values and other things we might need
# (4) we have a slightly more explicit/verbose representation to avoid having to rely
#     on the enclosing JSON context (too much)
# (5) if bandwidth becomes an issue, we can easily transition this to a more compact
#     representation such as protobufs

{
  "@context": [
    "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
  ],
  "@type": "kgtk_object_collection",
  "meta": {
    "@type": "kgtk_meta_info",
    "database": "wikidataos-v4",
    "version": "2021-02-24",
    ....<anything else we might need>...
  }
  "objects": [ 
    ....
  ]
}

{
  '@type': 'kgtk_node',
  '@id': 'Q30',
  'label': "'United States of America'@en",
  'alias': ['USA', 'US'],
  'description': 'sovereign state in North America',
  'edges': [
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qxyz',
              'node1': 'Q30',
              'label': 'P123',
              'node2': 'Qxyz',
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               'node1': 'Q30-P123-Qxyz',
                               'label': 'P585',
                               'node2': '^1970-00-00T00:00:00Z/9'
                              },
                              {'@type': 'kgtk_edge',
                               'node1': 'Q30-P123-Qxyz',
                               'label': 'P890',
                               'node2': 'Q4567'
                              },
                              {'@type': 'kgtk_edge',
                               'node1': 'Q30-P123-Qxyz',
                               'label': 'P876',
                               'node2': '0.0'
                              }
              ]
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qabc',
              'node1': 'Q30',
              'label': 'P123',
              'node2': 'Qabc'
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P234-5000',
              'node1': 'Q30',
              'label': 'p234',
              'node2': '5000',
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               'node1': 'Q30-P234-5000',
                               'label': 'P585',
                               'node2': '^1970-00-00T00:00:00Z/9'
                              }
               ]
             }
    ]
}

# more compact alternative using spo:
{
  '@type': 'kgtk_node',
  '@id': 'Q30',
  'label': "'United States of America'@en",
  'alias': ['USA', 'US'],
  'description': 'sovereign state in North America',
  'edges': [
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qxyz',
              'spo': ['Q30', 'P123', 'Qxyz'],
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               'spo': ['Q30-P123-Qxyz', 'P585', '^1970-00-00T00:00:00Z/9']
                              },
                              {'@type': 'kgtk_edge',
                               'spo': ['Q30-P123-Qxyz', 'P890', 'Q4567']
                              },
                              {'@type': 'kgtk_edge',
                               'spo': ['Q30-P123-Qxyz', 'P876', '0.0']
                              }
              ]
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qabc',
              'spo': ['Q30', 'P123', 'Qabc']
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P234-5000',
              'spo': ['Q30', 'p234', '5000'],
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               'spo': ['Q30-P234-5000', 'P585', '^1970-00-00T00:00:00Z/9']
                              }
               ]
             }
    ]
}

# compromise that uses separate s/p/o keys in case we ever do want to interpret
# this as JSON-LD, in which case the list representation would be cumbersome
# (this is what we currently use):

{
  '@type': 'kgtk_node',
  '@id': 'Q30',
  'label': "'United States of America'@en",
  'alias': ['USA', 'US'],
  'description': 'sovereign state in North America',
  'edges': [
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qxyz',
              's': 'Q30', 'p': 'P123', 'o': 'Qxyz',
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               's': 'Q30-P123-Qxyz', 'p': 'P585', 'o': '^1970-00-00T00:00:00Z/9'
                              },
                              {'@type': 'kgtk_edge',
                               's': 'Q30-P123-Qxyz', 'p': 'P890', 'o': 'Q4567'
                              },
                              {'@type': 'kgtk_edge',
                               's': 'Q30-P123-Qxyz', 'p': 'P876', 'o': '0.0'
                              }
              ]
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P123-Qabc',
              's': 'Q30', 'p': 'P123', 'o': 'Qabc'
             },
             {'@type': 'kgtk_edge',
              '@id': 'Q30-P234-5000',
              's': 'Q30', 'p': 'p234', 'o': '5000',
              'qualifiers': [
                              {'@type': 'kgtk_edge',
                               's': 'Q30-P234-5000', 'p': 'P585', 'o': '^1970-00-00T00:00:00Z/9'
                              }
               ]
             }
    ]
}

{
  '@type': 'kgtk_object_labels',
  '@id': 'kgtk_object_labels_4567',
  'labels': {
    'Qxyz': 'some label',
    'Qabc': 'another label',
    ...: ...,
  }
}

# data types: TBD
{
  '@type': 'kgtk_property_types',
  '@id': 'kgtk_property_types_1234',
  'datatypes': {
    'P123': 'wikibase-item',
    'P234': 'quantity',
    'PP585': 'time',
    ...: ...,
  }
}

# sitelinks: TBD
"""
