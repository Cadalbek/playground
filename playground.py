# coding: utf8
# author : gerard

from geoserver.catalog import Catalog
import subprocess
import webbrowser
import json
import requests
import logging
import psycopg2

logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')
# hdl = GsHandler('config.json')
# hdl.InitGs()
# hdl.InitGs('fr')
# hdl2 = GsHandler('config2.json')
# hdl3 = GsHandler('config3.json')

class GsHandler(object):
    def __init__(self, config_file):
        # Initialisation des variables
        self.config = open(config_file)
        self.param = json.load(self.config)
        self.store = self.param['cnx_globales']['urlgeoserver']
        self.websig = self.param['cnx_globales']['urlwebsig']
        self.cat = Catalog(self.param['cnx_globales']['urlrest'], username=self.param['cnx_globales']['auth_admin'],
                           password=self.param['cnx_globales']['auth_password'])
        self.auth = (self.param['cnx_globales']['auth_admin'], self.param['cnx_globales']['auth_password'])
        self.con_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            self.param['cnx_psql']['user'],
            self.param['cnx_psql']['passwd'],
            self.param['cnx_psql']['host'],
            self.param['cnx_psql']['port'],
            self.param['cnx_psql']['database']
        )
        self.conn = psycopg2.connect(self.con_string)
        self.cur = self.conn.cursor()
        self.qu1 = """SELECT table_name FROM information_schema.tables WHERE table_schema = '""" + \
                   self.param['cnx_psql']['schema'] + """' """

    def InitGs(self):
        # Input de lancement du server en local
        print '---- Launching Process ----'
        if (raw_input("Gus Gs Server - Input [Y/N] for start: ")) == 'Y':
            subprocess.Popen(self.param['cnx_globales']['pathbat'],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            pass

        # Input de lancement du GeoServer UI
        if (raw_input("Input [Y/N] to launch the GeoServer UI: ")) == 'Y':
            webbrowser.open(self.store)
        else:
            pass

        # Input de lancement du site web
        if (raw_input("Input [Y/N] to launch the website: ")) == 'Y':
            webbrowser.open(self.websig)
        else:
            pass

        # Appel de la nouvelle fonction CraftGs
        self.CraftGs()

    def CraftGs(self):
        # Input de création d'un nouveau WorkSpace [WS]
        if (raw_input("Input [Y/N] to open a workspace: ")) == 'Y':
            self.workspace_name = (raw_input("Input your workspace's name: "))
            self.uri = (raw_input("Input your uri's name: "))
            Catalog.create_workspace(self.cat, self.workspace_name, self.uri)
            print '---- WorkSpace created ----'
        else:
            pass

        # Input de création d'un DataStore [PSQL]
        self.choice = (raw_input("Input [PSQL/SHP] to open a PostgreSQL or a Shapefile datastore: "))
        if self.choice == 'PSQL':
            print 'Pay attention ! The workspace must be existing !'
            self.workspace_name_psql = (raw_input("Input your workspace's name: "))
            self.datastore_name_psql = (raw_input("Input your datastore's name: "))
            ds = Catalog.create_datastore(self.cat, self.datastore_name_psql, self.workspace_name_psql)
            ds.connection_parameters.update(host=self.param['cnx_psql']['host'],
                                            port=self.param['cnx_psql']['port'],
                                            database=self.param['cnx_psql']['database'],
                                            user=self.param['cnx_psql']['user'],
                                            passwd=self.param['cnx_psql']['passwd'],
                                            dbtype=self.param['cnx_psql']['dbtype'],
                                            schema=self.param['cnx_psql']['schema'])
            self.cat.save(ds)
            print '---- PGSQL DataStore created ----'

        # Input de création d'un DataStore [SHP]
        elif self.choice == 'SHP':
            print 'Pay attention ! The workspace must be existing !'
            self.data_shp = self.param['cnx_globales']['datashp']
            self.workspace_name_shp = (raw_input("Input your workspace's name: "))
            self.datastore_name_shp = (raw_input("Input your datastore's name: "))
            self.url_shp = self.param['cnx_globales'][
                               'urlrest'] + self.workspace_name_shp + "/datastores/" + self.datastore_name_shp + "/external.shp?configure=all"
            self.headers_shp = {'Content-type': 'text/plain'}
            self.response1 = requests.put(self.url_shp, data=self.data_shp, auth=self.auth, headers=self.headers_shp)

        else:
            pass

        # Appel de la nouvelle fonction DataGs
        self.DataGs()

    def DataGs(self):
        # Input de publication de données UNIQUE
        self.choice2 = (raw_input("Input [MASS/UNIQUE] to do a massive or unique data import: "))
        if self.choice2 == 'UNIQUE':
            print 'Pay attention ! The workspace and the datastore must be existing !'
            self.workspace_name_data = (raw_input("Input your workspace's name: "))
            self.datastore_name_data = (raw_input("Input your datastore's name: "))
            self.file_name_data = (raw_input("Input your file name: "))
            self.url_data = self.param['cnx_globales'][
                                'urlrest'] + self.workspace_name_data + "/datastores/" + self.datastore_name_data + "/featuretypes"
            self.data_data = "<featureType><name>" + self.file_name_data + "</name></featureType>"
            self.headers_data = "{'Content-type': 'text/xml'}"
            self.response = requests.post(self.url_data, data=self.data_data, auth=self.auth, headers=self.headers_data)

        # Input de publication de données MASS
        elif self.choice2 == 'MASS':
            self.cur.execute(self.qu1)
            self.rows = self.cur.fetchall()
            self.workspace_name_data_mass = (raw_input("Input your workspace's name: "))
            self.datastore_name_data_mass = (raw_input("Input your datastore's name: "))

            for self.i in self.rows:
                self.table_name = str(self.i)[2:-3]
                print self.table_name
                logging.info('Uploading ... ' + self.table_name + ' ...')
                self.file_name_data_mass = self.table_name
                self.url_data_mass = "http://localhost:8080/geoserver/rest/workspaces/" + self.workspace_name_data_mass + "/datastores/" + self.datastore_name_data_mass + "/featuretypes"
                self.data_data_mass = "<featureType><name>" + self.file_name_data_mass + "</name></featureType>"
                self.headers_data_mass = {'Content-type': 'text/xml'}
                self.response_mass = requests.post(self.url_data_mass, data=self.data_data_mass, auth=self.auth,
                                                   headers=self.headers_data_mass)

        self.AppendWebsig()

    def AppendWebsig(self):
        self.choice3 = (raw_input("Input [Y/N] for appened the result on a new html leaflet file: "))
        if self.choice3 == 'Y':
            self.cur.execute(self.qu1)
            self.rows = self.cur.fetchall()
            self.html_file = """: L.tileLayer.wms('http://localhost:8080/geoserver/schematest/wms?', {
			layers: '"""

            self.schemafile = self.param['cnx_psql']['schema']

            self.html_file_2 = """',
			format: 'image/png',
  			transparent: true
		}),"""

            self.list_final = []

            for self.z in self.rows:
                self.table_name_2 = str(self.z)[2:-3]
                self.final = self.table_name_2 + self.html_file + self.schemafile + """:""" + self.table_name_2 + self.html_file_2
                self.list_final.append(self.final)
        else:
            pass

        with open("result.html", "w") as result:
            ii = str()
            for i in self.list_final:
                ii += i + '\n' + '\n'
            result.write(str(ii))
            print ii


        print '---- Ending Process ----'


"""MAIN"""

if __name__ == '__main__':
    handler = GsHandler('config.json')
    handler.InitGs()

##### BACKLOG #####
## Un appel de console unique ?
## Un fichier de config global pour tout
