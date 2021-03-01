# kgtk-browser

## Requirements

* you need to install the kgtk and flask Python packages
* download wikidataos-v4-browser.sqlite3.db.gz from the KGTK shared drive
  in the KGTK > datasets > wikidataos-v4 folder
* uncompress the DB somewhere on your system which will require about 50GB
  of space; for best performance this should be on an SSD drive
* edit DB_GRAPH_CACHE in kgtk_browser_config.py to point to that location


## Running the web app

The following steps will start a server on your local host at the default port (5000):

```
> cd .../kgtk-browser
> export FLASK_APP=kgtk_browser_app.py
> export FLASK_ENV=development
> export KGTK_BROWSER_CONFIG=$PWD/kgtk_browser_config.py
> flask run
```


## Design and status

The top-level entry points are defined at the end of
`kgtk_browser_app.py`.  The main one to use is `get_all_node_data`
(example below) which takes a node as an argument and retrieves all
relevant edges, qualifier edges, node labels and descriptions as well
as a labels dictionary for all referenced properties and objects.

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

Currently all labels, descriptions, etc. are transmitted as
multi-valued fields that have values in multiple languages.  The first
one of those lists should generally be a good candidate to use, but
we'll have to think about how to best sort them in general, and how to
best support multiple languages.

In general, sorting values for best presentation still needs to be
implemented.

There probably needs to be some definition somewhere which properties
define labels, descriptions, instance-of, etc.  For now we can assume
the ones used by Wikidata, but we probably want to use this for
non-Wikidata KGs as well.

Construction and transmission of property data types, site links and other
information still needs to be implemented.


## Example

The example below shows how to query the server.  In development mode Flask
pretty-prints the JSON which makes things more verbose.  Also the default
Unicode encoding is possibly not what we want, but it should be OK as a start.

```
http://127.0.0.1:5000/kgtk/browser/backend/get_all_node_data?node=Q100104271

{
  "@context": [
    "https://github.com/usc-isi-i2/kgtk-browser/kgtk_objects.jsonld"
  ], 
  "@type": "kgtk_object_collection", 
  "meta": {
    "@type": "kgtk_meta_info", 
    "database": "wikidataos-v4", 
    "version": "2021-02-24"
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
              "@type": "kgtk_edge", 
              "o": "^1988-00-00T00:00:00Z/9", 
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
              "@type": "kgtk_edge", 
              "o": "^1987-00-00T00:00:00Z/9", 
              "p": "P582", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@type": "kgtk_edge", 
              "o": "^1980-00-00T00:00:00Z/9", 
              "p": "P580", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
              "@type": "kgtk_edge", 
              "o": "Q752297", 
              "p": "P512", 
              "s": "Q100104271-P69-Q190080-f617727b-0"
            }, 
            {
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
      "label": [
        "'Pedro Szekely'@en"
      ]
    }, 
    {
      "@id": "kgtk_object_labels_Q100104271", 
      "@type": "kgtk_object_labels", 
      "labels": {
        "P101": [
          "'field of work'@en", 
          "'campo de trabajo'@es", 
          "'\u043e\u0431\u043b\u0430\u0441\u0442\u044c \u0434\u0435\u044f\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438'@ru", 
          "'\u5de5\u4f5c\u9886\u57df'@zh-cn"
        ], 
        "P106": [
          "'occupation'@en", 
          "'ocupaci\u00f3n'@es", 
          "'\u0440\u043e\u0434 \u0437\u0430\u043d\u044f\u0442\u0438\u0439'@ru", 
          "'\u804c\u4e1a'@zh-cn"
        ], 
        "P108": [
          "'employer'@en", 
          "'empleador'@es", 
          "'\u0440\u0430\u0431\u043e\u0442\u043e\u0434\u0430\u0442\u0435\u043b\u044c'@ru", 
          "'\u96c7\u4e3b'@zh-cn"
        ], 
        "P1416": [
          "'affiliation'@en", 
          "'afiliaci\u00f3n'@es", 
          "'\u043f\u0440\u0438\u043d\u0430\u0434\u043b\u0435\u0436\u0438\u0442 \u043a'@ru"
        ], 
        "P1960": [
          "'Google Scholar author ID'@en", 
          "'identificador Google Acad\u00e9mico'@es", 
          "'\u043a\u043e\u0434 Google Scholar'@ru"
        ], 
        "P21": [
          "'sex or gender'@en", 
          "'sexo o g\u00e9nero'@es", 
          "'\u043f\u043e\u043b \u0438\u043b\u0438 \u0433\u0435\u043d\u0434\u0435\u0440'@ru", 
          "'\u6027\u522b'@zh-cn"
        ], 
        "P31": [
          "'instance of'@en", 
          "'instancia de'@es", 
          "'\u044d\u0442\u043e \u0447\u0430\u0441\u0442\u043d\u044b\u0439 \u0441\u043b\u0443\u0447\u0430\u0439 \u043f\u043e\u043d\u044f\u0442\u0438\u044f'@ru", 
          "'\u6027\u8d28'@zh-cn"
        ], 
        "P512": [
          "'academic degree'@en", 
          "'grado acad\u00e9mico'@es", 
          "'\u0443\u0447\u0451\u043d\u0430\u044f \u0441\u0442\u0435\u043f\u0435\u043d\u044c'@ru", 
          "'\u5b66\u4f4d'@zh-cn"
        ], 
        "P580": [
          "'start time'@en", 
          "'fecha de inicio'@es", 
          "'\u0434\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430'@ru", 
          "'\u59cb\u4e8e'@zh-cn"
        ], 
        "P582": [
          "'end time'@en", 
          "'fecha de fin'@es", 
          "'\u0434\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f'@ru", 
          "'\u7ec8\u4e8e'@zh-cn"
        ], 
        "P69": [
          "'educated at'@en", 
          "'educado en'@es", 
          "'\u0443\u0447\u0435\u0431\u043d\u043e\u0435 \u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435'@ru", 
          "'\u5c31\u8bfb\u5b66\u6821'@zh-cn"
        ], 
        "P735": [
          "'given name'@en", 
          "'nombre de pila'@es", 
          "'\u043b\u0438\u0447\u043d\u043e\u0435 \u0438\u043c\u044f'@ru", 
          "'\u540d\u5b57'@zh-cn"
        ], 
        "P812": [
          "'academic major'@en", 
          "'especializaci\u00f3n acad\u00e9mica'@es", 
          "'\u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0443\u0447\u0435\u0431\u043d\u044b\u0439 \u043f\u0440\u0435\u0434\u043c\u0435\u0442'@ru"
        ], 
        "P856": [
          "'official website'@en", 
          "'p\u00e1gina web oficial'@es", 
          "'\u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0430\u0439\u0442'@ru", 
          "'\u5b98\u65b9\u7f51\u7ad9'@zh-cn"
        ], 
        "Q11660": [
          "'artificial intelligence'@en", 
          "'inteligencia artificial'@es", 
          "'\u0438\u0441\u043a\u0443\u0441\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442'@ru", 
          "'\u4eba\u5de5\u667a\u80fd'@zh-cn"
        ], 
        "Q1569421": [
          "'University of the Andes'@en", 
          "'Universidad de los Andes'@es", 
          "'\u0423\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442 \u0410\u043d\u0434'@ru"
        ], 
        "Q15897419": [
          "'Pedro'@en", 
          "'Pedro'@es", 
          "'\u041f\u0435\u0434\u0440\u043e / \u041f\u0435\u0434\u0440\u0443'@ru"
        ], 
        "Q1650915": [
          "'researcher'@en", 
          "'investigador'@es", 
          "'\u0438\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c'@ru", 
          "'\u7814\u7a76\u8005'@zh-cn"
        ], 
        "Q190080": [
          "'Carnegie Mellon University'@en", 
          "'Universidad Carnegie Mellon'@es", 
          "'\u0423\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442 \u041a\u0430\u0440\u043d\u0435\u0433\u0438 \u2014 \u041c\u0435\u043b\u043b\u043e\u043d'@ru", 
          "'\u5361\u5185\u57fa\u6885\u9686\u5927\u5b66'@zh-cn"
        ], 
        "Q21198": [
          "'computer science'@en", 
          "'ciencias de la computaci\u00f3n'@es", 
          "'\u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u043a\u0430'@ru", 
          "'\u8ba1\u7b97\u673a\u79d1\u5b66'@zh-cn"
        ], 
        "Q4614": [
          "'University of Southern California'@en", 
          "'Universidad del Sur de California'@es", 
          "'\u0423\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442 \u042e\u0436\u043d\u043e\u0439 \u041a\u0430\u043b\u0438\u0444\u043e\u0440\u043d\u0438\u0438'@ru"
        ], 
        "Q5": [
          "'human'@en", 
          "'ser humano'@es", 
          "'\u0447\u0435\u043b\u043e\u0432\u0435\u043a'@ru", 
          "'\u4eba\u7c7b'@zh-cn"
        ], 
        "Q6030821": [
          "'Information Sciences Institute'@en"
        ], 
        "Q6581097": [
          "'male'@en", 
          "'masculino'@es", 
          "'\u043c\u0443\u0436\u0441\u043a\u043e\u0439 \u043f\u043e\u043b'@ru", 
          "'\u7537'@zh-cn"
        ], 
        "Q752297": [
          "'Doctor of Philosophy'@en", 
          "'Ph.D.'@es", 
          "'\u0434\u043e\u043a\u0442\u043e\u0440 \u0444\u0438\u043b\u043e\u0441\u043e\u0444\u0438\u0438'@ru", 
          "'\u54f2\u5b66\u535a\u58eb'@zh-cn"
        ]
      }
    }
  ]
}
```