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

import argparse

from .altium import generateDbLibFile
from .database import LibraryDatabase
from .gsheet import GSheetReader
from .sync_config import SyncConfig


def sync(config_file, field_populators=[]):

    print('[1/8] Reading config file: %s' % config_file.name)
    sync_config = SyncConfig(config_file)

    database_config = sync_config.get('database')
    print('[2/8] Connecting to database %s@%s:%s (%s)... ' % 
        (database_config['user'], database_config['host'],
        database_config['port'], database_config['database']
    ), end='', flush=True)
    db = LibraryDatabase(database_config)
    print('Connected.')

    try:
        print('[3/8] Connecting to Google sheet... ', end='', flush=True)
        gsReader = GSheetReader(sync_config.get('gsheet'))
        print('Connected.')
       
        print('[4/8] Reading & validating schema from Google sheet... ', 
              end='', flush=True)
        count = gsReader.readAndValidateCategories()
        print('Found %i valid categories.' % count)


        print('[5/8] Droping current library tables... ', end='', flush=True)
        count = db.dropAllTables()
        print('Dropped %i tables.' % count)

        print('[6/8] Creating new schema... ', end='', flush=True)
        for c in gsReader.categories:
            query = gsReader.categories[c].generate_create_table()
            db.execute(query)
        print('Created %i new tables.' % len(gsReader.categories))

        print('[7/8] Adding Components to database... ', end='', flush=True)
        count = gsReader.addComponentsToDatabase(db, field_populators=field_populators)
        print('Added %i components to database.' % count)

        print('[8/8] Updating DbLib file... ', end='', flush=True)
        generateDbLibFile(gsReader.categories, db.getConnectionString(), 
        sync_config.get('altium')['dblib_file'])
        print('Done.')

    finally:
        db.close()
        print('Done!! Closed DB connection.')


# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(
#         description='Sync altium library from target gSheet.')

#     parser.add_argument('--config', type=argparse.FileType('r'), nargs='?',
#                         metavar='c', default='config.ini',
#                         help='Configuration file for sync.')
#     args = parser.parse_args()

#     sync(args.config)