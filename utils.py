import operator

import json

ASCENDING = 'asc'
DESCENDING = 'desc'

sort_order_dict = {
    "wikibase-form": ASCENDING,
    "commonsMedia": ASCENDING,
    "time": DESCENDING,
    "string": ASCENDING,
    "monolingualtext": ASCENDING,
    "external-id": ASCENDING,
    "wikibase-item": ASCENDING,
    "math": ASCENDING,
    "geo-shape": ASCENDING,
    "quantity": ASCENDING,
    "musical-notation": ASCENDING,
    "wikibase-lexeme": ASCENDING,
    "wikibase-property": ASCENDING,
    "url": ASCENDING,
    "tabular-data": ASCENDING,
    "wikibase-sense": ASCENDING,
    "globe-coordinate": ASCENDING
}


def create_sort_metadata(property_qualifiers_stats_file):
    pstats = json.load(open(property_qualifiers_stats_file))

    sort_metadata = {}
    for property in pstats:
        key = property
        sort_metadata[key] = sort_order_dict.get(pstats[property]['datatype'])
        qualifiers = pstats[property].get('qualifiers', {})
        for q in qualifiers:
            key = f'{property}_{q}'
            sort_metadata[key] = sort_order_dict.get(qualifiers[q]['datatype'])
    return sort_metadata


def create_sort_metadata_ajax(property_qualifiers_stats_file):
    pstats = json.load(open(property_qualifiers_stats_file))

    sort_metadata = {}
    for property in pstats:
        key = property
        p_datatype = pstats[property]['datatype']
        sort_metadata[key] = sort_order_dict.get(p_datatype)
        qualifiers = pstats[property].get('qualifiers', {})
        if not qualifiers:
            sort_metadata[key] = {
                'sort_by': sort_order_dict[p_datatype],
                'value_counts': pstats[key]['value_counts'],
                'property_datatype': p_datatype,
                'qratio': 0.0
            }
        else:
            top_qualifier = \
                sorted(qualifiers.items(), key=lambda x: operator.getitem(x[1], 'value_counts'), reverse=True)[0]
            sort_metadata[key] = {
                'qualifier': top_qualifier[0],
                'sort_by': sort_order_dict[top_qualifier[1]['datatype']],
                'qualifier_value_counts': top_qualifier[1]['value_counts'],
                'property_value_counts': pstats[key]['value_counts'],
                'property_datatype': p_datatype,
                'qualifier_datatype': top_qualifier[1]['datatype'],
                'qratio': float(top_qualifier[1]['value_counts']) / float(pstats[key]['value_counts'])
            }

    # sorted_by_q_ratio = sorted(sort_metadata.items(), key=lambda x: operator.getitem(x[1], 'qratio'), reverse=True)

    return sort_metadata


def run_both(property_qualifiers_stats_file, sort_metadata_file):
    sync = create_sort_metadata(property_qualifiers_stats_file)
    ajax = create_sort_metadata_ajax(property_qualifiers_stats_file)
    sm = {
        'ajax_properties': ajax,
        'sync_properties': sync
    }
    open(sort_metadata_file, 'w').write(json.dumps(sm, indent=2))


# create_sort_metadata('property_qualifier_stats.json', 'sort_metadata.json')
# create_sort_metadata_ajax('property_qualifier_stats.json', 'sort_metadata_ajax_properties.json')
run_both('property_qualifier_stats.json', 'properties_sort_metadata.json')
