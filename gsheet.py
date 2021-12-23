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


import json
import uuid

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from .models import Category, Field


class GSheetReader:

    COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(self, gsheet_config):
        # use creds to create a client to interact with the Google Drive API
        creds = ServiceAccountCredentials.from_json_keyfile_name(
                    gsheet_config['secret_file'], 
                    ['https://www.googleapis.com/auth/spreadsheets']) # scope

        service = build('sheets', 'v4', credentials=creds)
        self._sheet = service.spreadsheets()

        self._config = gsheet_config

    def readAndValidateCategories(self): 

        sheet_metadata = self._sheet.get(
            spreadsheetId=self._config['sheet_id']).execute()

        self.categories = {}

        for s in sheet_metadata['sheets']:
            category_name = s['properties']['title']
            row_count = s['properties']['gridProperties']['rowCount']
            self.categories[category_name] = Category(category_name, row_count)


        for c in self.categories:
            header_row = self._sheet.values().get(
                spreadsheetId=self._config['sheet_id'], 
                range='%s!1:1' % c).execute().get('values')[0]

            for h in header_row:
                self.categories[c].add_field(Field(h))


        invalid_categories = []

        for c in self.categories: 

            if 'custom_required_fields' in self._config:
                custom_req = json.loads(self._config['custom_required_fields'])
            else:
                custom_req = []
            
            missing_fields = self.categories[c].get_missing_required_fields(
                custom_req
            )

            if len(missing_fields) > 0:
                invalid_categories.append(c)
                raise Exception(
                    'Category "%s" is missing field(s): %s, removing from list.'
                    % (c, missing_fields))

        return len(self.categories)

    def addComponentsToDatabase(self, database, field_populators=[]):

        new_id_count = 0
        component_count = 0

        for c in self.categories:
            parts_rows = self._sheet.values().get(
                spreadsheetId=self._config['sheet_id'], range='%s!2:%i' 
                    % (c, self.categories[c].row_count)).execute().get('values')
    
            componet_id_index = self.categories[c].field_index('component_id')

            for row_index in range(len(parts_rows)):
                if (len(parts_rows[row_index]) == 0):
                    continue
                
                if parts_rows[row_index][componet_id_index] == '':
                    new_uuid = uuid.uuid4()
                    self._sheet.values().update(
                        spreadsheetId=self._config['sheet_id'], 
                        range='%s!%s%i' 
                        % (c, GSheetReader.COLUMN_NAMES[componet_id_index], 
                            row_index+2), valueInputOption='RAW',
                            body={'values':[[str(new_uuid)]]}).execute()

                    print('\n -> Assigned Component ID "%s" for row %i in category "%s"' 
                            % (new_uuid, row_index+2, c), end='', flush=True)

                    parts_rows[row_index][componet_id_index] = str(new_uuid)
                    new_id_count += 1

                for f in field_populators:
                    val, update_index = f(self.categories[c], parts_rows[row_index])
                    if update_index >= 0:
                        self._sheet.values().update(
                            spreadsheetId=self._config['sheet_id'], 
                            range='%s!%s%i' 
                            % (c, GSheetReader.COLUMN_NAMES[update_index], 
                                row_index+2), valueInputOption='RAW',
                                body={'values':[[str(val)]]}).execute()
                        parts_rows[row_index][update_index] = str(val)
                    
                # TODO: sanitize inputs
                query = "INSERT INTO `%s` (" % c

                for field_index in range(len(parts_rows[row_index])):
                    query += "`%s`," % self.categories[c].fields[field_index].database_name

                query = query[:-1] + ') VALUES ('

                for column_index in range(len(parts_rows[row_index])):
                    query += "'%s'," % parts_rows[row_index][column_index]

                query = query[:-1] + ');'
        
                database.execute(query)
                component_count += 1
        
        database.commit()
        
        print('')
        
        return component_count