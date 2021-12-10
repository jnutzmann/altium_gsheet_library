# MIT License
#
# Copyright 2021 Jonathan Nutzmann
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.


import mariadb


class LibraryDatabase:

    def __init__(self, database_config):

        self._config = database_config

        try:
            self._conn = mariadb.connect(
                user=database_config['user'],
                password=database_config['password'],
                host=database_config['host'],
                port=int(database_config['port']),
                database=database_config['database']
            )
        except mariadb.Error as e:
            raise Exception("Error connecting to specified database.")

        # Get Cursor
        self._cursor = self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def execute(self, query):
        return self._cursor.execute(query)

    def dropAllTables(self):
        query  = "SELECT CONCAT('DROP TABLE IF EXISTS `', table_name, '`;') "
        query += "FROM information_schema.tables "
        query += "WHERE table_schema = '%s';" % self._config['database']

        self._cursor.execute(query)
        drop_statements = self._cursor.fetchall()

        for q in drop_statements:
            self._cursor.execute(q[0])

        return len(drop_statements)

    def getConnectionString(self):
        return ('Driver={MySQL ODBC 8.0 Unicode Driver};SERVER=%s;USER=%s;'
                'PASSWORD=%s;DATABASE=%s;PORT=%s' % 
                (self._config['host'], self._config['user'],
                 self._config['password'], self._config['database'],
                 self._config['port']))

    def close(self):
        self._conn.close()