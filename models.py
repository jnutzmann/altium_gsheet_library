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


from .altium import ALTIUM_SPECIAL_FIELDS


class Category:

    def __init__(self, name, row_count):
       
        self.name = name
        self.row_count = row_count
        self.fields = []
        self.link_counts = 0
        self.raw_rows = None


    def add_field(self, field):
       
        if field.link:
            self.link_counts += 1
            field.link_index = self.link_counts
        self.fields.append(field)


    def get_missing_required_fields(self, custom_req_fields):
        
        # TODO: add custom required fields from config file.
        required_fields = ['Component ID'] + ALTIUM_SPECIAL_FIELDS + custom_req_fields
        missing_fields = []
        
        for rf in required_fields:
            found = False
            for f in self.fields:
                if rf == f.altium_name:
                    found = True
                    break
            
            if not found:
                missing_fields.append(rf)

        return missing_fields


    def field_index(self, field_database_name):

        for i in range(len(self.fields)):
            if self.fields[i].database_name == field_database_name:
                return i
        return -1


    # TODO: make sure we sanitize inputs.
    def generate_create_table(self):
         
        query = "CREATE TABLE `%s` (id INT NOT NULL AUTO_INCREMENT," % (self.name)

        for f in self.fields:

            if f.database_name == 'component_id':
                query += 'component_id CHAR(36) CHARACTER SET ascii NOT NULL,'
            elif f.link:
                query += "ComponentLink%iDescription CHAR(%i) DEFAULT '%s'," \
                    % (f.link_index, len(f.altium_name), f.altium_name)
                query += 'ComponentLink%iURL VARCHAR(255),' % f.link_index
                f.database_name = 'ComponentLink%iURL' % f.link_index
            else:
                query += "`%s` VARCHAR(255)," % f.database_name

        query += "PRIMARY KEY (id));"

        return query

class Field:
    
    def __init__(self, sheet_name):
        self.altium_name = sheet_name.strip().replace('*','').replace('^','')
        self.database_name = self.altium_name.lower().replace(' ', '_')
        self.visibleOnAdd = sheet_name.find('*') > -1
        self.link = sheet_name.find('^') > -1
        self.link_index = -1

    def __repr__(self) -> str:
        return ("%s (%s) - %s, %s" % (self.database_name, self.altium_name, 
                                      self.visibleOnAdd, self.link))