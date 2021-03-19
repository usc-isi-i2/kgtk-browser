"""
Kypher backend support for the KGTK browser.
"""

import os.path
import io
import csv
from http import HTTPStatus
from functools import lru_cache

import kgtk.kypher.query as kyquery
import kgtk.kypher.sqlstore as sqlstore
from kgtk.exceptions import KGTKException


class BrowserBackend(object):
    """
    KGTK browser backend using the Kypher graph cache and query infrastructure.
    """

    LOG_LEVEL = 0
    MAX_RESULTS = 100000
    LRU_CACHE_SIZE = 1000

    FORMAT_TSV = 'tsv'
    FORMAT_LIST = 'list'
    FORMAT_JSON = 'json'
    LANGUAGE_ANY = 'any'

    def __init__(self, app=None, config=None):
        self.app = app
        self.config = config
        self.sql_store = None
        self.lock = None
        # core data queries:
        self.edges_query = None
        self.labels_query = None
        self.aliases_query = None
        self.descriptions_query = None
        self.edge_qualifiers_query = None
        # string descriptor queries:
        self.edge_label_labels_query = None
        self.edge_node2_labels_query = None
        self.edge_qualifier_label_labels_query = None
        self.edge_qualifier_node2_labels_query = None

    def get_config(self, key, dflt=None):
        """Access a configuration value for 'key' from the associated
        Flask app configuration.
        """
        if self.config is None:
            self.config = self.app.config
        return self.config.get(key, dflt)

    def get_sql_store(self):
        """Create a new SQL store object from the configuration or return a cached value.
        """
        if self.sql_store is None:
            graph_cache = self.get_config('DB_GRAPH_CACHE')
            # TO DO: abstract this better so we can pass in a connection object that is setup the way we want
            self.sql_store = sqlstore.SqliteStore(graph_cache, create=not os.path.exists(graph_cache))
            self.sql_store.close()
            import sqlite3
            self.sql_store.conn = sqlite3.connect(graph_cache, check_same_thread=False)
            self.sql_store.configure()
        return self.sql_store

    def get_lock(self):
        """Return a lock object if one was defined.
        """
        return self.lock

    def set_lock(self, lock):
        """Set the lock object to 'lock'.
        """
        self.lock = lock

    def execute_query(self, query, sql, params):
        """Execute the Kypher 'query' with translation 'sql' and the given 'params'
        and return the result (which is an iterator of tuples).
        """
        # TO DO: abstract this better in Kypher query API
        result = query.store.execute(sql, params)
        query.result_header = [query.unalias_column_name(c[0]) for c in result.description]
        return result

    def subst_params(self, params, substitutions):
        """Return a copy of the list 'params' modified by any 'substitutions'.
        """
        return [substitutions.get(x, x) for x in params]

    def query_result_to_tsv(self, result, header=None):
        """Test driver: convert a query 'result' set into a TSV string.
        """
        output = io.StringIO()
        tsvwriter = csv.writer(output, dialect=None, delimiter='\t',
                               quoting=csv.QUOTE_NONE, quotechar=None,
                               lineterminator='\n',
                               escapechar=None)
        output.write('<pre>')
        if header is not None:
            tsvwriter.writerow(header)
        tsvwriter.writerows(result)
        output.write('</pre>')
        return output.getvalue()

    def query_result_to_list(self, result, header=None):
        """Test driver: convert a query 'result' set into a stringified Python list.
        """
        output = io.StringIO()
        output.write('<pre>')
        if header is not None:
            output.write(header)
            output.write('\n')
        for tuple in result:
            output.write(str(tuple))
            output.write('\n')
        output.write('</pre>')
        return output.getvalue()


    def get_node_edges_query(self):
        """Create and cache the Kypher query used by 'get_node_edges'.
        """
        # TO DO: this currently only caches Kypher query processing, it doesn't use an
        # SQL prepared statement, but then sqlite3 is very fast for simple queries like this:
        if self.edges_query is None:
            store = self.get_sql_store()
            query = kyquery.KgtkQuery([self.get_config('DB_EDGES_GRAPH', 'edges')],
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(n2)' % self.get_config('DB_EDGES_GRAPH'),
                                      where='n=$NODE',
                                      ret='r as id, n as node1, r.label as label, n2 as node2',
                                      limit=str(self.MAX_RESULTS),
                                      # this is just a pseudo parameter which will be instantiated later:
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edges_query = query
        return self.edges_query

    def get_node_edges(self, node):
        """Retrieve all edges that have 'node' as their node1.
        """
        query, sql, params = self.get_node_edges_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_labels_query(self):
        """Create and cache the Kypher query used by 'get_node_labels'.
        """
        if self.labels_query is None:
            store = self.get_sql_store()
            query = kyquery.KgtkQuery([self.get_config('DB_LABELS_GRAPH', 'labels')],
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(l)' % self.get_config('DB_LABELS_GRAPH'),
                                      where='n=$NODE',
                                      ret='distinct l as label',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.labels_query = query
        return self.labels_query

    def get_node_labels(self, node):
        """Retrieve all labels for 'node'.
        """
        query, sql, params = self.get_node_labels_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_aliases_query(self):
        """Create and cache the Kypher query used by 'get_node_aliases'.
        """
        if self.aliases_query is None:
            store = self.get_sql_store()
            query = kyquery.KgtkQuery([self.get_config('DB_ALIASES_GRAPH', 'aliases')],
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(l)' % self.get_config('DB_ALIASES_GRAPH'),
                                      where='n=$NODE',
                                      ret='distinct l as alias',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.aliases_query = query
        return self.aliases_query

    def get_node_aliases(self, node):
        """Retrieve all aliases for 'node'.
        """
        query, sql, params = self.get_node_aliases_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_descriptions_query(self):
        """Create and cache the Kypher query used by 'get_node_descriptions'.
        """
        if self.descriptions_query is None:
            store = self.get_sql_store()
            query = kyquery.KgtkQuery([self.get_config('DB_DESCRIPTIONS_GRAPH', 'descriptions')],
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(l)' % self.get_config('DB_DESCRIPTIONS_GRAPH'),
                                      where='n=$NODE',
                                      ret='distinct l as description',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.descriptions_query = query
        return self.descriptions_query

    def get_node_descriptions(self, node):
        """Retrieve all descriptions for 'node'.
        """
        query, sql, params = self.get_node_descriptions_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result
    
    def get_node_edge_qualifiers_query(self):
        """Create and cache the Kypher query used by 'get_node_edge_qualifiers'.
        """
        if self.edge_qualifiers_query is None:
            store = self.get_sql_store()
            graphs = (self.get_config('DB_EDGES_GRAPH', 'edges'),
                      self.get_config('DB_QUALIFIERS_GRAPH', 'qualifiers'))
            query = kyquery.KgtkQuery(graphs,
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(), `%s`: (r)-[q]->(v)' % graphs,
                                      where='n=$NODE',
                                      ret='q, r as node1, q.label, v as node2',
                                      order='r, v desc',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edge_qualifiers_query = query
        return self.edge_qualifiers_query

    def get_node_edge_qualifiers(self, node):
        """Retrieve all qualifiers for edges that have 'node' as their node1.
        """
        query, sql, params = self.get_node_edge_qualifiers_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

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
            lang = self.get_config('DEFAULT_LANGUAGE', 'en')
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

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def get_node_graph_data(self, node, lang=None):
        """Run all queries neccessary to collect the data to build a 'kgtk_node' object
        and assemble the results into an approriate dict/JSON object.  This function
        focuses on edges and qualifier edges only, but not the label strings required
        to describe them in human-readable form.  Return None if 'node' does not exist
        in the graph.
        """
        edge_tuples = self.get_node_edges(node)
        label_tuples = self.get_node_labels(node)
        alias_tuples = self.get_node_aliases(node)
        desc_tuples = self.get_node_descriptions(node)
        qual_tuples = self.get_node_edge_qualifiers(node)
        
        qualifiers = {}
        for qid, eid, label, value in qual_tuples:
            qedge = {
                '@type': 'kgtk_edge',
                's': eid,
                'p': label,
                'o': value,
            }
            qualifiers.setdefault(eid, []).append(qedge)

        edges = []
        for eid, node1, label, node2 in edge_tuples:
            edge = {
                '@type': 'kgtk_edge',
                '@id': eid,
                's': node1,
                'p': label,
                'o': node2,
            }
            quals = qualifiers.get(eid)
            if quals is not None:
                edge['qualifiers'] = quals
            edges.append(edge)

        node_data = {
            '@type': 'kgtk_node',
            '@id': node,
            'label': [l for (l,) in label_tuples],
            'alias': [a for (a,) in alias_tuples],
            'description': [d for (d,) in desc_tuples],
            'edges': edges,
        }

        if not edges and not node_data['label'] and not node_data['alias'] and not node_data['description']:
            # 'node' doesn't exist or nothing is known about it:
            return None

        if isinstance(lang, str) and lang != self.LANGUAGE_ANY:
            self.filter_lqstrings(node_data['label'], lang, dflt=node)
            self.filter_lqstrings(node_data['alias'], lang)
            self.filter_lqstrings(node_data['description'], lang)
        return node_data


    def get_node_edge_label_labels_query(self):
        """Create and cache the Kypher query used by 'get_node_edge_label_labels'.
        """
        if self.edge_label_labels_query is None:
            store = self.get_sql_store()
            graphs = (self.get_config('DB_EDGES_GRAPH', 'edges'),
                      self.get_config('DB_LABELS_GRAPH', 'labels'))
            query = kyquery.KgtkQuery(graphs,
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r {label: rl}]->(), `%s`: (rl)-[]->(rlabel)' % graphs,
                                      where='n=$NODE',
                                      ret='distinct rl as node1, rlabel as label',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edge_label_labels_query = query
        return self.edge_label_labels_query

    def get_node_edge_label_labels(self, node):
        """Retrieve all label strings associated with labels of edges starting from 'node'.
        """
        query, sql, params = self.get_node_edge_label_labels_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_edge_node2_labels_query(self):
        """Create and cache the Kypher query used by 'get_node_edge_node2_labels'.
        """
        if self.edge_node2_labels_query is None:
            store = self.get_sql_store()
            graphs = (self.get_config('DB_EDGES_GRAPH', 'edges'),
                      self.get_config('DB_LABELS_GRAPH', 'labels'))
            query = kyquery.KgtkQuery(graphs,
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[]->(n2), `%s`: (n2)-[]->(n2label)' % graphs,
                                      where='n=$NODE',
                                      ret='distinct n2 as node1, n2label as label',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edge_node2_labels_query = query
        return self.edge_node2_labels_query

    def get_node_edge_node2_labels(self, node):
        """Retrieve all label strings associated with node2's of edges starting from 'node'.
        """
        query, sql, params = self.get_node_edge_node2_labels_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_edge_qualifier_label_labels_query(self):
        """Create and cache the Kypher query used by 'get_node_edge_qualifier_label_labels'.
        """
        if self.edge_qualifier_label_labels_query is None:
            store = self.get_sql_store()
            graphs = (self.get_config('DB_EDGES_GRAPH', 'edges'),
                      self.get_config('DB_QUALIFIERS_GRAPH', 'qualifiers'),
                      self.get_config('DB_LABELS_GRAPH', 'labels'))
            query = kyquery.KgtkQuery(graphs,
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(), `%s`: (r)-[q {label: ql}]->(), `%s`: (ql)-[]->(qlabel)' % graphs,
                                      where='n=$NODE',
                                      ret='distinct ql as node1, qlabel as label',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edge_qualifier_label_labels_query = query
        return self.edge_qualifier_label_labels_query

    def get_node_edge_qualifier_label_labels(self, node):
        """Retrieve all label strings associated with labels of qualifier edges associated with 'node'.
        """
        query, sql, params = self.get_node_edge_qualifier_label_labels_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    def get_node_edge_qualifier_node2_labels_query(self):
        """Create and cache the Kypher query used by 'get_node_edge_qualifier_node2_labels'.
        """
        if self.edge_qualifier_node2_labels_query is None:
            store = self.get_sql_store()
            graphs = (self.get_config('DB_EDGES_GRAPH', 'edges'),
                      self.get_config('DB_QUALIFIERS_GRAPH', 'qualifiers'),
                      self.get_config('DB_LABELS_GRAPH', 'labels'))
            query = kyquery.KgtkQuery(graphs,
                                      store,
                                      loglevel=self.LOG_LEVEL,
                                      index=self.get_config('DB_INDEX_MODE'),
                                      match='`%s`: (n)-[r]->(), `%s`: (r)-[]->(qn2), `%s`: (qn2)-[]->(qlabel)' % graphs,
                                      where='n=$NODE',
                                      ret='distinct qn2 as node1, qlabel as label',
                                      limit=str(self.MAX_RESULTS),
                                      parameters={'NODE': '$NODE'},
            )
            sql, params, graphs, indexes = query.translate_to_sql()
            query.ensure_relevant_indexes(sql, graphs=graphs, auto_indexes=indexes)
            query = (query, sql, params)
            self.edge_qualifier_node2_labels_query = query
        return self.edge_qualifier_node2_labels_query

    def get_node_edge_qualifier_node2_labels(self, node):
        """Retrieve all label strings associated with node2's of qualifier edges associated with 'node'.
        """
        query, sql, params = self.get_node_edge_qualifier_node2_labels_query()
        result = self.execute_query(query, sql, self.subst_params(params, {'$NODE': node}))
        return result

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def get_node_object_labels(self, node, lang=None):
        """Run all queries neccessary to collect the label string data for all edge
        labels and value objects collected by 'get_node_graph_data', and assemble the
        results into an approriate 'kgtk_object_labels' dict/JSON object.
        """
        edge_label_label_tuples = self.get_node_edge_label_labels(node)
        edge_node2_label_tuples = self.get_node_edge_node2_labels(node)
        qual_label_label_tuples = self.get_node_edge_qualifier_label_labels(node)
        qual_node2_label_tuples = self.get_node_edge_qualifier_node2_labels(node)
        
        object_labels = {}
        for obj, label in edge_label_label_tuples:
            object_labels.setdefault(obj, []).append(label)

        new_labels = {}
        for obj, label in edge_node2_label_tuples:
            if obj not in object_labels:
                new_labels.setdefault(obj, []).append(label)
        for obj, labels in new_labels.items():
            object_labels[obj] = labels

        new_labels = {}
        for obj, label in qual_label_label_tuples:
            if obj not in object_labels:
                new_labels.setdefault(obj, []).append(label)
        for obj, labels in new_labels.items():
            object_labels[obj] = labels

        new_labels = {}
        for obj, label in qual_node2_label_tuples:
            if obj not in object_labels:
                new_labels.setdefault(obj, []).append(label)
        for obj, labels in new_labels.items():
            object_labels[obj] = labels

        if isinstance(lang, str) and lang != self.LANGUAGE_ANY:
            for obj, labels in object_labels.items():
                self.filter_lqstrings(labels, lang, dflt=obj)

        labels_data = {
            '@type': 'kgtk_object_labels',
            '@id': 'kgtk_object_labels_%s' % node,
            'labels': object_labels,
        }
        return labels_data

    def get_all_node_data(self, node, lang=None):
        """Return all graph and label data for 'node' and return it as a
        'kgtk_object_collection' dict/JSON object.  Return None if 'node'
        does not exist in the graph.
        """
        graph_data = self.get_node_graph_data(node, lang=lang)
        if graph_data is None:
            return None
        object_labels = self.get_node_object_labels(node, lang=lang)
        
        node_data = {
            "@type": "kgtk_object_collection",
            # @context and meta info are not used and just for illustration for now:
            "@context": [
                "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
            ],
            "meta": {
                "@type": "kgtk_meta_info",
                "database": "wikidataos-v4",
                "version": "2021-02-24",
            },
            "objects": [ 
                graph_data,
                object_labels,
            ],
        }
        return node_data


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
