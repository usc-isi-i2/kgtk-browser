"""
Kypher backend support for the KGTK browser.
"""

import os.path
import io
import csv
from http import HTTPStatus
from functools import lru_cache
import sqlite3

import pandas as pd

import kgtk.kypher.query as kyquery
import kgtk.kypher.sqlstore as sqlstore
from kgtk.exceptions import KGTKException


# TO DO:
# - reimplement the "language backoff" we had previously; currently we don't
#   substitute labels, etc. from other languages if the desired language is empty


class BrowserBackend(object):
    """
    KGTK browser backend using the Kypher graph cache and query infrastructure.
    """

    LRU_CACHE_SIZE = 1000
    LANGUAGE_ANY = 'any'

    def __init__(self, app, api=None):
        self.app = app
        self.api = api or app.config['NODE_LABELS_QUERY'].api
        # import app config on top of api object config:
        for key, value in self.app.config.items():
            self.api.set_config(key, value)

    def get_config(self, key, dflt=None):
        """Access a configuration value for 'key' from the current configuration.
        """
        return self.api.get_config(key, dflt=dflt)

    def get_lang(self, lang=None):
        return lang or self.get_config('DEFAULT_LANGUAGE', self.LANGUAGE_ANY)

    def get_lock(self):
        """Return the lock object.
        """
        return self.api.get_lock()

    def __enter__(self):
        """Lock context manager for 'with ... as backend:' idiom.
        """
        self.api.__enter__()
        return self

    def __exit__(self, *_exc):
        self.api.__exit__()


    ### Query wrappers:
    
    def get_node_labels(self, node, lang=None, fmt=None):
        """Retrieve all labels for 'node'.
        """
        return self.get_config('NODE_LABELS_QUERY').execute(NODE=node, LANG=self.get_lang(lang), fmt=fmt)

    def get_node_aliases(self, node, lang=None, fmt=None):
        """Retrieve all aliases for 'node'.
        """
        return self.get_config('NODE_ALIASES_QUERY').execute(NODE=node, LANG=self.get_lang(lang), fmt=fmt)

    def get_node_descriptions(self, node, lang=None, fmt=None):
        """Retrieve all descriptions for 'node'.
        """
        return self.get_config('NODE_DESCRIPTIONS_QUERY').execute(NODE=node, LANG=self.get_lang(lang), fmt=fmt)
    
    def get_node_images(self, node, fmt=None):
        """Retrieve all images for 'node'.
        """
        return self.get_config('NODE_IMAGES_QUERY').execute(NODE=node, fmt=fmt)
    
    def get_node_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node1.
        """
        return self.get_config('NODE_EDGES_QUERY').execute(
            NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_inverse_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node2.
        """
        return self.get_config('NODE_INVERSE_EDGES_QUERY').execute(
            NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node1.
        """
        return self.get_config('NODE_EDGE_QUALIFIERS_QUERY').execute(
            NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_inverse_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node2.
        """
        return self.get_config('NODE_INVERSE_EDGE_QUALIFIERS_QUERY').execute(
            NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)


    ### Utilities:

    # this is currently not needed, but we keep it just in case we reimplement language backoff:
    def filter_lqstrings(self, strings, lang, dflt=None):
        """Destructively filter 'strings' to contain the first language-qualified string
        satisfying 'lang' as its only element.  If 'strings' is not a list, listify it first.
        An element matches if it is an LQ-string and its language tag starts with 'lang'
        (which means 'zh' matches 'zh-ch' for example).  If no qualifying element could be
        found first try to fall back on the configured DEFAULT_LANGUAGE, if that fails on
        the first element of 'strings', if that fails 'dflt', otherwise return an empty list.
        Return the filtered modified or newly constructed list.
        """
        if not isinstance(strings, list):
            strings = list(strings)
        suffix = "'@" + lang
        filtered = list(filter(lambda x: isinstance(x, str) and x.startswith("'") and x.find(suffix) > 0, strings))
        if not filtered:
            lang = self.get_config('DEFAULT_LANGUAGE')
            suffix = "'@" + lang
            filtered = list(filter(lambda x: isinstance(x, str) and x.startswith("'") and x.find(suffix) > 0, strings))
        if not filtered and strings:
            filtered = [strings[0]]
        if not filtered and dflt is not None:
            filtered = [dflt]
        strings.clear()
        if filtered:
            strings.append(filtered[0])
        return strings

    def query_result_to_string(self, result):
        """Convert a query 'result' into a string so it can be displayed.
        """
        output = io.StringIO()
        output.write('<pre>\n')
        if type(result).__name__ == 'DataFrame':
            output.write(result.to_string())
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=4, stream=output)
            pp.pprint(result)
        output.write('</pre>\n')
        return output.getvalue()


    ### Collecting node data:
    
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
    
    def collect_edges(self, edges_df):
        """Given a full edges dataframe 'edges_df' including target node info columns, 
        project out the core edge columns and remove any duplicates.
        """
        if edges_df is not None:
            df = edges_df.loc[:,self.KGTK_EDGE_COLUMNS]
            df.drop_duplicates(ignore_index=True, inplace=True)
            return df
        return None

    def collect_edge_label_labels(self, edges_df, lang=None, inverse=False):
        """Given an edges dataframe 'edges_df' collect all label strings for any referenced
        edge labels according to 'lang' and return a binary label_node/label_string frame.
        'inverse' indicates that 'edges_df' is an inverse edge frame which is ignored.
        """
        # TO DO: make this more efficient, but caching will smooth this out quickly
        if edges_df is not None:
            if edges_df.empty:
                return pd.DataFrame([], columns=(self.NODE1_COLUMN, self.LABEL_COLUMN))
            df = edges_df.loc[:,[self.LABEL_COLUMN]]
            df.drop_duplicates(ignore_index=True, inplace=True)
            labels = [self.get_node_labels(row[self.LABEL_COLUMN], lang=lang, fmt='df') for index, row in df.iterrows()]
            labels_df = pd.concat(labels, ignore_index=True, copy=False)
            return labels_df
        return None
    
    def collect_edge_node_labels(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node label columns and remove any duplicates.  'inverse' indicates that 
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.loc[:,[target_column, self.NODE_LABEL_COLUMN]]
            df.dropna(inplace=True)
            df.drop_duplicates(ignore_index=True, inplace=True)
            return df
        return None
    
    def collect_edge_node_images(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node image columns and remove any duplicates.  'inverse' indicates that 
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.loc[:,[target_column, self.NODE_IMAGE_COLUMN]]
            df.dropna(inplace=True)
            df.drop_duplicates(ignore_index=True, inplace=True)
            return df
        return None
    
    def collect_edge_node_fanouts(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node fanout columns and remove any duplicates.  'inverse' indicates that
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.loc[:,[target_column, self.NODE_FANOUT_COLUMN]]
            # TO DO: think about folding default fanout substitution into here:
            df.dropna(inplace=True)
            df = df.astype({self.NODE_FANOUT_COLUMN: int})
            df.drop_duplicates(ignore_index=True, inplace=True)
            return df
        return None

    def union_frames(self, *dfs):
        """Take the union of all data frames 'dfs' which are assumed to have the same arity
        and column type, but not necessarily the same name, and remove any duplicates.
        The result uses the column names of the first of 'dfs'.
        """
        columns = None
        norm_dfs = []
        for df in dfs:
            if df is None:
                continue
            if columns is None and norm_dfs:
                columns = norm_dfs[0].columns
            if columns is not None and not df.columns.equals(columns):
                df = df.rename(columns=dict(zip(df.columns, columns)), inplace=False)
            norm_dfs.append(df)
        if not norm_dfs:
            return None
        if len(norm_dfs) == 1:
            return norm_dfs[0]
        else:
            df = pd.concat(norm_dfs, ignore_index=True, copy=False)
            df.drop_duplicates(ignore_index=True, inplace=True)
            return df

    #@lru_cache(maxsize=LRU_CACHE_SIZE)
    def get_node_data_frames(self, node, lang=None, images=False, fanouts=False, inverse=False):
        """Run all neccessary queries to collect the data to build a 'kgtk_node' object for 'node'.
        Collects all relevant data for 'node' into a set of data frames that is returned as a dict.
        Converting those into the appropriate JSON object(s) is done in separate steps.
        Return None if 'node' does not exist in the graph.

        'lang' controls the language of labels, aliases, etc. (one of 'any', 'en', 'es', etc.)
        If 'images' is True, also include images for 'node' and 'node2's of edges and qualifiers.
        If 'fanouts' is True, also include fanouts for 'node2's of edges and qualifiers.
        If 'inverse' also include edges that have 'node' as their 'node2' (and their qualifiers).
        For inverse edges, labels, images and fanouts are collected for the respective 'node1'.
        Inverse edges may have very high fanout (e.g. in Wikidata), so be careful with that.
        """

        node_labels = self.get_node_labels(node, lang=lang, fmt='df')
        node_aliases = self.get_node_aliases(node, lang=lang, fmt='df')
        node_descs = self.get_node_descriptions(node, lang=lang, fmt='df')
        # the 'images' switch only controls 'node2' images, not images for 'node':
        node_images = self.get_node_images(node, fmt='df')
        
        edges = self.get_node_edges(node, lang=lang, images=images, fanouts=fanouts, fmt='df')
        quals = self.get_node_edge_qualifiers(node, lang=lang, images=images, fanouts=fanouts, fmt='df')

        inv_edges, inv_quals = None, None
        if inverse:
            inv_edges = self.get_node_inverse_edges(node, lang=lang, images=images, fanouts=fanouts, fmt='df')
            inv_quals = self.get_node_inverse_edge_qualifiers(node, lang=lang, images=images, fanouts=fanouts, fmt='df')
            
        if (node_labels.empty and node_aliases.empty and node_descs.empty and
            edges.empty and (inv_edges is None or inv_edges.empty)):
            # 'node' doesn't exist or nothing is known about it:
            return None

        all_edges = self.union_frames(self.collect_edges(edges), self.collect_edges(inv_edges))
        all_quals = self.union_frames(self.collect_edges(quals), self.collect_edges(inv_quals))

        all_labels = self.union_frames(
            node_labels,
            self.collect_edge_label_labels(edges, lang=lang),
            self.collect_edge_label_labels(inv_edges, lang=lang, inverse=True),
            self.collect_edge_label_labels(quals, lang=lang),
            self.collect_edge_label_labels(inv_quals, lang=lang),
            self.collect_edge_node_labels(edges),
            self.collect_edge_node_labels(inv_edges, inverse=True),
            self.collect_edge_node_labels(quals),
            self.collect_edge_node_labels(inv_quals))

        all_images = None
        if images:
            all_images = self.union_frames(
                node_images,
                self.collect_edge_node_images(edges),
                self.collect_edge_node_images(inv_edges, inverse=True),
                self.collect_edge_node_images(quals),
                self.collect_edge_node_images(inv_quals))

        all_fanouts = None
        if fanouts:
            all_fanouts = self.union_frames(
                self.collect_edge_node_fanouts(edges),
                self.collect_edge_node_fanouts(inv_edges, inverse=True),
                self.collect_edge_node_fanouts(quals),
                self.collect_edge_node_fanouts(inv_quals))
        
        node_data = {
            'node': node,
            'labels': node_labels,
            'aliases': node_aliases,
            'descriptions': node_descs,
            'images': node_images,
            'edges': all_edges,
            'qualifiers': all_quals,
            'all_labels': all_labels,
            'all_images': all_images,
            'all_fanouts': all_fanouts,
        }
        return node_data


    ### Converting to JSON objects:

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
        df = edges_df.rename(columns=self.KGTK_TO_JSON_EDGE_COLUMN_MAP, inplace=False)
        # add JSON-LD @type field:
        df['@type'] = 'kgtk_edge'
        return df.to_dict(orient='records')

    def value_df_to_json(self, values_df):
        """Convert a single-valued 'values_df' data frame into a corresponding JSON list of dicts.
        Assumes 'values_df' is a binary key/value frame where each key has exactly 1 value.
        """
        return dict(values_df.itertuples(index=False, name=None))

    def values_df_to_json(self, values_df):
        """Convert a multi-valued 'values_df' data frame into a corresponding JSON list of dicts.
        Assumes 'values_df' is a binary key/value frame where each key can have multiple values.
        """
        keycol = values_df.columns[0]
        valcol = values_df.columns[1]
        return values_df.groupby(by=keycol)[valcol].apply(list).to_dict()

    def node_data_core_to_json(self, node_data):
        """Convert core node components of 'node_data' into a JSONLD 'kgtk_node' object.
        """
        node = node_data['node']
        core_data = {
            '@type': 'kgtk_node',
            '@id':   node,
            'label': list(node_data['labels'][self.NODE_LABEL_COLUMN]),
            'alias': list(node_data['aliases'][self.NODE_ALIAS_COLUMN]),
            'description':
                     list(node_data['descriptions'][self.NODE_DESCRIPTION_COLUMN]),
            'image': list(node_data['images'][self.NODE_IMAGE_COLUMN]),
            'edges': self.edges_df_to_json(node_data['edges'])
        }
        # adding qualifiers to edge dicts is a bit messy, maybe there is a more panda-ish way:
        qualifiers = node_data['qualifiers']
        if not qualifiers.empty:
            edge_index = {edge[self.JSON_ID_COLUMN]: edge for edge in core_data['edges']}
            for edge_id, quals in qualifiers.groupby(self.NODE1_COLUMN):
                edge_index[edge_id]['qualifiers'] = self.edges_df_to_json(quals)
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
            'images': images is not None and self.values_df_to_json(images) or [],
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
            'fanouts': fanouts is not None and self.value_df_to_json(fanouts) or [],
        }
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
                "database": os.path.basename(self.api.sql_store.dbfile),
                "version": "2021-08-01",
            },
            "objects": objects,
        }
        return node_data


    ### Top level:
    
    def get_all_node_data(self, node, lang=None, images=False, fanouts=False, inverse=False):
        """Return all graph and label data for 'node' and return it as a
        'kgtk_object_collection' dict/JSON object.  Return None if 'node'
        does not exist in the graph.  If 'images' and/or 'fanouts' is True
        fetch and add the respective node2 descriptor data.  If 'inverse'
        is True, also include edges (and their associated info) that have
        'node' as their node2.
        """
        node_data = self.get_node_data_frames(node, lang=lang, images=images, fanouts=fanouts, inverse=inverse)
        if node_data is None:
            return None
        else:
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
