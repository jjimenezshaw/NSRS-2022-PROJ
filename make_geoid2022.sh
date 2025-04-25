#!/usr/bin/env sh
gdal_translate -if netcdf NETCDF:"GEOID2022.v1.a.ggxf":"/SGEOID2022/North America/geoidHeight" \
    -of gtiff sgeoid2022_na.tmp.tiff \
    -a_gt -190 0.016666666666667 0 90.0 0 -0.016666666666667 -a_srs EPSG:9990

gdal_calc.py -A sgeoid2022_na.tmp.tiff --outfile=sgeoid2022_na.tmp2.tiff --calc="A/0.0022" --type=Int16 --overwrite
rm sgeoid2022_na.tmp.tiff
gdal_translate -ot int16 -a_nodata -32768 -a_scale 0.0022 \
    -co compress=deflate -co predictor=2 -co tiled=yes \
    -mo "TIFFTAG_DATETIME=`date +"%Y:%m:%d 00:00:00"`" \
    -mo AREA_OR_POINT=Point -mo TYPE=VERTICAL_OFFSET_GEOGRAPHIC_TO_VERTICAL \
    -mo "TIFFTAG_COPYRIGHT=Derived from work by NOAA" \
    -mo "TIFFTAG_IMAGEDESCRIPTION=ITRF2020 (EPSG:9990) to NAPGD2022. Only SGEOID2022 component. Stored as int16 to make it smaller. Converted from GEOID2022.v1.a.ggxf North America" \
    -mo target_crs_epsg_code=NAPGD2022 \
    sgeoid2022_na.tmp2.tiff us_noaa_sgeoid2022_na_v1a.tif
rm sgeoid2022_na.tmp2.tiff

gdalinfo us_noaa_sgeoid2022_na_v1a.tif
