### PLAYGROUND
Playground allows you to have a multiple tool for a geoserver handling.
Features :
- Open a .bat command prompt for launching the geoserver prompt
- Open the geoserver UI 
- Open a HTML local page (leaflet)
- Create a Workspace (Need to set the name and the URI)
- Create a local or a PSQL connexion datastore (Need to set the Workspace name and the Datastore name)
- Import Mass or Unique data (Need to set the workspace and the datastore name)
- Create a HTML sample to connect the data to the GS

```
; Default credentials

{
  "cnx_psql": {
    "host": "XXX",
    "port": "XXX",
    "database": "XXX",
    "user": "XXX",
    "passwd": "XXX",
    "dbtype": "XXX",
    "schema": "XXX"
  },
  "cnx_globales": {
    "auth_admin": "XXX",
    "auth_password": "XXX",
    "urlgeoserver": "http://localhost:8080/geoserver/web/",
    "urlrest": "http://localhost:8080/geoserver/rest",
    "urlwebsig": "/playground/leaflet/visu.html",
    "pathbat": "/playground/start_geoserver.bat",
    "datashp": "XXX",
    "headers": "{'Content-type': 'text/xml'}"
  }
}

; Shapefile folder



#### Requierements 

Python 2.7

- geoserver.catalog 
- subprocess
- webbrowser
- json
- requests
- logging
- psycopg2
