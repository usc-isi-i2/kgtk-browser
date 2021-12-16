# kgtk-browser

Download the codebase and setup the python environment. In a terminal run the following commands ,

```
git clone https://github.com/usc-isi-i2/kgtk-browser
cd kgtk-browser
git checkout dev
conda create -n kgtk-env python=3.9
conda activate kgtk-env
pip install -r requirements.txt
```

## Prerequisites

The following files are required ,

- labels.en.tsv.gz
- aliases.en.tsv.gz
- descriptions.en.tsv.gz
- claims.tsv.gz
- metadata.property.datatypes.tsv.gz
- qualifiers.tsv.gz
- metadata.pagerank.undirected.tsv.gz
- derived.isastar.tsv.gz

The files `metadata.pagerank.undirected.tsv.gz` `derived.isastar.tsv.gz` and can be created by running this [notebook](https://github.com/usc-isi-i2/kgtk/blob/dev/use-cases/Wikidata%20Useful%20Files.ipynb)

## SQLITE or ElasticSearch

KGTK Browser can be setup with either a SQLITE DB Cache file or a [KGTK Search api](https://github.com/usc-isi-i2/kgtk-search). We'll describe both options.

### Building a SQLITE Cache DB file
- Execute [this](https://github.com/usc-isi-i2/kgtk-browser/blob/dev/KGTK-Query-Text-Search-Setup.ipynb) notebook.
- Set parameters: `create_db = 'yes'` and `create_es = 'no'` to create only the SQLITE DB Cache file.
- Setup other parameters as described in the notebook.

### Setting up ElasticSearch Index and KGTK Search API
- Execute [this](https://github.com/usc-isi-i2/kgtk-browser/blob/dev/KGTK-Query-Text-Search-Setup.ipynb) notebook.
- Set parameters: `create_db = 'no'` and `create_es = 'yes'` to create and load the ElasticSearch index.
- Setup other parameters as described in the notebook.
- This will result in a ElasticSearch index which can now be used to setup the [KGTK Search api](https://github.com/usc-isi-i2/kgtk-search).
- Setup the [KGTK Search API](https://github.com/usc-isi-i2/kgtk-search)

## Running the web app using SQLITE Cache File

Update the parameter `GRAPH_CACHE` in the file `kgtk_browser_config.py` and set it to the cache file location as created in the step `Building a SQLITE Cache DB file`.

Ensure that recent versions of "npm" and "node" are installed:

```
npm --version
7.20.3
```
```
node --version
v16.6.2
````

The following steps will start a server on your local host at the default port (5000):

Build the frontend files ,

```
cd app
export REACT_APP_FRONTEND_URL='/browser'
export REACT_APP_BACKEND_URL=''

npm run build
```

Start the server using `kgtk browse` ,

```
cd ..
export PYTHONPATH=$PYTHONPATH:$PWD
kgtk browse --host localhost --port 5000
```

NOTE: using development mode turns on JSON pretty-printing which about
doubles the size of response objects.  For faster server response,
set `FLASK_ENV` to `production`.


## Design and status

The top-level entry points are defined at the end of
`kgtk_browser_app.py`.  The main one to use is `get_all_node_data`
(example below) which takes a node as an argument and retrieves all
relevant edges, qualifier edges, node labels and descriptions as well
as a labels dictionary for all referenced properties and objects.
An optional `lang` argument is also available, see below.

The response time even for large nodes such as Q30 should be a
fraction of a second.  If it takes significantly longer, there is
likely something wrong in the setup somewhere.

Query results are transmitted as a set of JSON-LD objects, but there
is no requirement to use JSON-LD.  The main import of that is that
each object has a `@type` field that defines its type and the set of
relevant slots (but there is no actual context definition at the
moment, `kgtk_objects.jsonld` is just a stub).

All literals are currently transmitted with their KGTK quote and
escape characters.  Those should be easy to remove but if that is an
issue we can remove them on the server which will increase response
time.  Also that will make it more difficult to transmit language
tags, for example.

All labels, aliases, descriptions, etc. are transmitted as
multi-valued fields that have values in one or more languages.  The
optional `lang` argument can be used to select which language to
prefer and defaults to `en` (English).  An `any` language tag can be
used to return strings in all languages.  If a requested language does
not exist for a label or description string, a fallback language will
be used which can be configured via the `DEFAULT_LANGUAGE` property
(which defaults to `en`).  If all else fails (e.g., no label exists at
all), the node name itself will be used as a fallback.  Language tags
are matched as prefixes, so `zh` matches `zh-cn` and other variants.

Sorting values for best presentation still needs to be implemented.

The configuration file allows simple definition of which input files
and edge labels to use to define labels, descriptions, images, etc.
This will need to be generalized for more flexibility, e.g., by
allowing the specification of queries for certain aspects of the data.

There are two optional request arguments `images` and `fanout` which
optionally retrieve image links and fanout of any `node2`s in the
basic (non-qualifier) edges retrieved.  This data can be used for
presentation or to provide an indication of how much data a node is
connected to.

Construction and transmission of property data types, site links and other
information still needs to be implemented.


## Examples

The example below shows how to query the server.  In development mode
Flask pretty-prints the JSON which makes things more verbose.  We
retrieve both images and fanouts here to document the corresponding
objects.

```
http://127.0.0.1:5000/kgtk/browser/backend/get_all_node_data?node=Q100104271&lang=en&images=true&fanouts=true&inverse=false

{
  "@context": [
    "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
  ], 
  "@type": "kgtk_object_collection", 
  "meta": {
    "@type": "kgtk_meta_info", 
    "database": "wikidata-20210215-dwd-browser.2021-07-09T19:19.sqlite3.db", 
    "version": "2021-08-01"
  }, 
  "objects": [
    {
      "@id": "Q100104271", 
      "@type": "kgtk_node", 
      "alias": [], 
      "description": [
        "'researcher'@en"
      ], 
      "edges": [
        {
          "@id": "Q100104271-P101-Q11660-de2f2bf2-0", 
          "@type": "kgtk_edge", 
          "o": "Q11660", 
          "p": "P101", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P106-Q1650915-349d2437-0", 
          "@type": "kgtk_edge", 
          "o": "Q1650915", 
          "p": "P106", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P108-Q4614-3d59a6b0-0", 
          "@type": "kgtk_edge", 
          "o": "Q4614", 
          "p": "P108", 
          "qualifiers": [
            {
              "@id": "Q100104271-P108-Q4614-3d59a6b0-0-P580-39ff98-0", 
              "@type": "kgtk_edge", 
              "o": "^1988-01-01T00:00:00Z/9", 
              "p": "P580", 
              "s": "Q100104271-P108-Q4614-3d59a6b0-0"
            }
          ], 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P1416-Q6030821-6b7a061a-0", 
          "@type": "kgtk_edge", 
          "o": "Q6030821", 
          "p": "P1416", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P1960-528436-670ba1f6-0", 
          "@type": "kgtk_edge", 
          "o": "\"U1A6iBMAAAAJ\"", 
          "p": "P1960", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P21-Q6581097-d2bd3064-0", 
          "@type": "kgtk_edge", 
          "o": "Q6581097", 
          "p": "P21", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P31-Q5-f20b8654-0", 
          "@type": "kgtk_edge", 
          "o": "Q5", 
          "p": "P31", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P69-Q1569421-0e7acaa4-0", 
          "@type": "kgtk_edge", 
          "o": "Q1569421", 
          "p": "P69", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P69-Q190080-f617727b-0", 
          "@type": "kgtk_edge", 
          "o": "Q190080", 
          "p": "P69", 
          "qualifiers": [
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P582-f13b45-0", 
              "@type": "kgtk_edge", 
              "o": "^1987-01-01T00:00:00Z/9", 
              "p": "P582", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P580-aa16a3-0", 
              "@type": "kgtk_edge", 
              "o": "^1980-01-01T00:00:00Z/9", 
              "p": "P580", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P512-Q752297-0", 
              "@type": "kgtk_edge", 
              "o": "Q752297", 
              "p": "P512", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P812-Q21198-0", 
              "@type": "kgtk_edge", 
              "o": "Q21198", 
              "p": "P812", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }
          ], 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P735-Q15897419-923d6b40-0", 
          "@type": "kgtk_edge", 
          "o": "Q15897419", 
          "p": "P735", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P856-b56474-4cbdfa31-0", 
          "@type": "kgtk_edge", 
          "o": "\"https://usc-isi-i2.github.io/szekely/\"", 
          "p": "P856", 
          "s": "Q100104271"
        }
      ], 
      "image": [], 
      "label": [
        "'Pedro Szekely'@en"
      ]
    }, 
    {
      "@id": "kgtk_object_labels_Q100104271", 
      "@type": "kgtk_object_labels", 
      "labels": {
        "P101": [
          "'field of work'@en"
        ], 
        "P106": [
          "'occupation'@en"
        ], 
        "P108": [
          "'employer'@en"
        ], 
        "P1416": [
          "'affiliation'@en"
        ], 
        "P1960": [
          "'Google Scholar author ID'@en"
        ], 
        "P21": [
          "'sex or gender'@en"
        ], 
        "P31": [
          "'instance of'@en"
        ], 
        "P512": [
          "'academic degree'@en"
        ], 
        "P580": [
          "'start time'@en"
        ], 
        "P582": [
          "'end time'@en"
        ], 
        "P69": [
          "'educated at'@en"
        ], 
        "P735": [
          "'given name'@en"
        ], 
        "P812": [
          "'academic major'@en"
        ], 
        "P856": [
          "'official website'@en"
        ], 
        "Q100104271": [
          "'Pedro Szekely'@en"
        ], 
        "Q11660": [
          "'artificial intelligence'@en"
        ], 
        "Q1569421": [
          "'University of the Andes'@en"
        ], 
        "Q15897419": [
          "'Pedro'@en"
        ], 
        "Q1650915": [
          "'researcher'@en"
        ], 
        "Q190080": [
          "'Carnegie Mellon University'@en"
        ], 
        "Q21198": [
          "'computer science'@en"
        ], 
        "Q4614": [
          "'University of Southern California'@en"
        ], 
        "Q5": [
          "'human'@en"
        ], 
        "Q6030821": [
          "'Information Sciences Institute'@en"
        ], 
        "Q6581097": [
          "'male'@en"
        ], 
        "Q752297": [
          "'Doctor of Philosophy'@en"
        ]
      }
    }, 
    {
      "@id": "kgtk_object_images_Q100104271", 
      "@type": "kgtk_object_images", 
      "images": {
        "Q1569421": [
          "\"Universidad de los Andes (3326108271).jpg\""
        ], 
        "Q190080": [
          "\"CMU campus Cathedral Learning background.jpg\""
        ], 
        "Q4614": [
          "\"052607-016-BovardHall-USC.jpg\""
        ], 
        "Q5": [
          "\"Anterior view of human female and male, with labels.svg\""
        ]
      }
    }, 
    {
      "@id": "kgtk_object_fanouts_Q100104271", 
      "@type": "kgtk_object_fanouts", 
      "fanouts": {
        "Q11660": 63, 
        "Q1569421": 32, 
        "Q15897419": 16, 
        "Q1650915": 22, 
        "Q190080": 70, 
        "Q21198": 53, 
        "Q4614": 71, 
        "Q5": 70, 
        "Q6030821": 14, 
        "Q6581097": 17, 
        "Q752297": 13
      }
    }
  ]
}
```

Here is a slightly different example that requests a different
language and also adds inverse links.  For some of the labels a
Spanish version does not exist and the current version of the backend
does not try to substitute a different language instead.  Inverse
edges are not explicitly marked, they simply reference the given
node as their object or node2 value.

CAREFUL: inverse links might have very high fanout in KGs such
as Wikidata, so be sure to request them with proper caution.

```
http://127.0.0.1:5000/kgtk/browser/backend/get_all_node_data?node=Q100104271&lang=es&images=true&fanouts=true&inverse=true

{
  "@context": [
    "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
  ], 
  "@type": "kgtk_object_collection", 
  "meta": {
    "@type": "kgtk_meta_info", 
    "database": "wikidata-20210215-dwd-browser.2021-07-09T19:19.sqlite3.db", 
    "version": "2021-08-01"
  }, 
  "objects": [
    {
      "@id": "Q100104271", 
      "@type": "kgtk_node", 
      "alias": [], 
      "description": [], 
      "edges": [
        {
          "@id": "Q100104271-P101-Q11660-de2f2bf2-0", 
          "@type": "kgtk_edge", 
          "o": "Q11660", 
          "p": "P101", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P106-Q1650915-349d2437-0", 
          "@type": "kgtk_edge", 
          "o": "Q1650915", 
          "p": "P106", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P108-Q4614-3d59a6b0-0", 
          "@type": "kgtk_edge", 
          "o": "Q4614", 
          "p": "P108", 
          "qualifiers": [
            {
              "@id": "Q100104271-P108-Q4614-3d59a6b0-0-P580-39ff98-0", 
              "@type": "kgtk_edge", 
              "o": "^1988-01-01T00:00:00Z/9", 
              "p": "P580", 
              "s": "Q100104271-P108-Q4614-3d59a6b0-0"
            }
          ], 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P1416-Q6030821-6b7a061a-0", 
          "@type": "kgtk_edge", 
          "o": "Q6030821", 
          "p": "P1416", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P1960-528436-670ba1f6-0", 
          "@type": "kgtk_edge", 
          "o": "\"U1A6iBMAAAAJ\"", 
          "p": "P1960", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P21-Q6581097-d2bd3064-0", 
          "@type": "kgtk_edge", 
          "o": "Q6581097", 
          "p": "P21", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P31-Q5-f20b8654-0", 
          "@type": "kgtk_edge", 
          "o": "Q5", 
          "p": "P31", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P69-Q1569421-0e7acaa4-0", 
          "@type": "kgtk_edge", 
          "o": "Q1569421", 
          "p": "P69", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P69-Q190080-f617727b-0", 
          "@type": "kgtk_edge", 
          "o": "Q190080", 
          "p": "P69", 
          "qualifiers": [
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P582-f13b45-0", 
              "@type": "kgtk_edge", 
              "o": "^1987-01-01T00:00:00Z/9", 
              "p": "P582", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P580-aa16a3-0", 
              "@type": "kgtk_edge", 
              "o": "^1980-01-01T00:00:00Z/9", 
              "p": "P580", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P512-Q752297-0", 
              "@type": "kgtk_edge", 
              "o": "Q752297", 
              "p": "P512", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@id": "Q100104271-P69-Q190080-f617727b-0-P812-Q21198-0", 
              "@type": "kgtk_edge", 
              "o": "Q21198", 
              "p": "P812", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }
          ], 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P735-Q15897419-923d6b40-0", 
          "@type": "kgtk_edge", 
          "o": "Q15897419", 
          "p": "P735", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q100104271-P856-b56474-4cbdfa31-0", 
          "@type": "kgtk_edge", 
          "o": "\"https://usc-isi-i2.github.io/szekely/\"", 
          "p": "P856", 
          "s": "Q100104271"
        }, 
        {
          "@id": "Q96625619-P50-Q100104271-574cdc3e-0", 
          "@type": "kgtk_edge", 
          "o": "Q100104271", 
          "p": "P50", 
          "qualifiers": [
            {
              "@id": "Q96625619-P50-Q100104271-574cdc3e-0-P1932-318dd4-0", 
              "@type": "kgtk_edge", 
              "o": "\"Pedro Szekely\"", 
              "p": "P1932", 
              "s": "Q96625619-P50-Q100104271-574cdc3e-0"
            }, 
            {
              "@id": "Q96625619-P50-Q100104271-574cdc3e-0-P1545-2bf175-0", 
              "@type": "kgtk_edge", 
              "o": "\"4\"", 
              "p": "P1545", 
              "s": "Q96625619-P50-Q100104271-574cdc3e-0"
            }
          ], 
          "s": "Q96625619"
        }
      ], 
      "image": [], 
      "label": []
    }, 
    {
      "@id": "kgtk_object_labels_Q100104271", 
      "@type": "kgtk_object_labels", 
      "labels": {
        "P101": [
          "'campo de trabajo'@es"
        ], 
        "P106": [
          "'ocupaci\u00f3n'@es"
        ], 
        "P108": [
          "'empleador'@es"
        ], 
        "P1416": [
          "'afiliaci\u00f3n'@es"
        ], 
        "P1545": [
          "'orden dentro de la serie'@es"
        ], 
        "P1932": [
          "'referido como'@es"
        ], 
        "P1960": [
          "'identificador Google Acad\u00e9mico'@es"
        ], 
        "P21": [
          "'sexo o g\u00e9nero'@es"
        ], 
        "P31": [
          "'instancia de'@es"
        ], 
        "P50": [
          "'autor'@es"
        ], 
        "P512": [
          "'grado acad\u00e9mico'@es"
        ], 
        "P580": [
          "'fecha de inicio'@es"
        ], 
        "P582": [
          "'fecha de fin'@es"
        ], 
        "P69": [
          "'educado en'@es"
        ], 
        "P735": [
          "'nombre de pila'@es"
        ], 
        "P812": [
          "'especializaci\u00f3n acad\u00e9mica'@es"
        ], 
        "P856": [
          "'p\u00e1gina web oficial'@es"
        ], 
        "Q11660": [
          "'inteligencia artificial'@es"
        ], 
        "Q1569421": [
          "'Universidad de los Andes'@es"
        ], 
        "Q15897419": [
          "'Pedro'@es"
        ], 
        "Q1650915": [
          "'investigador'@es"
        ], 
        "Q190080": [
          "'Universidad Carnegie Mellon'@es"
        ], 
        "Q21198": [
          "'ciencias de la computaci\u00f3n'@es"
        ], 
        "Q4614": [
          "'Universidad del Sur de California'@es"
        ], 
        "Q5": [
          "'ser humano'@es"
        ], 
        "Q6581097": [
          "'masculino'@es"
        ], 
        "Q752297": [
          "'Doctor en Filosof\u00eda'@es"
        ]
      }
    }, 
    {
      "@id": "kgtk_object_images_Q100104271", 
      "@type": "kgtk_object_images", 
      "images": {
        "Q1569421": [
          "\"Universidad de los Andes (3326108271).jpg\""
        ], 
        "Q190080": [
          "\"CMU campus Cathedral Learning background.jpg\""
        ], 
        "Q4614": [
          "\"052607-016-BovardHall-USC.jpg\""
        ], 
        "Q5": [
          "\"Anterior view of human female and male, with labels.svg\""
        ]
      }
    }, 
    {
      "@id": "kgtk_object_fanouts_Q100104271", 
      "@type": "kgtk_object_fanouts", 
      "fanouts": {
        "Q11660": 63, 
        "Q1569421": 32, 
        "Q15897419": 16, 
        "Q1650915": 22, 
        "Q190080": 70, 
        "Q21198": 53, 
        "Q4614": 71, 
        "Q5": 70, 
        "Q6030821": 14, 
        "Q6581097": 17, 
        "Q752297": 13, 
        "Q96625619": 11
      }
    }
  ]
}
```

## Startup Messages with Auto Indexing

Here's a sample of the messages that were output during an initial server startup
with auto indexing.

```
 * Serving Flask app 'kgtk_browser_app.py' (lazy loading)
 * Environment: development
 * Debug mode: on
[2021-08-20 12:50:22 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_2_c1."node1" "_aLias.node1", graph_2_c1."node2" "_aLias.node_label"
     FROM graph_2 AS graph_2_c1
     WHERE graph_2_c1."label" = ?
        AND ((graph_2_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['label', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 12:50:22 sqlstore]: CREATE INDEX on table graph_2 column label ...
[2021-08-20 12:50:42 sqlstore]: ANALYZE INDEX on table graph_2 column label ...
[2021-08-20 12:50:45 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_3_c1."node1" "_aLias.node1", graph_3_c1."node2" "_aLias.node_alias"
     FROM graph_3 AS graph_3_c1
     WHERE graph_3_c1."label" = ?
        AND ((graph_3_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_3_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['alias', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 12:50:45 sqlstore]: CREATE INDEX on table graph_3 column label ...
[2021-08-20 12:50:49 sqlstore]: ANALYZE INDEX on table graph_3 column label ...
[2021-08-20 12:50:50 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_4_c1."node1" "_aLias.node1", graph_4_c1."node2" "_aLias.node_description"
     FROM graph_4 AS graph_4_c1
     WHERE graph_4_c1."label" = ?
        AND ((graph_4_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_4_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['description', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 12:50:50 sqlstore]: CREATE INDEX on table graph_4 column label ...
[2021-08-20 12:51:21 sqlstore]: ANALYZE INDEX on table graph_4 column label ...
[2021-08-20 12:51:26 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_1_c1."node1" "_aLias.node1", graph_1_c1."node2" "_aLias.node_image"
     FROM graph_1 AS graph_1_c1
     WHERE graph_1_c1."label" = ?
        AND (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['P18', ('NODE',), 10000]
---------------------------------------------
[2021-08-20 12:51:26 sqlstore]: CREATE INDEX on table graph_1 column label ...
[2021-08-20 12:58:33 sqlstore]: ANALYZE INDEX on table graph_1 column label ...
[2021-08-20 12:58:53 query]: SQL Translation:
---------------------------------------------
  SELECT graph_1_c1."id" "_aLias.id", graph_1_c1."node1" "_aLias.node1", graph_1_c1."label" "_aLias.label", graph_1_c1."node2" "_aLias.node2", graph_2_c2."node2" "_aLias.node_label", graph_1_c3."node2" "_aLias.node_image", graph_6_c4."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     LEFT JOIN graph_2 AS graph_2_c2
     ON graph_1_c1."node2" = graph_2_c2."node1"
        AND graph_2_c2."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c2."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c3
     ON graph_1_c1."node2" = graph_1_c3."node1"
        AND graph_1_c3."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c4
     ON graph_1_c1."node2" = graph_6_c4."node1"
        AND graph_6_c4."label" = ?
        AND ?
     WHERE (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), ('NODE',), 10000]
---------------------------------------------
[2021-08-20 12:58:53 sqlstore]: CREATE INDEX on table graph_6 column label ...
[2021-08-20 12:59:17 sqlstore]: ANALYZE INDEX on table graph_6 column label ...
[2021-08-20 12:59:19 sqlstore]: CREATE INDEX on table graph_1 column node2 ...
[2021-08-20 13:05:21 sqlstore]: ANALYZE INDEX on table graph_1 column node2 ...
[2021-08-20 13:05:42 query]: SQL Translation:
---------------------------------------------
  SELECT graph_1_c1."id" "_aLias.id", graph_1_c1."node1" "_aLias.node1", graph_1_c1."label" "_aLias.label", graph_1_c1."node2" "_aLias.node2", graph_2_c2."node2" "_aLias.node_label", graph_1_c3."node2" "_aLias.node_image", graph_6_c4."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     LEFT JOIN graph_2 AS graph_2_c2
     ON graph_1_c1."node1" = graph_2_c2."node1"
        AND graph_2_c2."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c2."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c3
     ON graph_1_c1."node1" = graph_1_c3."node1"
        AND graph_1_c3."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c4
     ON graph_1_c1."node1" = graph_6_c4."node1"
        AND graph_6_c4."label" = ?
        AND ?
     WHERE (graph_1_c1."node2" = ?)
     LIMIT ?
  PARAS: ['label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:05:42 query]: SQL Translation:
---------------------------------------------
  SELECT graph_5_c2."id", graph_1_c1."id" "_aLias.node1", graph_5_c2."label" "_aLias.label", graph_5_c2."node2" "_aLias.node2", graph_2_c3."node2" "_aLias.node_label", graph_1_c4."node2" "_aLias.node_image", graph_6_c5."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     INNER JOIN graph_5 AS graph_5_c2
     ON graph_1_c1."id" = graph_5_c2."node1"
        AND (graph_1_c1."node1" = ?)
     LEFT JOIN graph_2 AS graph_2_c3
     ON graph_5_c2."node2" = graph_2_c3."node1"
        AND graph_2_c3."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c3."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c4
     ON graph_5_c2."node2" = graph_1_c4."node1"
        AND graph_1_c4."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c5
     ON graph_5_c2."node2" = graph_6_c5."node1"
        AND graph_6_c5."label" = ?
        AND ?
     ORDER BY graph_1_c1."id" ASC, graph_5_c2."node2" DESC
     LIMIT ?
  PARAS: [('NODE',), 'label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), 10000]
---------------------------------------------
[2021-08-20 13:05:42 sqlstore]: CREATE INDEX on table graph_5 column node2 ...
[2021-08-20 13:07:00 sqlstore]: ANALYZE INDEX on table graph_5 column node2 ...
[2021-08-20 13:07:03 sqlstore]: CREATE INDEX on table graph_1 column id ...
[2021-08-20 13:13:01 sqlstore]: ANALYZE INDEX on table graph_1 column id ...
[2021-08-20 13:13:24 query]: SQL Translation:
---------------------------------------------
  SELECT graph_5_c2."id", graph_1_c1."id" "_aLias.node1", graph_5_c2."label" "_aLias.label", graph_5_c2."node2" "_aLias.node2", graph_2_c3."node2" "_aLias.node_label", graph_1_c4."node2" "_aLias.node_image", graph_6_c5."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     INNER JOIN graph_5 AS graph_5_c2
     ON graph_1_c1."id" = graph_5_c2."node1"
        AND (graph_1_c1."node2" = ?)
     LEFT JOIN graph_2 AS graph_2_c3
     ON graph_5_c2."node2" = graph_2_c3."node1"
        AND graph_2_c3."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c3."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c4
     ON graph_5_c2."node2" = graph_1_c4."node1"
        AND graph_1_c4."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c5
     ON graph_5_c2."node2" = graph_6_c5."node1"
        AND graph_6_c5."label" = ?
        AND ?
     ORDER BY graph_1_c1."id" ASC, graph_5_c2."node2" DESC
     LIMIT ?
  PARAS: [('NODE',), 'label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), 10000]
---------------------------------------------
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 289-494-431
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_2_c1."node1" "_aLias.node1", graph_2_c1."node2" "_aLias.node_label"
     FROM graph_2 AS graph_2_c1
     WHERE graph_2_c1."label" = ?
        AND ((graph_2_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['label', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_3_c1."node1" "_aLias.node1", graph_3_c1."node2" "_aLias.node_alias"
     FROM graph_3 AS graph_3_c1
     WHERE graph_3_c1."label" = ?
        AND ((graph_3_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_3_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['alias', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_4_c1."node1" "_aLias.node1", graph_4_c1."node2" "_aLias.node_description"
     FROM graph_4 AS graph_4_c1
     WHERE graph_4_c1."label" = ?
        AND ((graph_4_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_4_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['description', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_1_c1."node1" "_aLias.node1", graph_1_c1."node2" "_aLias.node_image"
     FROM graph_1 AS graph_1_c1
     WHERE graph_1_c1."label" = ?
        AND (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['P18', ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT graph_1_c1."id" "_aLias.id", graph_1_c1."node1" "_aLias.node1", graph_1_c1."label" "_aLias.label", graph_1_c1."node2" "_aLias.node2", graph_2_c2."node2" "_aLias.node_label", graph_1_c3."node2" "_aLias.node_image", graph_6_c4."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     LEFT JOIN graph_2 AS graph_2_c2
     ON graph_1_c1."node2" = graph_2_c2."node1"
        AND graph_2_c2."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c2."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c3
     ON graph_1_c1."node2" = graph_1_c3."node1"
        AND graph_1_c3."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c4
     ON graph_1_c1."node2" = graph_6_c4."node1"
        AND graph_6_c4."label" = ?
        AND ?
     WHERE (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT graph_1_c1."id" "_aLias.id", graph_1_c1."node1" "_aLias.node1", graph_1_c1."label" "_aLias.label", graph_1_c1."node2" "_aLias.node2", graph_2_c2."node2" "_aLias.node_label", graph_1_c3."node2" "_aLias.node_image", graph_6_c4."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     LEFT JOIN graph_2 AS graph_2_c2
     ON graph_1_c1."node1" = graph_2_c2."node1"
        AND graph_2_c2."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c2."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c3
     ON graph_1_c1."node1" = graph_1_c3."node1"
        AND graph_1_c3."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c4
     ON graph_1_c1."node1" = graph_6_c4."node1"
        AND graph_6_c4."label" = ?
        AND ?
     WHERE (graph_1_c1."node2" = ?)
     LIMIT ?
  PARAS: ['label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT graph_5_c2."id", graph_1_c1."id" "_aLias.node1", graph_5_c2."label" "_aLias.label", graph_5_c2."node2" "_aLias.node2", graph_2_c3."node2" "_aLias.node_label", graph_1_c4."node2" "_aLias.node_image", graph_6_c5."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     INNER JOIN graph_5 AS graph_5_c2
     ON graph_1_c1."id" = graph_5_c2."node1"
        AND (graph_1_c1."node1" = ?)
     LEFT JOIN graph_2 AS graph_2_c3
     ON graph_5_c2."node2" = graph_2_c3."node1"
        AND graph_2_c3."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c3."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c4
     ON graph_5_c2."node2" = graph_1_c4."node1"
        AND graph_1_c4."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c5
     ON graph_5_c2."node2" = graph_6_c5."node1"
        AND graph_6_c5."label" = ?
        AND ?
     ORDER BY graph_1_c1."id" ASC, graph_5_c2."node2" DESC
     LIMIT ?
  PARAS: [('NODE',), 'label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), 10000]
---------------------------------------------
[2021-08-20 13:13:26 query]: SQL Translation:
---------------------------------------------
  SELECT graph_5_c2."id", graph_1_c1."id" "_aLias.node1", graph_5_c2."label" "_aLias.label", graph_5_c2."node2" "_aLias.node2", graph_2_c3."node2" "_aLias.node_label", graph_1_c4."node2" "_aLias.node_image", graph_6_c5."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     INNER JOIN graph_5 AS graph_5_c2
     ON graph_1_c1."id" = graph_5_c2."node1"
        AND (graph_1_c1."node2" = ?)
     LEFT JOIN graph_2 AS graph_2_c3
     ON graph_5_c2."node2" = graph_2_c3."node1"
        AND graph_2_c3."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c3."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c4
     ON graph_5_c2."node2" = graph_1_c4."node1"
        AND graph_1_c4."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c5
     ON graph_5_c2."node2" = graph_6_c5."node1"
        AND graph_6_c5."label" = ?
        AND ?
     ORDER BY graph_1_c1."id" ASC, graph_5_c2."node2" DESC
     LIMIT ?
  PARAS: [('NODE',), 'label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), 10000]
---------------------------------------------
127.0.0.1 - - [20/Aug/2021 13:18:48] "GET / HTTP/1.1" 404 -
127.0.0.1 - - [20/Aug/2021 13:18:48] "GET /favicon.ico HTTP/1.1" 404 -
```

### Sample Query Messages with Auto Indexing

Here is a sample of the server's messages executing a sample query.  The server was started with auto indexing enabled.

```
[2021-08-20 13:29:41 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_2_c1."node1" "_aLias.node1", graph_2_c1."node2" "_aLias.node_label"
     FROM graph_2 AS graph_2_c1
     WHERE graph_2_c1."label" = ?
        AND ((graph_2_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['label', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:29:41 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_3_c1."node1" "_aLias.node1", graph_3_c1."node2" "_aLias.node_alias"
     FROM graph_3 AS graph_3_c1
     WHERE graph_3_c1."label" = ?
        AND ((graph_3_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_3_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['alias', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:29:41 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_4_c1."node1" "_aLias.node1", graph_4_c1."node2" "_aLias.node_description"
     FROM graph_4 AS graph_4_c1
     WHERE graph_4_c1."label" = ?
        AND ((graph_4_c1."node1" = ?) AND ((? = ?) OR (kgtk_lqstring_lang(graph_4_c1."node2") = ?)))
     LIMIT ?
  PARAS: ['description', ('NODE',), ('LANG',), 'any', ('LANG',), 10000]
---------------------------------------------
[2021-08-20 13:29:41 query]: SQL Translation:
---------------------------------------------
  SELECT DISTINCT graph_1_c1."node1" "_aLias.node1", graph_1_c1."node2" "_aLias.node_image"
     FROM graph_1 AS graph_1_c1
     WHERE graph_1_c1."label" = ?
        AND (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['P18', ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:29:41 query]: SQL Translation:
---------------------------------------------
  SELECT graph_1_c1."id" "_aLias.id", graph_1_c1."node1" "_aLias.node1", graph_1_c1."label" "_aLias.label", graph_1_c1."node2" "_aLias.node2", graph_2_c2."node2" "_aLias.node_label", graph_1_c3."node2" "_aLias.node_image", graph_6_c4."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     LEFT JOIN graph_2 AS graph_2_c2
     ON graph_1_c1."node2" = graph_2_c2."node1"
        AND graph_2_c2."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c2."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c3
     ON graph_1_c1."node2" = graph_1_c3."node1"
        AND graph_1_c3."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c4
     ON graph_1_c1."node2" = graph_6_c4."node1"
        AND graph_6_c4."label" = ?
        AND ?
     WHERE (graph_1_c1."node1" = ?)
     LIMIT ?
  PARAS: ['label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), ('NODE',), 10000]
---------------------------------------------
[2021-08-20 13:29:42 query]: SQL Translation:
---------------------------------------------
  SELECT graph_5_c2."id", graph_1_c1."id" "_aLias.node1", graph_5_c2."label" "_aLias.label", graph_5_c2."node2" "_aLias.node2", graph_2_c3."node2" "_aLias.node_label", graph_1_c4."node2" "_aLias.node_image", graph_6_c5."node2" "_aLias.node_fanout"
     FROM graph_1 AS graph_1_c1
     INNER JOIN graph_5 AS graph_5_c2
     ON graph_1_c1."id" = graph_5_c2."node1"
        AND (graph_1_c1."node1" = ?)
     LEFT JOIN graph_2 AS graph_2_c3
     ON graph_5_c2."node2" = graph_2_c3."node1"
        AND graph_2_c3."label" = ?
        AND ((? = ?) OR (kgtk_lqstring_lang(graph_2_c3."node2") = ?))
     LEFT JOIN graph_1 AS graph_1_c4
     ON graph_5_c2."node2" = graph_1_c4."node1"
        AND graph_1_c4."label" = ?
        AND ?
     LEFT JOIN graph_6 AS graph_6_c5
     ON graph_5_c2."node2" = graph_6_c5."node1"
        AND graph_6_c5."label" = ?
        AND ?
     ORDER BY graph_1_c1."id" ASC, graph_5_c2."node2" DESC
     LIMIT ?
  PARAS: [('NODE',), 'label', ('LANG',), 'any', ('LANG',), 'P18', ('FETCH_IMAGES',), 'count_distinct_properties', ('FETCH_FANOUTS',), 10000]
---------------------------------------------
127.0.0.1 - - [20/Aug/2021 13:29:43] "GET /kgtk/browser/backend/get_all_node_data?node=Q100104271&lang=en&images=true&fanouts=true&inverse=false HTTP/1.1" 200 -
```

Repeating the same query resulted in one additional message:
```
127.0.0.1 - - [20/Aug/2021 13:31:33] "GET /kgtk/browser/backend/get_all_node_data?node=Q100104271&lang=en&images=true&fanouts=true&inverse=false HTTP/1.1" 200 -
```
