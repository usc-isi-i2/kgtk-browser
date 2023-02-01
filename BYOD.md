# Bring Your Own Data

This document describes the steps required for importing any file in [KGTK Edge File format](https://kgtk.readthedocs.io/en/latest/data_model/#file-format) to the Sqlite db file for KGTK Browser backend.

Let's say you have a file called `mydata.tsv.gz` in KGTK edge file format. 

Next we need to create a file similar to https://github.com/usc-isi-i2/kgtk/blob/master/kgtk-properties/kgtk.properties.tsv for any new properties in the file `mydata.tsv.gz`. Let's say the new properties are `Property1` and `Property2`. The new properties file should look like this ,

|node1   |label      |node2                                                                             |
|--------|-----------|----------------------------------------------------------------------------------|
|Property1    |label      |'property 1'@en                                                                    |
|Property1    |alias      |'alias for property 1'@en                                                                     |
|Property1    |description|'description for property 1'@en                                       |
|Property1    |P31        |Q18616576                                                                    |
|Property1    |datatype   |wikibase-item                                                                |
|Property2|label      |'property 2'@en                                                    |
|Property2|alias      |'alias of property 2'@en                                                     |
|Property2|description|'description of property 2'@en|
|Property2|P31        |Q18616576                                                                         |
|Property2    |datatype   |wikibase-item                                                                 |

The properties `label`, `alias`, `description` and `P31` are optional but nice to have. The property `datatype` is mandatory as it drives the way browser 
dislpays information.

Here is a list of valid KGTK datatypes: 

|    KGTK Datatypes    |
|--------|
|commonsMedia|
|external-id|
|geo-shape|
|globe-coordinate|
|math    |
|monolingualtext|
|musical-notation|
|node2   |
|quantity|
|string  |
|tabular-data|
|time    |
|url     |
|wikibase-form|
|wikibase-item|
|wikibase-lexeme|
|wikibase-property|
|wikibase-sense|


Let's call the new properties file: `mynewproperties.tsv.gz`

Run the following commands ,

```
kgtk cat -i mydata.tsv.gz -i mynewproperties.tsv.gz -o mydata_1.tsv.gz
kgtk add-id -i mydata_1.tsv.gz -o mydata_2.tsv.gz --id-style wikidata
kgtk sort -i mydata_2.tsv.gz -o all.tsv.gz
```

**Assumption: If you are re using some of the wikidata properties, data type for those properties exist in the `mydata.tsv.gz` or  `mynewproperties.tsv.gz` file**


Next, setup and run this [notebook](https://github.com/usc-isi-i2/kgtk-notebooks/blob/main/use-cases/create_wikidata/partition-wikidata.ipynb). The notebook has the following parameters:
```
wikidata_input_path = <path to the input KGTK Edge file>
wikidata_parts_path = <output folder path>
temp_folder_path =    wikidata_parts_path + '/temp' # leave as is
gzip_command =        'pigz' # if you have pigz, leave as is, other wise update this to 'gzip'
kgtk_command =        'time kgtk' # leave as is
kgtk_options =        '--debug --timing' # leave as is
kgtk_extension =      'tsv.gz' # leave as is
presorted =           'False' # whether the input file is sorted or not
sort_extras =         '--parallel 24 --buffer-size 30% --temporary-directory ' + temp_folder_path # reduce the number after '--parallel' to the numbe of CPUs you want to use
use_mgzip =           'True' # multithreaded gzip in python
verbose =             'True' # leave as is to see all the logs
```
Successful run of the notebook will produce partitioned files at the `wikidata_parts_path` folder. These files are required for the KGTK Browser.
