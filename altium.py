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


import configparser
from genericpath import isfile
import os

from termcolor import colored


ALTIUM_SPECIAL_FIELDS = ['Description', 'Library Ref', 'Library Path', 
        'Footprint Ref', 'Footprint Path']


def generateDbLibFile(categories, connection_string, filename):

    config = configparser.ConfigParser()

    config['OutputDatabaseLinkFile'] = { 'Version': '1.1' }
    config['DatabaseLinks'] = {
        'ConnectionString': connection_string,
        'AddMode': '3',
        'RemoveMode': '1',
        'UpdateMode': '2',
        'ViewMode': '0',
        'LeftQuote': '`',
        'RightQuote': '`',
        'QuoteTableNames': '1',
        'UseTableSchemaName': '0',
        'DefaultColumnType': 'VARCHAR(255)',
        'LibraryDatabaseType': '',
        'LibraryDatabasePath': '',
        'DatabasePathRelative': '0',
        'TopPanelCollapsed': '0',
        'LibrarySearchPath': 'symbols;footprints',
        'OrcadMultiValueDelimiter': ',',
        'SearchSubDirectories': '0',
        'SchemaName': '',
        'LastFocusedTable': ''
    }

    table_index = 1

    for c in categories:
        config['Table%i' % table_index] = {
            'SchemaName': '',
            'TableName': c,
            'Enabled': 'True',
            'UserWhere': '0',
            'UserWhereText': '',
            'BrowserOrder_Sorting': '',
            'BrowserOrder_Grouping': ''
        }

        table_index += 1

    field_map_index = 1

    for c in categories:

        options = []

        # Add the ID field to every category.  This field is used as the
        # primary key in the database, but is not used anywhere else.
        # We add it here so that the DbLib matches the database.
        options.append('FieldName=%s.id' % c)
        options.append('TableNameOnly=%s' % c)
        options.append('FieldNameOnly=id')
        options.append('FieldType=1')
        options.append('ParameterName=')
        options.append('VisibleOnAdd=False')
        options.append('AddMode=0')
        options.append('RemoveMode=0')
        options.append('UpdateMode=0')

        config['FieldMap%i' % field_map_index] = {
            'Options': '|'.join(options)
        }
        field_map_index += 1


        for f in categories[c].fields:

            options = []

            options.append('FieldName=%s.%s' % (c,f.database_name))
            options.append('TableNameOnly=%s' % c)
            options.append('FieldNameOnly=%s' % f.database_name)
            
            # Use the component_id field as the library key in Altium
            if f.database_name == 'component_id':
                options.append('FieldType=0')
            else:
                options.append('FieldType=1')
            
            
            if f.altium_name in ALTIUM_SPECIAL_FIELDS:
                options.append('ParameterName=[%s]' % f.altium_name)
            
            elif f.link:
                # If we have a link field, we need to add both the URL and the
                # description field.
                options2 = []
                options2.append('FieldName=%s.ComponentLink%iDescription' % (c,f.link_index))
                options2.append('TableNameOnly=%s' % c)
                options2.append('FieldNameOnly=ComponentLink%iDescription' % f.link_index)
                options2.append('FieldType=1')
                options2.append('ParameterName=ComponentLink%iDescription' % f.link_index)
                options2.append('VisibleOnAdd=%s' % False)
                options2.append('AddMode=0')
                options2.append('RemoveMode=0')
                options2.append('UpdateMode=0')

                config['FieldMap%i' % field_map_index] = {
                    'Options': '|'.join(options2)
                }

                field_map_index += 1

                options.append('ParameterName=ComponentLink%iURL' % f.link_index)
            
            else:
                options.append('ParameterName=%s' % f.altium_name)
            
            options.append('VisibleOnAdd=%s' % f.visibleOnAdd)
            options.append('AddMode=0')
            options.append('RemoveMode=0')
            options.append('UpdateMode=0')

            config['FieldMap%i' % field_map_index] = {
                'Options': '|'.join(options)
            }

            field_map_index += 1

    with open(filename, 'w') as f:
        config.write(f)


def getLibraryFiles(alitum_config):
    
    symbol_files = {}
    footprint_files = {}

    try:
        symbol_dir = os.path.join(os.path.dirname(os.path.realpath(alitum_config['dblib_file'])), 'symbols')
        files = os.listdir(symbol_dir)

        for f in files:
            fpath = os.path.join(symbol_dir, f)
            if not os.path.isfile(fpath):
                # ignore subfolders (like History)
                continue

            symbols = []
            with open(fpath, mode='rb') as lib_file:
                contents = str(lib_file.read()).split('|')
                for s in contents:
                    if 'LibReference' in s:
                        symbols.append(s.split('=')[1])
            
            symbol_files[f.lower()] = symbols
    except:
        pass

    try:
        footprint_dir = os.path.join(os.path.dirname(os.path.realpath(alitum_config['dblib_file'])), 'footprints')
        files = os.listdir(footprint_dir)

        for f in files:
            fpath = os.path.join(footprint_dir, f)
            if not os.path.isfile(fpath):
                # ignore subfolders (like History)
                continue

            footprints = []

            with open(fpath, mode='rb') as lib_file:
                contents = str(lib_file.read()).split('|')
                for s in contents:
                    if 'PATTERN' in s:
                        footprints.append(s.split('=')[1])
            
            footprint_files[f.lower()] = footprints
    except:
        pass

    return symbol_files, footprint_files


def fileValidator(symbol_files, footprint_files, categories, rows):

    symbol_path = rows[categories.field_index('library_path')].lower()
    footprint_path = rows[categories.field_index('footprint_path')].lower()

    symbol = rows[categories.field_index('library_ref')]
    footprint = rows[categories.field_index('footprint_ref')]


    category = categories.name
    component_id = rows[categories.field_index('component_id')]

    if symbol_path not in symbol_files:
        print(colored('\n -> Warning: file "%s" not found in symbol folder. (%s:%s)' 
                            % (symbol_path, category, component_id), 'yellow'), end='', flush=True)

    elif symbol not in symbol_files[symbol_path]:
        print(colored('\n -> Warning: file "%s" does not contain the expected symbol "%s". (%s:%s)' 
                        % (symbol_path, symbol, category, component_id), 'yellow'), end='', flush=True)

    if footprint_path not in footprint_files:
        print(colored('\n -> Warning: file "%s" not found in footprint folder. (%s:%s)' 
                            % (footprint_path, category, component_id), 'yellow'), end='', flush=True)
        
    elif footprint not in footprint_files[footprint_path]:
        print(colored('\n -> Warning: file "%s" does not contain the expected footprint "%s". (%s:%s)' 
                        % (footprint_path, footprint, category, component_id), 'yellow'), end='', flush=True)

    # Do not update anything
    return None, -1