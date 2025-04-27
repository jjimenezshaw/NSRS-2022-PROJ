#!/usr/bin/env python3
###############################################################################
#
#  Project:  NSRS-2022-PROJ
#  Purpose:  Build auxiliary db for new SRS from NOAA/NGS
#  Author:   Javier Jimenez Shaw
#
###############################################################################
#  Copyright (c) 2025, Javier Jimenez Shaw
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
###############################################################################

import json
import os
import sqlite3

AUTHORITY = 'NSRS'
TRF = 'TRF2022'
refs = ["NA", "PA", "CA", "MA"]
names = ["North American", "Pacific", "Caribbean", "Mariana"]
PUBLICATION_DATE = "2025-04-22"

script_dir_name = os.path.dirname(os.path.realpath(__file__))

def usage(name, table, area_code=1262):
     #  1262 is World. Without any better option, just use it
     area = f"""
INSERT INTO usage VALUES(
    '{AUTHORITY}','{name}_USAGE','{table}','{AUTHORITY}','{name}','EPSG','{area_code}','EPSG','1024');
"""
     return area


def create_geodetic_datums():
    str = ""
    for ref, name in zip(refs, names):
        id = f'{ref}{TRF}_datum'
        datum = f"""
INSERT INTO geodetic_datum VALUES(
    '{AUTHORITY}','{id}',          -- code
    '{name} Terrestrial Reference Frame 2022',        -- name
    '{name} Terrestrial Reference Frame 2022 datum',  -- description
    'EPSG','7019',  -- ellispoid GRS 80
    'EPSG','8901',  -- prime meridian
    '{PUBLICATION_DATE}',   -- publication date
    2020.0,  -- frame reference epoch
    NULL,    -- ensemble accuracy
    NULL,    -- anchor
    NULL,    -- anchor epoch
    0);"""
        str += datum + usage(id, 'geodetic_datum')
    return str


def create_geodetic_crss():
    str = ""
    types = ["geocentric", "geographic 3D", "geographic 2D"]
    suffixes = ["gc", "3D", "2D"]
    type_codes = [6500, 6423, 6422]
    for type, type_code, suffix in zip (types, type_codes, suffixes):
        for ref in refs:
            id = f'{ref}{TRF}_{suffix}'
            crs = f"""
INSERT INTO geodetic_crs VALUES(
    '{AUTHORITY}','{id}',  -- code
    '{ref}{TRF}',          -- name
    '{ref}{TRF}',          -- description
    '{type}','EPSG','{type_code}', -- {type}
    '{AUTHORITY}','{ref}{TRF}_datum', -- datum
    NULL, -- text definition
    0);"""
            str += crs + usage(id, 'geodetic_crs')
    return str


def create_vertical_datum():
    id = 'NAPGD2022_datum'
    datum = f"""
INSERT INTO vertical_datum VALUES(
    '{AUTHORITY}','{id}',          -- code
    'North American-Pacific Geodetic Datum 2022',  -- name
    NULL,    -- description
    '{PUBLICATION_DATE}',   -- publication date
    2020.0,  -- frame reference epoch
    NULL,    -- ensemble accuracy
    NULL,    -- anchor
    NULL,    -- anchor epoch
    0);"""
    return datum + usage(id, 'vertical_datum')


def create_vertical_crss():
    # vertical in m
    id = 'NAPGD2022'
    crs = f"""
INSERT INTO vertical_crs VALUES(
    '{AUTHORITY}','{id}',            -- code
    'NAPGD2022 height',              -- name
    NULL,                            -- description
    'EPSG', '6499',                  -- vertical m
    '{AUTHORITY}','NAPGD2022_datum', -- datum
    0);"""
    str = crs + usage(id, 'vertical_crs')

    # vertical in ft
    id = 'NAPGD2022_ft'
    crs = f"""
INSERT INTO vertical_crs VALUES(
    '{AUTHORITY}','{id}',            -- code
    'NAPGD2022 height (ft)',         -- name
    NULL,                            -- description
    'EPSG', '1030',                  -- vertical ft
    '{AUTHORITY}','NAPGD2022_datum', -- datum
    0);"""
    str += crs + usage(id, 'vertical_crs')

    return str

def create_vertical_transformations():
    id = 'ITRF2020_to_NAPGD2022'
    in_file = 'GEOID2022.v1.a.ggxf'
    out_file = 'us_noaa_sgeoid2022_na_v1a.tif'
    # that trigger checks the existence of some things... that are in proj.db but not here.
    # so far we just delete the trigger.
    delete_trigger = """
DROP TRIGGER grid_transformation_insert_trigger;"""
    str = f"""
INSERT INTO grid_transformation VALUES(
    '{AUTHORITY}','{id}','ITRF2020 to NAPGD2022 height',NULL,
    'EPSG','9665','Geographic3D to GravityRelatedHeight (gtx)',
    'EPSG','9989', -- source CRS (ITRF2020)
    '{AUTHORITY}','NAPGD2022', -- target CRS (NAPGD2022 height)
    NULL,  -- accuracy
    'EPSG','8666','Geoid (height correction) model file','GEOID2022.v1.a.ggxf',
    NULL,NULL,NULL,NULL,
    NULL,NULL,NULL,0);"""

    alternative = f"""
INSERT INTO grid_alternatives VALUES(
    '{in_file}','{out_file}',NULL,'GTiff','geoid_like',0,NULL,'https://jjimenezshaw.github.io/NSRS-2022-PROJ/{out_file}',1,1,NULL);
"""

    return delete_trigger + str + usage(id, 'grid_transformation') + alternative


def create_itrf2020_transformations():
    epps = {
        "NA": (0.051, -0.736, -0.024),
        "PA": (-0.409, 1.047, -2.169),
        "CA": (-0.039, -0.974, 0.611),
        "MA": (-8.089, 5.937, 2.159)
    }
    str = ""
    for key, value in epps.items():
        str += create_itrf2020_transformation(key + TRF, *value)
    return str

def create_itrf2020_transformation(ref, x, y, z):
    transf = f"""
INSERT INTO helmert_transformation
    ("auth_name", "code", "name", "description", "method_auth_name", "method_code", "method_name",
    "source_crs_auth_name", "source_crs_code", "target_crs_auth_name", "target_crs_code", 
    "accuracy", 
    "tx", "ty", "tz", "translation_uom_auth_name", "translation_uom_code", 
    "rx", "ry", "rz", "rotation_uom_auth_name", "rotation_uom_code", 
    "scale_difference", "scale_difference_uom_auth_name", "scale_difference_uom_code", 
    "rate_tx", "rate_ty", "rate_tz", "rate_translation_uom_auth_name", "rate_translation_uom_code", 
    "rate_rx", "rate_ry", "rate_rz", "rate_rotation_uom_auth_name", "rate_rotation_uom_code", 
    "rate_scale_difference", "rate_scale_difference_uom_auth_name", "rate_scale_difference_uom_code", 
    "epoch", "epoch_uom_auth_name", "epoch_uom_code", 
    "px", "py", "pz", "pivot_uom_auth_name", "pivot_uom_code", "operation_version", 
    "deprecated") 
    VALUES ('{AUTHORITY}', 'ITRF2020_to_{ref}', 'ITRF2020 to {ref}', 'from https://alpha.ngs.noaa.gov/EPP/index.shtml', 
    'EPSG', '1056', 'Time-dependent Coordinate Frame rotation (geocen)',
    'EPSG', '9988', '{AUTHORITY}', '{ref}_gc', 
    '0.01', -- accuracy
    '0', '0', '0', 'EPSG', '1025',
    '0', '0', '0', 'EPSG', '1031',
    '0', 'EPSG', '1028',
    '0', '0', '0', 'EPSG', '1027',
    '{x}', '{y}', '{z}', 'EPSG', '1032', -- milliarc-seconds per year
    '0', 'EPSG', '1030',
    '2020.0', 'EPSG', '1029',
    '', '', '', '', '', '',
    '0');"""
    return transf + usage(f'ITRF2020_to_{ref}', 'helmert_transformation')

def make_conversion(e, code, name, type, feet=False):
    suffix = "_ft" if feet else ""
    unit = "(ift)" if feet else "(m)"
    unit_code = 9002 if feet else 9001
    str = ""

    padding = "NULL," * 10 # for TM.
    padding12 = "NULL," * 12 # for LC1 

    lat = e["Origin latitude (deg)"]
    lon = e["Origin longitude west (deg)"]
    k = e["Projection origin scale"]
    easting = e[f"False easting {unit}"].replace(",","")
    northing = e[f"False northing {unit}"].replace(",","")
    azimuth = e["Skew azimuth (deg)"]

    if type == "LC1":

        str = f"""
INSERT INTO conversion VALUES (
    '{AUTHORITY}', '{code}{suffix}', '{name} {unit}', '{e['Zone code']}',
    'EPSG', '9801', 'Lambert Conic Conformal (1SP)',
    'EPSG', '8801', 'Latitude of natural origin', {lat}, 'EPSG', '9102',
    'EPSG', '8802', 'Longitude of natural origin', {lon}, 'EPSG', '9102',
    'EPSG', '8805', 'Scale factor at natural origin', {k}, 'EPSG', '9201',
    'EPSG', '8806', 'False easting', {easting}, 'EPSG', '{unit_code}',
    'EPSG', '8807', 'False northing', {northing}, 'EPSG', '{unit_code}',
    {padding12}
    0);"""

    elif type == "TM":

        str = f"""
INSERT INTO conversion_table VALUES (
    '{AUTHORITY}', '{code}{suffix}', '{name} {unit}', '{e['Zone code']}',
    'EPSG', '9807',
    'EPSG', '8801', {lat}, 'EPSG', '9102',
    'EPSG', '8802', {lon}, 'EPSG', '9102',
    'EPSG', '8805', {k}, 'EPSG', '9201',
    'EPSG', '8806', {easting}, 'EPSG', '{unit_code}',
    'EPSG', '8807', {northing}, 'EPSG', '{unit_code}',
    {padding}
    0);"""

    elif type == "OMC":

        str = f"""
INSERT INTO conversion_table VALUES (
    '{AUTHORITY}', '{code}{suffix}', '{name} {unit}', '{e['Zone code']}',
    'EPSG', '9815',
    'EPSG', '8811', {lat}, 'EPSG', '9102',
    'EPSG', '8812', {lon}, 'EPSG', '9102',
    'EPSG', '8813', {azimuth}, 'EPSG', '9102',
    'EPSG', '8814', {azimuth}, 'EPSG', '9102',
    'EPSG', '8815', {k}, 'EPSG', '9201',
    'EPSG', '8816', {easting}, 'EPSG', '{unit_code}',
    'EPSG', '8817', {northing}, 'EPSG', '{unit_code}',
    0);"""
    return str


def make_projected(e, code, name, feet=False):
    suffix = "_ft" if feet else ""
    unit = " (ft)" if feet else ""
    cs = 4495 if feet else 4499
    ref = e["Reference frame"]
    id = f'{code}{suffix}'
    str = f"""
INSERT INTO projected_crs VALUES (
    '{AUTHORITY}', '{id}', '{ref} / {name}{unit}', '{e['Zone code']}',
    'EPSG', '{cs}',
    '{AUTHORITY}', '{ref}_2D',
    '{AUTHORITY}', '{code}{suffix}', NULL,
    0);"""
    return str + usage(id, 'projected_crs')


def create_spcss():
    # https://alpha.ngs.noaa.gov/SPCS/json_data/zoneDefinitions.json
    # To check: https://alpha.ngs.noaa.gov/SPCS/json_data/coordinates.json
    definitions = os.path.join(script_dir_name, 'zoneDefinitions.json')
    if not os.path.exists(definitions):
        raise Exception("Download file https://alpha.ngs.noaa.gov/SPCS/json_data/zoneDefinitions.json")
    with open(definitions) as defs:
        d = json.load(defs)
    str = ""
    for e in d:
        code = e['Zone abrv']
        name = e['Zone name']
        type = e['Proj type']
        conv_m = make_conversion(e, code, name, type, feet=False)
        crs_m = make_projected(e, code, name, feet=False)
        str += conv_m + crs_m
        conv_ft = make_conversion(e, code, name, type, feet=True)
        crs_ft = make_projected(e, code, name, feet=True)
        str += conv_ft + crs_ft
    return str


str = "" #f"INSERT INTO builtin_authorities VALUES ('{NSRS_AUTHORITY}');"
str += create_geodetic_datums()
str += create_geodetic_crss()
str += create_vertical_datum()
str += create_vertical_crss()
str += create_vertical_transformations()
str += create_spcss()
str += create_itrf2020_transformations()

empty_filename = os.path.join(script_dir_name, 'empty_aux_db.sql')
if not os.path.exists(empty_filename):
    raise Exception("Generate empty_aux_db.sql with `projinfo --dump-db-structure`")

with open(empty_filename) as empty_db:
    empty_db_sql =  empty_db.read()

db_sql = empty_db_sql + str

sql_filename = os.path.join(script_dir_name, 'nsrs_proj.sql')
with open(sql_filename, 'w') as sql:
    sql.write(db_sql)

nsrs_db = os.path.join(script_dir_name, 'nsrs_proj.db')
if os.path.exists(nsrs_db):
    os.unlink(nsrs_db)
proj_db_conn = sqlite3.connect(nsrs_db)
proj_db_cursor = proj_db_conn.cursor()
proj_db_cursor.executescript(db_sql)

