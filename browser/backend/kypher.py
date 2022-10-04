"""
Kypher backend support for the KGTK browser and visualizer.
"""

import io
from functools import lru_cache
import itertools

from browser.backend.fastdf import FastDataFrame
import browser.backend.format as fmt


# TO DO:
# - reimplement the "language backoff" we had previously; currently we don't
#   substitute labels, etc. from other languages if the desired language is empty
# - handle inverse edge fanouts which are different than the forward fanouts
#   we already collect of node1's on inverse edges; this would require a separate
#   entry in the JSON object so we can distinguish them


class BrowserBackend(object):
    """
    KGTK browser backend using the Kypher graph cache and query infrastructure.
    """

    LRU_CACHE_SIZE = 1000
    LANGUAGE_ANY = 'any'

    def __init__(self, api, formatter=None):
        self.api = api

        # use triple format used by visualizer by default:
        self.formatter = formatter or fmt.JsonTripleFormat()

    def set_app_config(self, app):
        # import app config on top of api object config:
        for key, value in app.config.items():
            self.api.kapi.set_config(key, value)

    def get_config(self, key, dflt=None):
        """Access a configuration value for 'key' from the current configuration.
        """

        return self.api.kapi.get_config(key, dflt=dflt)

    def get_lang(self, lang=None):
        return lang or self.get_config('DEFAULT_LANGUAGE', self.LANGUAGE_ANY)

    def get_lock(self):
        """Return the lock object.
        """
        return self.api.kapi.get_lock()

    def __enter__(self):
        """Lock context manager for 'with ... as backend:' idiom.
        """
        self.api.kapi.__enter__()
        return self

    def __exit__(self, *_exc):
        self.api.kapi.__exit__()

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
        query = self.api.NODE_LABELS_QUERY(node, self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def get_node_aliases(self, node, lang=None, fmt=None):
        """Retrieve all aliases for 'node'.
        """
        query = self.api.NODE_ALIASES_QUERY(node, self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def get_node_descriptions(self, node, lang=None, fmt=None):
        """Retrieve all descriptions for 'node'.
        """
        query = self.api.NODE_DESCRIPTIONS_QUERY(node, self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def get_node_images(self, node, fmt=None):
        """Retrieve all images for 'node'.
        """
        query = self.api.NODE_IMAGES_QUERY(node)
        return self.execute_query(query, fmt=fmt)

    def get_node_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node1.
        """
        query = self.api.NODE_EDGES_QUERY(node, self.get_lang(lang), images, fanouts)
        return self.execute_query(query, fmt=fmt)

    def get_node_inverse_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all edges that have 'node' as their node2.
        """
        query = self.api.NODE_INVERSE_EDGES_QUERY(node, self.get_lang(lang), images, fanouts)
        return self.execute_query(query, fmt=fmt)

    def get_node_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node1.
        """
        query = self.api.NODE_EDGE_QUALIFIERS_QUERY(node, self.get_lang(lang), images, fanouts)
        return self.execute_query(query, fmt=fmt)

    def get_node_inverse_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve all qualifiers for edges that have 'node' as their node2.
        """
        query = self.api.NODE_INVERSE_EDGE_QUALIFIERS_QUERY(node, self.get_lang(lang), images, fanouts)
        return self.execute_query(query, fmt=fmt)

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

    def collect_edges(self, edges_df):
        """Given a full edges dataframe 'edges_df' including target node info columns,
        project out the core edge columns and remove any duplicates.
        """
        if edges_df is not None:
            df = edges_df.project(fmt.KGTK_EDGE_COLUMNS)
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
            df = edges_df.project(fmt.LABEL_COLUMN)
            df.drop_duplicates(inplace=True)
            columns = (fmt.NODE1_COLUMN, fmt.LABEL_COLUMN)
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
            target_column = inverse and fmt.NODE1_COLUMN or fmt.NODE2_COLUMN
            df = edges_df.project([target_column, fmt.NODE_LABEL_COLUMN])
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
            target_column = inverse and fmt.NODE1_COLUMN or fmt.NODE2_COLUMN
            df = edges_df.project([target_column, fmt.NODE_IMAGE_COLUMN])
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
            target_column = inverse and fmt.NODE1_COLUMN or fmt.NODE2_COLUMN
            df = edges_df.project([target_column, fmt.NODE_FANOUT_COLUMN])
            # TO DO: think about folding default fanout substitution into here:
            df.drop_nulls(inplace=True)
            df.drop_duplicates(inplace=True)
            # deferred to JSON conversion for now:
            # df.coerce_type(fmt.NODE_FANOUT_COLUMN, int, inplace=True)
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
            inv_quals = self.get_node_inverse_edge_qualifiers(node, lang=lang, images=images, fanouts=fanouts,
                                                              fmt=result_fmt)

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

    ### Top level:

    # We do LRU-cache this one also, since conversion from cached query results
    # to data frames and JSON takes about 20% of overall query time.

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def get_all_node_data(self, node, lang=None, images=False, fanouts=False, inverse=False, formatter=None):
        """Return all graph and label data for 'node' and return it as a
        dict/JSON object produced by 'self.formatter'.  Return None if 'node'
        does not exist in the graph.  If 'images' and/or 'fanouts' is True
        fetch and add the respective node2 descriptor data.  If 'inverse'
        is True, also include edges (and their associated info) that have
        'node' as their node2.
        """
        node_data = self.get_node_data_frames(node, lang=lang, images=images, fanouts=fanouts, inverse=inverse)
        if node_data is None:
            return None
        else:
            if formatter is None:
                formatter = self.formatter
            return formatter.format_node_data(node_data)

    # Support for the revised browser:
    def rb_get_node_labels(self, node, fmt=None):
        """Retrieve all labels for 'node'.

        Node names are assumed to always be in upper case in the database and
        the search is always assumed to be case-insensitive.  We don't have
        seperate exact case/case-insensitive queries for this retreival.

        This search method supports rb_get_kb_query(), which generates a list of
        candidate nodes.  The search must be fast.
        """

        # Raise the case of the label to implement a case-insensitive search.
        node = node.upper()
        query = self.api.MATCH_ITEMS_EXACTLY_QUERY(node)

        return self.execute_query(query, fmt=fmt)

    # def rb_get_nodes_with_label(self, label, lang=None, fmt=None, ignore_case: bool = False):
    #     """Retrieve all nodes with label 'label'.
    #
    #     This search method supports rb_get_kb_query(), which generates a list
    #     of candidate nodes.  The label is searched for a complete match, which
    #     may or may not be case-insensitive.  The search must be fast.
    #     """
    #
    #     if ignore_case:
    #         # Raise the case of the label to implement a case-insensitive search.
    #         label = label.upper()
    #         query = self.api.RB_NODES_WITH_UPPER_LABEL_QUERY
    #
    #     else:
    #         # This query relies on making an exact match for the label.
    #         query = self.api.RB_NODES_WITH_LABEL_QUERY(label, self.get_lang(lang))
    #
    #     return self.execute_query(query, fmt=fmt)

    # @lru_cache(maxsize=LRU_CACHE_SIZE)
    # def rb_get_nodes_starting_with(self, node, limit: int = 20, lang=None, fmt=None):
    #     """Retrieve nodes and labels for all nodes starting with 'node'.
    #
    #     Node names are assumed to always be in upper case in the database and
    #     the search is always assumed to be case-insensitive.  We don't have
    #     seperate exact case/case-insensitive queries for this retreival.
    #
    #     This search method supports rb_get_kb_query(), which generates a list of
    #     candidate nodes.  The search must be fast.
    #     """
    #
    #     # Raise the case of the label to implement a case-insensitive search.
    #     node = node.upper()
    #     query = self.api.MATCH_ITEM_TEXTSEARCH_QUERY
    #
    #     # Protect against glob metacharacters in `node` (`*`, `[...]`, `?`]
    #     safe_node: str = node.translate({ord(i): None for i in '*[?'})
    #
    #     return self.execute_query(query, NODE=safe_node, LIMIT=limit, LANG=self.get_lang(lang), fmt=fmt)

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def search_labels_exactly(self, label, limit: int = 20, lang=None, fmt=None):
        """Retrieve nodes and labels for all nodes with labels starting with 'label'.

        This search method supports rb_get_kb_query(), which generates a list of
        candidate nodes. The label is searched for a complete match, which
        may or may not be case-insensitive.  The search must be fast.
        """

        # Raise the case of the label to implement a case-insensitive search.

        _lang = self.get_lang(lang)

        # Protect against glob metacharacters in `label` (`*`, `[...]`, `?`]
        safe_label: str = label.translate({ord(i): None for i in '*[?'})

        search_label = f"'{safe_label}'@{_lang}".upper()

        query = self.api.MATCH_UPPER_LABELS_EXACTLY_QUERY(search_label, limit)

        return self.execute_query(query, fmt=fmt)

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def search_labels_textlike(self, label, limit: int = 20, lang=None, fmt=None):
        """Retrieve nodes and labels for all nodes with labels like 'label'.

         The label is searched for a like match, which is case-insensitive.
           The search must be fast.
        """

        # Protect against glob metacharacters in `label` (`*`, `[...]`, `?`]
        safe_label: str = label.translate({ord(i): None for i in '*[?'})

        query = self.api.MATCH_LABELS_TEXTLIKE_QUERY(safe_label, self.get_lang(lang), limit)

        return self.execute_query(query, fmt=fmt)

    @lru_cache(maxsize=LRU_CACHE_SIZE)
    def search_labels(self, label, limit: int = 20, lang=None, fmt=None):
        """Retrieve nodes and labels for all nodes with labels starting with 'label'.

        This search method supports rb_get_kb_query(), which generates a list of
        candidate nodes. The label is searched for a complete match, which
        may or may not be case-insensitive.  The search must be fast.
        """

        # Protect against glob metacharacters in `label` (`*`, `[...]`, `?`]
        safe_label: str = label.translate({ord(i): None for i in '*[?'})

        query = self.api.MATCH_LABELS_TEXTSEARCH_QUERY(safe_label, self.get_lang(lang), limit)

        return self.execute_query(query, fmt=fmt)

    def rb_get_node_edges(self, node, lang=None, images=False, fanouts=False, fmt=None, limit: int = 10000,
                          lc_properties: str = None):
        """Retrieve all edges that have 'node' as their node1.
        """
        if lc_properties is not None:
            # query = self.api.RB_NODE_EDGES_CONDITIONAL_QUERY(node, hc_properties, self.get_lang(lang), limit)
            query = self.api.RB_NODE_EDGES_CONDITIONAL_QUERY_2(node, lc_properties, self.get_lang(lang), limit)
            return self.execute_query(query, NODE=node, PROPS=lc_properties, fmt=fmt)
        else:
            query = self.api.RB_NODE_EDGES_QUERY(node, self.get_lang(lang), limit)
            return self.execute_query(query, fmt=fmt)

    # def rb_get_node_one_property_edges(self, node, property: str, limit: int, skip: int, lang=None, images=False,
    #                                    fanouts=False, fmt=None):
    #     """Retrieve all edges that have 'node' as their node1 for property=property
    #     """
    #
    #     query = self.api.RB_NODE_EDGES_ONE_PROPERTY_QUERY(node, property, self.get_lang(lang), skip, limit)
    #     return self.execute_query(query, fmt=fmt)

    def rb_get_node_one_property_with_qualifiers_edges(self,
                                                       node,
                                                       property: str,
                                                       limit: int,
                                                       skip: int,
                                                       qualifier_property: str = None,
                                                       lang=None,
                                                       sort_order: str = 'asc',
                                                       sort_by: str = 'qn2',
                                                       is_sort_by_quantity: bool = False,
                                                       fmt=None):
        """Retrieve all edges that have 'node' as their node1 for property=property with qualifiers
        """

        query = self.api.RB_NODE_EDGES_ONE_PROPERTY_WITH_QUALIFIERS_QUERY(node,
                                                                          property,
                                                                          self.get_lang(lang),
                                                                          skip,
                                                                          limit,
                                                                          sort_order,
                                                                          qualifier_property,
                                                                          sort_by,
                                                                          is_sort_by_quantity)
        return self.execute_query(query, fmt=fmt)

    def rb_get_node_one_property_related_edges(self, node, property: str, limit: int, skip: int, lang=None, fmt=None):
        """Retrieve all edges that have 'node' as their node1 for property=property
        """

        query = self.api.RB_NODE_RELATED_EDGES_ONE_PROPERTY_QUERY(node, property, self.get_lang(lang), skip, limit)
        return self.execute_query(query, fmt=fmt)

    def rb_get_node_multiple_properties_related_edges(self, node, lc_properties: str, limit: int, lang=None, fmt=None):
        """Retrieve all edges that have 'node' as their node1 for property in lc_properties
        """

        query = self.api.RB_NODE_RELATED_EDGES_MULTIPLE_PROPERTIES_QUERY(node, lc_properties, self.get_lang(lang),
                                                                         limit)
        return self.execute_query(query, NODE=node,PROPS=lc_properties, fmt=fmt)

    def rb_get_node_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None, limit: int = 10000):
        """Retrieve all edge qualifiers for edges that have 'node' as their node1.
        """
        query = self.api.RB_NODE_EDGE_QUALIFIERS_QUERY(node, self.get_lang(lang), limit)
        return self.execute_query(query, fmt=fmt)

    def rb_get_node_edge_qualifiers_by_edge_id(self, edge_id, lang=None, images=False, fanouts=False, fmt=None,
                                               limit: int = 10000):
        """Retrieve all edge qualifiers for the edge with edge ID edge_id..
        """
        query = self.api.RB_NODE_EDGE_QUALIFIERS_BY_EDGE_ID_QUERY(edge_id, self.get_lang(lang), limit)
        return self.execute_query(query, fmt=fmt)

    def rb_get_node_edge_qualifiers_in(self, id_list, lang=None, images=False, fanouts=False, fmt=None,
                                       limit: int = 10000):
        """Retrieve all edge qualifiers for edges that have their id in ID_LIST.
        """
        query = self.api.GET_RB_NODE_EDGE_QUALIFIERS_IN_QUERY(id_list)
        results = self.execute_query(query, LIMIT=limit, LANG=self.get_lang(lang), fmt=fmt)
        query.clear()  # Since we don't plan to re-issue this query, release its resources.
        return results

    # def rb_get_node_inverse_edges(self, node, lang=None, images=False, fanouts=False, fmt=None):
    #     """Retrieve all edges that have 'node' as their node2.
    #     """
    #     query = self.api.RB_NODE_INVERSE_EDGES_QUERY(node, self.get_lang(lang))
    #     return self.execute_query(query, fmt=fmt)

    # def rb_get_node_inverse_edge_qualifiers(self, node, lang=None, images=False, fanouts=False, fmt=None):
    #     """Retrieve all edge qualifiers for edges that have 'node' as their node2.
    #     """
    #     query = self.api.RB_NODE_INVERSE_EDGE_QUALIFIERS_QUERY(node, self.get_lang(lang))
    #     return self.execute_query(query, fmt=fmt)

    # def rb_get_node_categories(self, node, lang=None, images=False, fanouts=False, fmt=None):
    #     """Retrieve all categories that have 'node' as their node2.
    #     """
    #     query = self.api.RB_NODE_CATEGORIES_QUERY(node, self.get_lang(lang))
    #     return self.execute_query(query, fmt=fmt)

    def rb_get_image_formatter(self, node, lang=None, fmt=None):
        """Retrieve the first matching image formatter.
        """
        query = self.api.RB_IMAGE_FORMATTER_QUERY(node)
        return self.execute_query(query, fmt=fmt)

    def rb_get_subproperty_relationships(self, lang=None, fmt=None):
        """Retrieve all subproperty relationships.
        """
        query = self.api.RB_SUBPROPERTY_RELATIONSHIPS_QUERY(self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def rb_get_language_labels(self, code, lang=None, images=False, fanouts=False, fmt=None):
        """Retrieve language names for language code 'code'.
        """
        query = self.api.RB_LANGUAGE_LABELS_QUERY(code, self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def get_classviz_edge_results(self, node, fmt=FORMAT_FAST_DF):

        node = node.upper()
        query = self.api.GET_CLASS_VIZ_EDGE_QUERY(node)

        return self.execute_query(query, fmt=fmt)

    def get_classviz_node_results(self, node, fmt=FORMAT_FAST_DF):

        node = node.upper()
        query = self.api.GET_CLASS_VIZ_NODE_QUERY(node)

        return self.execute_query(query, fmt=fmt)

    def get_property_values_count_results(self, node, lang, fmt=None):
        query = self.api.GET_PROPERTY_VALUES_COUNT_QUERY(node, self.get_lang(lang))
        return self.execute_query(query, fmt=fmt)

    def get_incoming_edges_count_results(self, node, lang, properties_to_hide_str, fmt=None):
        query = self.api.GET_INCOMING_EDGES_COUNT_QUERY(node, self.get_lang(lang), properties_to_hide_str)
        return self.execute_query(query, fmt=fmt)
