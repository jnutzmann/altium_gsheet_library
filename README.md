# Altium GSheet Library

## Motivation

This code is designed to make an Altium Designer database-backed library (DbLib)
to store components used in designs.  Out of the box, Altium supports
connections via ODBC to external databases, connections to an Excel file (which 
doesn't work well), or to an Access database (which lives in a file).

To best support multiple users of the database without risking conflicts when
commiting to a version control system, it's best to use a centrally hosted
database that can be simutanously edited.  The downside of this, however,
is that creating a good UI is labor intensive for a MySQL or similar database.  
Additionally the latency of  connection between Altium and a remote database 
can really reduce performance if hosted in the cloud.


## Implementation

This library attempts to provide an easy to implement solution with the data
stored in a Google sheet.  This allows for multiple people to simultanously
edit, as well as provides built-in access control, etc.


### The Google Sheet

The scripts in this file expect the Google Sheet to be set up in a specific way.
First, each component category gets its own tab (for example "Resistor",
"IC/Memory", etc).

![Categories](https://github.com/jnutzmann/altium_gsheet_library/blob/main/docs/categories.png?raw=true | width=100)

Within each tab, fields for the specific component type can be defined.  There
are a few required fields to make the library work correct, but others are left
to the discression of the user.

The required fields are:
- *Component ID* - This is a UUID that is populated by this script when initially
  syncing and is used as the unique id for the specific component.
- *Description* - Description field for the part.
- *Library Ref* - Name of the schematic symbol in the SchLib.
- *Library Path* - Name of the SchLib file where the schematic symbol is located.
- *Footprint Ref* - Name of the footprint in the PcbLib.
- *Footprint Path* - Name of the PcbLib file containing the footprint.

If you would like to enforce additional required fields (like Manufacturer,
Company Part Number, etc), these can be defined in your custom `config.ini` file.

In addition to simply adding fields, there are a few special symbols that can
be appended to end of the field name:
- `*` - Adding this symbol will make the field visible on the schematic when the
  part is added.
- `^` - Adding this symbol will make the field be treated as a link so that
  you can right click on the component and open a link in Altium (like a
  Datasheet)
[Special Char](https://github.com/jnutzmann/altium_gsheet_library/blob/main/docs/special_char.png?raw=true | width=150)

## Setup

### MariaDB

### Google Sheet

### `config.ini`