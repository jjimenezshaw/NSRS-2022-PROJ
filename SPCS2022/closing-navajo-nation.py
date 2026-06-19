import os
import pathlib
import processing  # type: ignore  # module from PyQGIS
from qgis.core import QgsProject, QgsVectorLayer, QgsProviderRegistry

"""
Why are we doing this?

Navajo Nation area is like a checkerboard:
'That describes areas where every other PLSS section is privately owned,
with the others owned by a government agency.
Each section is nominally one mile square, hence the checkerboard look.
This was commonly done along ~40 mile-wide swaths centered on major railroad corridors,
particularly in the western U.S.
Apparently this was done as part of granting land to the railroad barons of the late 1800s,
to give them land but to prevent them from having too much control.'

This script simplifies it applying a positive and negative buffer, to "absorv" those squares.
"""

def process_and_export_geojson():
    # Inputs and parameters
    CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
    input_file = os.path.join(CURRENT_DIR, 'output', 'special_use_rest.geojson')
    output_file = os.path.join(CURRENT_DIR, 'output', 'special_use.geojson')
    threshold_distance = 0.04 

    # Load the original GeoJSON layer
    metadata = QgsProviderRegistry.instance().providerMetadata('ogr')
    sublayers = metadata.querySublayers(input_file)
    original_name = sublayers[0].name() if sublayers else 'Simplified'
    layer = QgsVectorLayer(input_file, original_name, 'ogr')
    if not layer.isValid():
        print("Error: Could not load the layer. Check the input file path.")
        return

    # Extract Navajo Nation
    print("Extracting Navajo Nation...")
    navajo_layer = processing.run("native:extractbyexpression", {
        'INPUT': layer,
        'EXPRESSION': "\"NameFull\" = 'Navajo Nation'",
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Extract the rest of the features
    print("Extracting the rest of the features...")
    rest_layer = processing.run("native:extractbyexpression", {
        'INPUT': layer,
        'EXPRESSION': "\"NameFull\" != 'Navajo Nation' OR \"NameFull\" IS NULL",
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Positive Buffer (Navajo Nation)
    print("Running positive buffer...")
    buffered = processing.run("native:buffer", {
        'INPUT': navajo_layer,
        'DISTANCE': threshold_distance,
        'SEGMENTS': 5,
        'END_CAP_STYLE': 2, # Flat/Square
        'JOIN_STYLE': 1,    # Miter
        'MITER_LIMIT': 2,
        'DISSOLVE': True,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Negative Buffer (Navajo Nation)
    print("Running negative buffer...")
    closed = processing.run("native:buffer", {
        'INPUT': buffered,
        'DISTANCE': -threshold_distance,
        'SEGMENTS': 5,
        'END_CAP_STYLE': 2,
        'JOIN_STYLE': 1,
        'MITER_LIMIT': 2,
        'DISSOLVE': False,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Collect Geometries (forces MultiPolygon)
    print("Ensuring MultiPolygon output...")
    multi_geom_layer = processing.run("native:collect", {
        'INPUT': closed,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Merge simplified Navajo Nation with the rest of the elements
    print("Merging features...")
    merged_temp = processing.run("native:mergevectorlayers", {
        'LAYERS': [multi_geom_layer, rest_layer],
        'CRS': layer.crs(), 
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Drop 'path' and 'layer' fields
    print("Removing 'path' and 'layer' fields and saving to GeoJSON...")
    final_temp = processing.run("native:deletecolumn", {
        'INPUT': merged_temp,
        'COLUMN': ['path', 'layer'],
        'OUTPUT': 'TEMPORARY_OUTPUT',
    })['OUTPUT']

    # Save GeoJSON
    processing.run("native:savefeatures", {
        'INPUT': final_temp,
        'OUTPUT': output_file,
        'LAYER_NAME': layer.name(),
        'LAYER_OPTIONS': 'RFC7946=YES;COORDINATE_PRECISION=5'
    })

    # Load the final saved GeoJSON into QGIS so you can inspect it
    final_loaded_layer = QgsVectorLayer(output_file, 'Closed Navajo Nation', 'ogr')
    if final_loaded_layer.isValid():
        QgsProject.instance().addMapLayer(final_loaded_layer)
        print(f"Processing complete! File saved successfully to: {output_file}")
    else:
        print("Processing finished, but could not load the final file into QGIS.")

# Run the function
process_and_export_geojson()
