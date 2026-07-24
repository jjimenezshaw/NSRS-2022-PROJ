import os
import math
import numpy as np
from osgeo import gdal, osr
from datetime import datetime

gdal.UseExceptions()

def get_safe_scale_offset(vmin, vmax, is_velocity):
    """
    Computes a scale and offset mapping [vmin, vmax] to Int16 [-32767, 32767],
    rounding the scale UP to 3 significant digits to avoid overflow.
    """
    offset = (vmax + vmin) / 2.0
    
    # If geoidHeight and offset is near 0, force it to 0
    if is_velocity:
        offset = round(offset, 6)
    elif abs(offset) > 2.0:
        offset = round(offset, 3)
    else:
        offset = 0.0

    max_dist = max(abs(vmax - offset), abs(vmin - offset))
    ideal_scale = max_dist / 32767.0 if max_dist > 0 else 1.0
    
    if ideal_scale == 0:
        return 1.0, offset
        
    exponent = math.floor(math.log10(ideal_scale))
    magnitude = 10 ** (2 - exponent) 
    safe_scale = math.ceil(ideal_scale * magnitude) / magnitude
    
    return safe_scale, offset

def process_ggxf_to_multipage_tiff(in_ggxf, out_tiff, do_scale):
    
    # Updated descriptions and regions (GC is Guam/CNMI)
    target_layers = [
        {
            "path": "//SGEOID2022/NA/geoidHeight",
            "area": "North America",
            "desc": "Undulation (North America)"
        },
        {
            "path": "//SGEOID2022/GC/geoidHeight",
            "area": "Guam and CNMI",
            "desc": "Undulation (Guam and CNMI)"
        },
        {
            "path": "//SGEOID2022/AS/geoidHeight",
            "area": "American Samoa",
            "desc": "Undulation (American Samoa)"
        },
        {
            "path": "//DGEOID2022/GL/geoidVelocity",
            "area": "Global",
            "desc": "Undulation velocity"
        }
    ]

    main_ds = gdal.Open(in_ggxf)
    meta = main_ds.GetMetadata()
    source_crs_wkt = meta.get("sourceCrsWkt", "")
    
    srs = osr.SpatialReference()
    if "ITRF2020" in source_crs_wkt:
        srs.ImportFromEPSG(9990)
        proj_wkt = srs.ExportToWkt()
    else:
        proj_wkt = source_crs_wkt
        
    driver = gdal.GetDriverByName("GTiff")
    
    if os.path.exists(out_tiff):
        os.remove(out_tiff)

    for i, layer_info in enumerate(target_layers):
        layer_path = layer_info["path"]
        print(f"Processing: {layer_path}...")
        
        sds_name = f'HDF5:"{in_ggxf}":{layer_path}'
        sds = gdal.Open(sds_name)
        data = sds.ReadAsArray()
        n_rows, n_cols = data.shape
        
        # Flip data (Bottom-Left origin to Top-Left origin)
        data = np.flipud(data)
        
        parts = layer_path.strip("/").split("/")
        prefix = f"{parts[0]}_{parts[1]}"
        affine_str = meta.get(f"{prefix}_affineCoeffs")
        lat0, dlat, _, lon0, _, dlon = map(float, affine_str.split())
        
        # Calculate Geotransform
        lat_max_center = lat0 + (n_rows - 1) * dlat
        tl_lon = lon0 - (dlon / 2.0)
        tl_lat = lat_max_center + (dlat / 2.0)
        geotransform = [tl_lon, dlon, 0.0, tl_lat, 0.0, -dlat]
        
        is_velocity = "geoidVelocity" in layer_path
        nodata_val = -32768
        if do_scale:
            vmin = float(np.nanmin(data))
            vmax = float(np.nanmax(data))
            scale, offset = get_safe_scale_offset(vmin, vmax, is_velocity)
            
            data_scaled = np.round((data - offset) / scale)
            data_int16 = np.where(np.isnan(data), nodata_val, data_scaled).astype(np.int16)
            print(offset, scale)
            print(vmax, vmin)
            print(np.ceil((vmax-offset)/scale), np.floor((vmin-offset)/scale))
        
        options = [
            "COMPRESS=DEFLATE",
            f"PREDICTOR={2 if do_scale else 3}",
            "TILED=YES"
        ]
        if i > 0:
            options.append("APPEND_SUBDATASET=YES")
            
        out_ds = driver.Create(out_tiff, n_cols, n_rows, 1, gdal.GDT_Int16 if do_scale else gdal.GDT_Float32, options=options)
        
        out_ds.SetGeoTransform(geotransform)
        if proj_wkt:
            out_ds.SetProjection(proj_wkt)
            
        # -- Dataset Level Metadata --
        out_ds.SetMetadataItem("AREA_OR_POINT", "Point")
        out_ds.SetMetadataItem("area_of_use", layer_info["area"])
        out_ds.SetMetadataItem("grid_name", layer_info["desc"])
        
        today = datetime.today().strftime('%Y-%m-%d')
        now = datetime.today().strftime('%Y:%m:%d %H:%M:%S')
        out_ds.SetMetadataItem("TIFFTAG_IMAGEDESCRIPTION", f"ITRF2020 (EPSG:9990) to NAPGD2022. Converted from {in_ggxf} (last modified at {today})")
        out_ds.SetMetadataItem("TIFFTAG_DATETIME", f"{now}")
        out_ds.SetMetadataItem("TIFFTAG_COPYRIGHT", "Derived from work by NGS/NOAA. CC-BY 4.0.")
        out_ds.SetMetadataItem("target_crs_epsg_code", "*NAPGD2022*")
        out_ds.SetMetadataItem("TYPE", "VELOCITY" if is_velocity else "VERTICAL_OFFSET_GEOGRAPHIC_TO_VERTICAL")

        # -- Band Level Metadata --
        band = out_ds.GetRasterBand(1)
        band.WriteArray(data_int16 if do_scale else data)
        band.SetNoDataValue(nodata_val)
        band.SetDescription("up_velocity" if is_velocity else "geoid_undulation")
        band.SetUnitType("metres per year" if is_velocity else "metre")
        if do_scale:
            band.SetScale(scale)
            band.SetOffset(offset)

        out_ds = None
        sds = None
        
    print(f"\nExtraction complete. Output written to {out_tiff}")


if __name__ == "__main__":
    INPUT_GGXF = "GEOID2022.beta_v0a.ggxf"
    OUTPUT_TIFF = "us_noaa_geoid2022_beta_v0a.tif"
    
    do_scale = True

    process_ggxf_to_multipage_tiff(INPUT_GGXF, OUTPUT_TIFF, do_scale)
