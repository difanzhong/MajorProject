import psycopg2
import sys

class DBConnect(object):

    def __init__(self):

        self._conn = None
        self._cur = None


    def connect(self):
        try:

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self._conn = psycopg2.connect(host='localhost', dbname='MP', user='postgres', password='adidas9038')

            # create a cursor
            self._cur = self._conn.cursor()

            # execute a statement
            print("Connected!\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            if self._conn is not None:
                self._conn.close()
                print('Database connection closed.')

    def close(self):

        if self._conn is not None:
            self._conn.close()

    def insert_tweet(self, created_at, text, tokenized, s_id):
        """ insert a new vendor into the vendors table """
        sql = """INSERT INTO tweepy (origintext, createtime, tokenized, suburb_id)
                 VALUES(%s, to_timestamp(%s, 'Mon dd hh24:mi:ss yyyy'), %s,%s) RETURNING id;"""

        try:

            # read database configuration
            if self._cur is not None:
            #     # execute the INSERT statement
                 self._cur.execute(sql, (text, created_at, tokenized, s_id))

            #     # get the generated id back
            #     #vendor_id = self._cur.fetchone()[0]
            #     # commit the changes to the database
                 self._conn.commit()
            #     # close communication with the database
            #     #self._cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def getSuburbId(self, lon, lat):
        sql = """SELECT id FROM suburbs where St_Within(St_SetSRID(St_MakePoint(%s,%s), 4326), geom)"""

        try:
            self._cur.execute(sql, (lon, lat))
            rows = self._cur.fetchall()
            #print("The number of parts: ", self._cur.rowcount)
            return rows[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def getSuburbCoordinates(self, lon, lat):

        sql = """SELECT row_to_json(fc)
                     FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
                     FROM (SELECT 'Feature' As type
                        , ST_AsGeoJSON(lg.geom)::json As geometry
                        , row_to_json((id, suburb_name)) As properties
                       FROM suburbs As lg WHERE St_Within(St_SetSRID(St_MakePoint(%s,%s), 4326), lg.geom) ) As f )  As fc"""

        sql2 = """SELECT ST_AsGeoJSON(geom) FROM suburbs where St_Within(St_SetSRID(St_MakePoint(%s,%s), 4326), geom)"""

        try:
            self._cur.execute(sql, (lon, lat))
            rows = self._cur.fetchall()
            # print("The number of parts: ", self._cur.rowcount)
            return rows[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def getMultipleSuburbCoordinates(self, idList):
        sql = """SELECT row_to_json(fc)
                             FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
                             FROM (SELECT 'Feature' As type
                                , ST_AsGeoJSON(lg.geom)::json As geometry
                                , row_to_json((lg.id, loc_pid, suburb_name,ST_AsGeoJSON(ST_Centroid(geom)))) As properties
                               FROM suburbs As lg WHERE lg.id IN %s ) As f )  As fc"""
        try:
            # query_para = ', '.join( '?' * len(idList))
            # print(query_para)

            print(tuple(idList))

            idList = tuple(idList)


            self._cur.execute(sql, (idList,))
            rows = self._cur.fetchall()
            # print("The number of parts: ", self._cur.rowcount)
            print(rows[0])
            return rows[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def getLatestDateTime(self):
        sql = """select max(createtime)::date, extract(hour from max(createtime)) from tweepy """

        try:
            print(sql)
            self._cur.execute(sql)

            rows = self._cur.fetchall()
            # print("The number of parts: ", self._cur.rowcount)
            return rows[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def getTerms(self, suburb_id, date, hour):
        sql = """SELECT suburb_id, string_agg(LTRIM(RTRIM(tokenized,']'), '['),',') AS tokenized_tweepy 
                  FROM tweepy 
                  WHERE extract(hour from createtime) = %s and createtime::date = %s and suburb_id = '%s' and tokenized <> '[]'
                  GROUP BY suburb_id"""

        try:
            print(sql, suburb_id)
            self._cur.execute(sql, ( hour, date, suburb_id))

            rows = self._cur.fetchall()
            # print("The number of parts: ", self._cur.rowcount)
            return rows[0][1]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def getAllTerms(self, date, hour):
        sql = """SELECT suburb_id, string_agg(LTRIM(RTRIM(tokenized,']'), '['),',') AS tokenized_tweepy 
                          FROM tweepy 
                          WHERE extract(hour from createtime) = %s and createtime::date = %s and tokenized <> '[]'
                          GROUP BY suburb_id"""

        try:

            self._cur.execute(sql, (hour, date))

            rows = self._cur.fetchall()
            # print("The number of parts: ", self._cur.rowcount)

            # gather all suburbs within an arr and gather all terms
            result = {}
            result['document'] = []
            result['words'] = ""

            for row in rows:
                document = {}
                document['suburb_id'] = row[0]
                #document['hour'] = row[1]
                document['terms'] = row[1]
                result['document'].append(document)
                result['words'] += ("," + row[1])

            print(len(result['words'].split(',')))

            return result


        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
