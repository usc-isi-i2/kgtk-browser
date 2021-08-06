"""
Kypher backend support for the KGTK browser.
"""

import os.path
import io
import csv
from http import HTTPStatus
from functools import lru_cache
import sqlite3
from operator import itemgetter
from collections import OrderedDict
import itertools

import kgtk.kypher.query as kyquery
import kgtk.kypher.sqlstore as sqlstore
from kgtk.exceptions import KGTKException


# TO DO:
# - reimplement the "language backoff" we had previously; currently we don't
#   substitute labels, etc. from other languages if the desired language is empty


class FastDataFrame(object):
    """
    Fast and simple dataframe implementation that mirrors the functionality we
    previously implemented via pandas.  This is less general but about 10x faster.
    """
    
    def __init__(self, columns, rows):
        """Create a dataframe with header 'columns' and data 'rows'.
        'columns' may be integers or strings and can be a single atom.
        'rows' can be any list or iterable of tuples whose arity is uniform
        and matches 'columns'.
        """
        self.columns = self.get_columns(columns)  # columns are always kept as a tuple
        self.rows = rows                          # rows can be a list, set or iterable

    def __iter__(self):
        return self.rows.__iter__()

    def __len__(self):
        return len(self.get_rows())

    def __getitem__(self, index):
        """Support indexed access to rows which requires conversion to a list format.
        """
        rows = self.rows
        if not isinstance(rows, (list, tuple)):
            rows = list(rows)
            self.rows = rows
        return rows[index]

    def empty(self):
        return len(self) == 0

    def copy(self):
        # if it is an iterable, we need to listify first, otherwise copying will exhaust the iter:
        rows = self.get_rows()
        return FastDataFrame(self.columns, rows.copy())

    def get_columns(self, columns=None):
        """Map 'columns' or the current columns onto a normalized tuple.
        'columns' may be integers or strings and can be a single atom.
        """
        columns = self.columns if columns is None else columns
        columns = (columns,) if isinstance(columns, (int, str)) else columns
        return tuple(columns)

    def get_rows(self):
        """Materialize the current set of rows as a list if necessary
        and return the result.
        """
        if not isinstance(self.rows, (list, set, tuple)):
            self.rows = list(self.rows)
        return self.rows
        
    def _get_column_indices(self, columns):
        """Convert 'columns' into a set of integer indices into 'self.columns'.
        'columns' may be integers or strings and can be a single atom.
        """
        icols = []
        for col in self.get_columns(columns):
            if isinstance(col, int):
                icols.append(col)
            else:
                icols.append(self.columns.index(col))
        return tuple(icols)

    def rename(self, colmap, inplace=False):
        """Rename some or all columns according to the map in 'colmap'.
        """
        newcols = tuple(colmap.get(c, c) for c in self.columns)
        df = inplace and self or FastDataFrame(newcols, self.rows)
        df.columns = newcols
        return df

    def project(self, columns):
        """Project rows of 'self' according to 'columns' which might be integer or string indices.
        This always creates a new dataframe as a result.  If a single column is given as an atom,
        rows will be atomic, if given as a list rows will be single-element tuples.
        """
        atomic_singletons = isinstance(columns, (int, str))
        icols = self._get_column_indices(columns)
        if len(icols) > 1 or atomic_singletons:
            return FastDataFrame(itemgetter(*icols)(self.columns), map(lambda r: itemgetter(*icols)(r), self.rows))
        else:
            # ensure single-item tuple, itemgetter converts to atom in this case:
            col = icols[0]
            return FastDataFrame(itemgetter(*icols)(self.columns), map(lambda r: (r[col],), self.rows))

    def drop_duplicates(self, inplace=False):
        """Remove all duplicate rows.  Preserve order of first appearance.
        """
        rows = list(OrderedDict.fromkeys(self.rows))
        if inplace:
            self.rows = rows
            return self
        else:
            return FastDataFrame(self.columns, rows)

    def drop_nulls(self, inplace=False):
        """Remove all rows that have at least one None value.
        """
        df = inplace and self or FastDataFrame(self.columns, None)
        df.rows = filter(lambda r: None not in r, self.rows)
        return df

    def coerce_type(self, column, type, inplace=False):
        # TO DO: for now we do this after JSON conversion
        pass

    def concat(self, *dfs, inplace=False):
        """Concatenate 'self' with all data frames 'dfs' which are assumed to have the
        same arity, column types and order, but not necessarily the same column names.
        The result uses the column names of 'self'.
        """
        columns = self.columns
        norm_dfs = [self]
        for df in dfs:
            if df is None:
                continue
            if len(columns) != len(df.columns):
                raise KGTKException('unioned frames need to have the same number of columns')
            norm_dfs.append(df)
        if len(norm_dfs) == 1:
            return inplace and self or self.copy()
        else:
            df = inplace and self or FastDataFrame(columns, None)
            df.rows = itertools.chain(*norm_dfs)
            return df
        
    def union(self, *dfs, inplace=False):
        """Concatenate 'self' with all data frames 'dfs' and remove any duplicates.
        """
        df = self.concat(*dfs, inplace=inplace)
        df = df.drop_duplicates(inplace=inplace)
        return df

    def to_list(self):
        """Return rows as a list of tuples.
        """
        self.rows = list(self.rows)
        return self.rows

    def to_string(self):
        """Return a printable string representation of this frame.
        """
        out = io.StringIO()
        csvwriter = csv.writer(out, dialect=None, delimiter='\t',
                               quoting=csv.QUOTE_NONE, quotechar=None,
                               lineterminator='\n', escapechar=None)
        csvwriter.writerow(self.columns)
        csvwriter.writerows(self.rows)
        return out.getvalue()

    def to_records_dict(self):
        """Return a list of rows each represented as a dict of column/value pairs.
        """
        columns = self.columns
        return [{k: v for k, v in zip(columns, r)} for r in self.rows]

    def to_value_dict(self):
        """Convert a single-valued values data frame into a corresponding JSON dict.
        Assumes 'self' is a binary key/value frame where each key has exactly 1 value.
        Keys are assumed to be in column 0 and values in column 1.
        """
        return {k: v for k, v in self.rows}

    def to_values_dict(self):
        """Convert a multi-valued 'values_df' data frame into a corresponding JSON dict.
        Assumes 'values_df' is a binary key/value frame where each key can have multiple values.
        Keys are assumed to be in column 0 and values in column 1.
        """
        result = {}
        for k, v in self.rows:
            result.setdefault(k, []).append(v)
        return result


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
    
    FORMAT_FAST_DF = 'fdf'

    def execute_query(self, query, fmt=None, **kwds):
        """Query execution wrapper that handles the special fast dataframe format.
        """
        qfmt = fmt == self.FORMAT_FAST_DF and 'list' or fmt
        result = query.execute(fmt=qfmt, **kwds)
        if fmt == self.FORMAT_FAST_DF:
            result = FastDataFrame(query.get_result_header(), result)
        return result
    
    def get_node_labels(self, node, lang=None, fmt=None):
        """Retrieve all labels for 'node'.
        """
        query = self.get_config('NODE_LABELS_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), fmt=fmt)

    def get_node_aliases(self, node, lang=None, fmt=None):
        """Retrieve all aliases for 'node'.
        """
        query = self.get_config('NODE_ALIASES_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), fmt=fmt)

    def get_node_descriptions(self, node, lang=None, fmt=None):
        """Retrieve all descriptions for 'node'.
        """
        query = self.get_config('NODE_DESCRIPTIONS_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), fmt=fmt)
    
    def get_node_images(self, node, fmt=None):
        """Retrieve all images for 'node'.
        """
        query = self.get_config('NODE_IMAGES_QUERY')
        return self.execute_query(query, NODE=node, fmt=fmt)
    
    def get_node_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node1.
        """
        query = self.get_config('NODE_EDGES_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_inverse_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node2.
        """
        query = self.get_config('NODE_INVERSE_EDGES_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node1.
        """
        query = self.get_config('NODE_EDGE_QUALIFIERS_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)

    def get_node_inverse_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node2.
        """
        query = self.get_config('NODE_INVERSE_EDGE_QUALIFIERS_QUERY')
        return self.execute_query(query, NODE=node, LANG=self.get_lang(lang), FETCH_IMAGES=images, FETCH_FANOUTS=fanouts, fmt=fmt)


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
        if hasattr(result, 'to_string'):
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
            df = edges_df.project(self.KGTK_EDGE_COLUMNS)
            df.drop_duplicates(inplace=True)
            return df
        return None

    def collect_edge_label_labels(self, edges_df, lang=None, inverse=False):
        """Given an edges dataframe 'edges_df' collect all label strings for any referenced
        edge labels according to 'lang' and return a binary label_node/label_string frame.
        'inverse' indicates that 'edges_df' is an inverse edge frame which is ignored.
        """
        # TO DO: make this more efficient, but caching will smooth this out quickly
        if edges_df is not None:
            df = edges_df.project(self.LABEL_COLUMN)
            df.drop_duplicates(inplace=True)
            columns = (self.NODE1_COLUMN, self.LABEL_COLUMN)
            if len(df) == 0:
                return FastDataFrame(columns, [])
            labels = [self.get_node_labels(label, lang=lang, fmt='list') for label in df]
            return FastDataFrame(columns, itertools.chain(*labels))
        return None
    
    def collect_edge_node_labels(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node label columns and remove any duplicates.  'inverse' indicates that 
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.project([target_column, self.NODE_LABEL_COLUMN])
            df.drop_nulls(inplace=True)
            df.drop_duplicates(inplace=True)
            return df
        return None
    
    def collect_edge_node_images(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node image columns and remove any duplicates.  'inverse' indicates that 
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.project([target_column, self.NODE_IMAGE_COLUMN])
            df.drop_nulls(inplace=True)
            df.drop_duplicates(inplace=True)
            return df
        return None
    
    def collect_edge_node_fanouts(self, edges_df, inverse=False):
        """Given a full edges dataframe 'edges_df', project out the target node and
        node fanout columns and remove any duplicates.  'inverse' indicates that
        'edges_df' is an inverse edge frame.
        """
        if edges_df is not None:
            target_column = inverse and self.NODE1_COLUMN or self.NODE2_COLUMN
            df = edges_df.project([target_column, self.NODE_FANOUT_COLUMN])
            # TO DO: think about folding default fanout substitution into here:
            df.drop_nulls(inplace=True)
            df.drop_duplicates(inplace=True)
            # deferred to JSON conversion for now:
            #df.coerce_type(self.NODE_FANOUT_COLUMN, int, inplace=True)
            return df
        return None

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
        result_fmt = self.FORMAT_FAST_DF
        node_labels = self.get_node_labels(node, lang=lang, fmt=result_fmt)
        node_aliases = self.get_node_aliases(node, lang=lang, fmt=result_fmt)
        node_descs = self.get_node_descriptions(node, lang=lang, fmt=result_fmt)
        # the 'images' switch only controls 'node2' images, not images for 'node':
        node_images = self.get_node_images(node, fmt=result_fmt)
        
        edges = self.get_node_edges(node, lang=lang, images=images, fanouts=fanouts, fmt=result_fmt)
        quals = self.get_node_edge_qualifiers(node, lang=lang, images=images, fanouts=fanouts, fmt=result_fmt)

        inv_edges, inv_quals = None, None
        if inverse:
            inv_edges = self.get_node_inverse_edges(node, lang=lang, images=images, fanouts=fanouts, fmt=result_fmt)
            inv_quals = self.get_node_inverse_edge_qualifiers(node, lang=lang, images=images, fanouts=fanouts, fmt=result_fmt)
            
        if (node_labels.empty() and node_aliases.empty() and node_descs.empty() and
            edges.empty() and (inv_edges is None or inv_edges.empty())):
            # 'node' doesn't exist or nothing is known about it:
            return None

        all_edges = self.collect_edges(edges).union(self.collect_edges(inv_edges))
        all_quals = self.collect_edges(quals).union(self.collect_edges(inv_quals))

        all_labels = node_labels.union(
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
            all_images = node_images.union(
                self.collect_edge_node_images(edges),
                self.collect_edge_node_images(inv_edges, inverse=True),
                self.collect_edge_node_images(quals),
                self.collect_edge_node_images(inv_quals))

        all_fanouts = None
        if fanouts:
            all_fanouts = self.collect_edge_node_fanouts(edges).union(
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
            'label': node_data['labels'].project(self.NODE_LABEL_COLUMN).to_list(),
            'alias': node_data['aliases'].project(self.NODE_ALIAS_COLUMN).to_list(),
            'description':
                     node_data['descriptions'].project(self.NODE_DESCRIPTION_COLUMN).to_list(),
            'image': node_data['images'].project(self.NODE_IMAGE_COLUMN).to_list(),
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
                "database": os.path.basename(self.api.sql_store.dbfile),
                "version": "2021-08-01",
            },
            "objects": objects,
        }
        return node_data


    ### Top level:

    # We do LRU-cache this one also, since conversion from cached query results
    # to data frames and JSON takes about 20% of overall query time.
    
    @lru_cache(maxsize=LRU_CACHE_SIZE)
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
