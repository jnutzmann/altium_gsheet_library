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

class SyncConfig:

    def __init__(self, config_file):
        self._config = configparser.ConfigParser()
        self._config.read_file(config_file)
        self.validate()

    def print_config(self):
        for c in self._config:
            print(c)
            print('=====')
            for f in self._config[c]:
                print(f + ': ' + self._config[c][f])
            print('')

    def get(self, category):
        return self._config[category]

    def validate(self):
        require = {
            'database': ['user','password','host','port','database'], 
            'gsheet': ['sheet_id', 'secret_file', 'custom_required_fields'],
            'altium': ['dblib_file']
        }

        for r in require:
            if r not in self._config:
                raise Exception('Missing category %s in config file.' % r)
            
            for f in require[r]:
                if f not in self._config[r]:
                    raise Exception('Missing field %s in %s of config file.' 
                                    % (f,r))
