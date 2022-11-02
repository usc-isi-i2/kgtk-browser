# Bring Your Own Data

This document describes the steps required for importing any file in [KGTK Edge File format](https://kgtk.readthedocs.io/en/latest/data_model/#file-format) to the Sqlite db file for KGTK Browser backend.

The input tsv file should **fulfill all the following requirements** ,
- it should have an `id` column containing ids for all the rows. See [kgtk add-id](https://kgtk.readthedocs.io/en/latest/transform/add_id/) to add the `id` column if there is none.
- it should contain data type for all the properties in the column `label`. 
  -  for new properties, please create a file similar to https://github.com/usc-isi-i2/kgtk/blob/master/kgtk-properties/kgtk.properties.tsv
  -  for existing wikidata properties, make sure the input file has data types.
  -  this is important, as data type is used to format the data in the browser.
- 

Next, setup and run this [notebook](https://github.com/usc-isi-i2/kgtk-notebooks/blob/main/use-cases/create_wikidata/partition-wikidata.ipynb). The notebook has the following parameters:
```
wikidata_input_path = <path to the input KGTK Edge file>
wikidata_parts_path = <output folder path>
temp_folder_path =    wikidata_parts_path + '/temp' # leave as is
gzip_command =        'pigz' # if you have pigz, leave as it, other wise update this to 'gzip'
kgtk_command =        'time kgtk' # leave as is
kgtk_options =        '--debug --timing' # leave as is
kgtk_extension =      'tsv.gz' # leave as is
presorted =           'False' # whether the input file is sorted or not
sort_extras =         '--parallel 24 --buffer-size 30% --temporary-directory ' + temp_folder_path # reduce the number after '--parallel' to the numbe of CPUs you want to use
use_mgzip =           'True' # multithreaded gzip in python
verbose =             'True' # leave as is to see all the logs
```
Successful run of the notebook will produce partitioned files at the `wikidata_parts_path` folder. These files are required for the KGTK Browser.
