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

Install `graph-tools` and `jupyterlab`
```
conda install -c conda-forge graph-tool
pip install jupyterlab
```

## Build the Graph Cache required for KGTK Browser Backend

**If you are bringing your own data (in contrast to Wikidata), please refer to [BYOD](BYOD.md). Successful run of steps in the document will produce the files required to proceed from here on.**
Only exception being `metadata.pagerank.undirected.tsv.gz`. Please read on.

The following files are required ,

- labels.en.tsv.gz
- aliases.en.tsv.gz
- descriptions.en.tsv.gz
- claims.tsv.gz
- metadata.property.datatypes.tsv.gz
- qualifiers.tsv.gz
- metadata.pagerank.undirected.tsv.gz
- class-visualization.edge.tsv.gz  **optional**
- class-visualization.node.tsv.gz  **optional**

The file `metadata.pagerank.undirected.tsv.gz` can be created by running this command ,

```
 kgtk --debug graph-statistics \
 -i claims.tsv.gz \
 -o metadata.pagerank.undirected.tsv.gz  \
 --compute-pagerank True  \
 --compute-hits False  \
 --page-rank-property Pundirected_pagerank \
 --output-degrees False  \
 --output-pagerank True  \
 --output-hits False  \
 --output-statistics-only \
 --undirected True \
 --log-file metadata.pagerank.undirected.summary.txt
 ```
 
 **Move the file `metadata.pagerank.undirected.tsv.gz`  to the folder containing the other files required for the browser cache.**

### SQLITE or ElasticSearch

KGTK Browser can be setup with either a SQLITE DB Cache file or a [KGTK Search api](https://github.com/usc-isi-i2/kgtk-search). We'll describe both options.

### Building a SQLITE Cache DB file
- Execute [this](https://github.com/usc-isi-i2/kgtk-notebooks/blob/main/use-cases/create_wikidata/KGTK-Query-Text-Search-Setup.ipynb) notebook.
- Set parameters: `create_db = 'yes'` and `create_es = 'no'` to create only the SQLITE DB Cache file.
- Setup other parameters as described in the notebook.

### Setting up ElasticSearch Index and KGTK Search API
- Execute [this](https://github.com/usc-isi-i2/kgtk-notebooks/blob/main/use-cases/create_wikidata/KGTK-Query-Text-Search-Setup.ipynb) notebook.
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
```

**NOTE: `node` version 18 (and above) gives the following error after `npm start`. Please use node version `v16.6.2`**
```
Proxy error: Could not proxy request /kb/info from localhost:3000 to http://localhost:3233.
See https://nodejs.org/api/errors.html#errors_common_system_errors for more information (ECONNREFUSED).
```

### Terminal-1: Run kgtk_browser_app.py

Set the following ENV variables in the terminal.

- KGTK_BROWSER_GRAPH_ID: Sets the title of the KGTK Browser. For example: `DWD Knowledge Graph`
- KGTK_BROWSER_GRAPH_CACHE: absolute path to the sqlite db graph cache file
- KGTK_BROWSER_CLASS_VIZ_DIR: path to folder where graph visualizations will be stored. This is optional and requried only in the case where you have
class visualization files.

```
export KGTK_BROWSER_GRAPH_ID=My Dataset Browser
export KGTK_BROWSER_GRAPH_CACHE=<path to the SQLITE DB Cache created>
export KGTK_BROWSER_CLASS_VIZ_DIR=/tmp # or to some folder
```

The following commands will start the backend flask server,

```
cd kgtk-browser
conda activate kgtk-env
python kgtk_browser_app.py
```

### Terminal-2: Run front end

The following steps will start a server on your local host at the default port (3000):

Build the frontend files ,

```
cd app
export REACT_APP_FRONTEND_URL='/browser'
export REACT_APP_BACKEND_URL=''
```
To use the SQLite text instead of Elasticsearch API, set the following environment variable.

```
export REACT_APP_USE_KGTK_KYPHER_BACKEND='1'
```

Continue ,

```
npm run build
npm start
```

A new tab should open in the default browser at `http://localhost:3000`

## Start the server using `kgtk browse` command

Set the ENV variables described in the previous section and run the following commands from a terminal.

```
cd kgtk-browser
cd app
npm run build

export PYTHONPATH=$PYTHONPATH:$PWD
kgtk browse --host localhost --port 5000
```

A new tab should open in the default browser at `http://localhost:5000`

NOTE: using development mode turns on JSON pretty-printing which about
doubles the size of response objects.  For faster server response,
set `FLASK_ENV` to `production`.


## Build a docker image for [KGTK Browser](https://kgtk.isi.edu/browser/) deployment (internal use only)

Running the following commands will create and push a new docker image with  the tag `kgtk-browser:06022022`

Open a terminal and type in the following commands

```
cd kgtk-browser
export REACT_APP_FRONTEND_URL='/browser'
export REACT_APP_BACKEND_URL='/browser'
```

To use the SQLite text instead of Elasticsearch API, set the following environment variable.

```
export REACT_APP_USE_KGTK_KYPHER_BACKEND='1'
```

Set the following environment variable to `0` or `1` if you have have the file `derived.P31279star.tsv.gz` loaded into the cache.
```
export REACT_APP_P31279STAR_NA='0' # if the file is available, otherwise

export REACT_APP_P31279STAR_NA='1'
```

continue ,
```
cd app
npm run build

cd ..
docker build -t docker-reg.ads.isi.edu:443/kgtk-browser:06022022 . && docker push docker-reg.ads.isi.edu:443/kgtk-browser:06022022
```
