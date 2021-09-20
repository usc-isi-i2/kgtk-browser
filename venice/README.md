1. Put the venice data into:
```
venice/venice_kgtk_file.tsv
```

2. You will need to have the latest developmental branch of
the `kgtk` project in your PYTHONPATH.

3. In the `kgtk-browser` top level folder, execute the following command to
prepare the sqlite3 database for the browser server:
```
venice/prepare-venice-data-for-browser.csh
```
(My apologies, I still use csh/tcsh)

3. In the `kgtk-browser` top level folder, execute the following command to
start the KGTK browser's server:
```
venice/start-venice-server.csh
```

4) As configured, the KTK browser server is accessible on port 5007 of the
local host (`https://127.0.0.1:5007`).  This requires that you connect to the
KGTK browser server using a Web browser (e.g., Firefox) running on the same
system.  If you want the browser to be more widely availabe, you may edit
`venice/start-venice-server.csh` and change the `--port` option, and/or
inserta a `--host` option.  If needed, ensure that your server system has an
opening in its firewall for the selected port.
