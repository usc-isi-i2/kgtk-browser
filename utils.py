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


def create_sort_metadata(property_qualifiers_stats_file, sort_metadata_file):
    pstats = json.load(open(property_qualifiers_stats_file))

    sort_metadata = {}
    for property in pstats:
        key = property
        sort_metadata[key] = sort_order_dict.get(pstats[property]['datatype'])
        qualifiers = pstats[property].get('qualifiers', {})
        for q in qualifiers:
            key = f'{property}_{q}'
            sort_metadata[key] = sort_order_dict.get(qualifiers[q]['datatype'])
    open(sort_metadata_file, 'w').write(json.dumps(sort_metadata))

# create_sort_metadata('property_qualifier_stats.json', 'sort_metadata.json')
