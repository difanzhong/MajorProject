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

    def insert_tweet(self, created_at, text, tokenized, s_id):
        """ insert a new vendor into the vendors table """
        sql = """INSERT INTO tweepy (origintext, createtime, tokenized, suburb_id)
                 VALUES(%s, to_timestamp(%s, 'Mon dd hh24:mi:ss yyyy') + make_interval(hours:=10), %s,%s) RETURNING id;"""

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






