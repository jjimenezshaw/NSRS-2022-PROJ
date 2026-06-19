import os
import pathlib
import processing  # type: ignore  # module from PyQGIS
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem


def geojson_path(layer_name):
    safe_file_name = layer_name.replace(' - ', '_').replace(' ', '_').lower()
    path = os.path.join(OUTPUT_DIR, f"{safe_file_name}.geojson")
    return path


# ==========================================
# --- CONFIGURATION ---
# ==========================================
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
INPUT_LAYER_NAME = 'SPCS2022_All_953_zones_FINAL_shapefile — SPCS2022_All_953_zones_FINAL.shp'
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'output') # Directory where all files will be saved

SIMPLIFY_THRESHOLD = 0.01

# Define each output layer name and its exact extraction expression.
OUTPUT_ZONES = {
    'Statewide': "\"ZoneType\" = 'Statewide'",
    'Multizone complete': "\"ZoneType\" = 'Multizone complete'",
    'Multizone partial': "\"ZoneType\" = 'Multizone partial'",
    'Special use - Gulf': "\"ZoneType\" = 'Special use' AND \"NameFull\" = 'Gulf'",
    'Special use - Rest': "\"ZoneType\" = 'Special use' AND coalesce(\"NameFull\", '') != 'Gulf'"
}
# ==========================================

# Setup paths and Data Cleanup
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

gpkg1_path = os.path.join(OUTPUT_DIR, 'filtered_zones.gpkg')
gpkg2_path = os.path.join(OUTPUT_DIR, 'simplified_zones.gpkg')

print("Performing pre-run cleanup...")

# Remove matching layers from the QGIS Canvas to release file locks
for layer_name in OUTPUT_ZONES.keys():
    existing_layers = QgsProject.instance().mapLayersByName(layer_name)
    for layer in existing_layers:
        QgsProject.instance().removeMapLayer(layer.id())

# Define files to delete
files_to_delete = [gpkg1_path, gpkg2_path]
for layer_name in OUTPUT_ZONES.keys():
    files_to_delete.append(geojson_path(layer_name))

# Delete files from disk
for file_path in files_to_delete:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"  -> Deleted old file: {os.path.basename(file_path)}")
        except PermissionError:
            print(f"  -> WARNING: Could not delete {os.path.basename(file_path)}. It may be open in another program.")

print("-" * 50)


# Get input layer
layer_list = QgsProject.instance().mapLayersByName(INPUT_LAYER_NAME)
if not layer_list:
    raise ValueError(f"Layer '{INPUT_LAYER_NAME}' not found. Please load it into QGIS first.")
input_layer = layer_list[0]

print(f"Starting process. Input layer has {input_layer.featureCount()} total features.\n")
print("-" * 50)

total_features = input_layer.featureCount()
computed_features = 0

# Process each defined output zone
for layer_name, expression in OUTPUT_ZONES.items():
    print(f"Processing Layer: {layer_name}")

    # Filter by Expression and save to the First Geopackage
    gpkg1_output = f"ogr:dbname='{gpkg1_path}' table=\"{layer_name}\" (geom)"

    processing.run("native:extractbyexpression", {
        'INPUT': input_layer,
        'EXPRESSION': expression,
        'OUTPUT': gpkg1_output
    })

    extracted_layer = QgsVectorLayer(f"{gpkg1_path}|layername={layer_name}", layer_name, "ogr")
    print(f"  -> Extracted to GPKG 1: {extracted_layer.featureCount()} features.")

    # Fix Geometries
    fixed_result = processing.run("native:fixgeometries", {
        'INPUT': extracted_layer,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })
    fixed_layer = fixed_result['OUTPUT']

    # Coverage Simplify and save to Second Geopackage
    gpkg2_output = f"ogr:dbname='{gpkg2_path}' table=\"{layer_name}\" (geom)"

    processing.run("native:coveragesimplify", {
        'INPUT': fixed_layer,
        'TOLERANCE': SIMPLIFY_THRESHOLD,
        'OUTPUT': gpkg2_output
    })

    simplified_layer = QgsVectorLayer(f"{gpkg2_path}|layername={layer_name}", layer_name, "ogr")
    print(f"  -> Simplified to GPKG 2: {simplified_layer.featureCount()} features.")
    
    # Overwrite CRS to EPSG:4326, to avoid unneeded transformation.
    noop_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    simplified_layer.setCrs(noop_crs)

    geojson = geojson_path(layer_name)
    processing.run("native:savefeatures", {
        'INPUT': simplified_layer,
        'OUTPUT': geojson,
        'LAYER_NAME': layer_name,
        'LAYER_OPTIONS': 'RFC7946=YES;COORDINATE_PRECISION=5'
    })

    # Load back into QGIS
    final_layer = QgsVectorLayer(geojson, layer_name, "ogr")
    print(f"  -> Exported clean GeoJSON: {final_layer.featureCount()} features.")
    QgsProject.instance().addMapLayer(final_layer)
    computed_features += final_layer.featureCount()

    print("-" * 50)

if total_features == computed_features:
    print(f"All {total_features} features processed")
else:
    print(f"ERROR: {total_features} features expected but {computed_features} processed")

print("Done")
