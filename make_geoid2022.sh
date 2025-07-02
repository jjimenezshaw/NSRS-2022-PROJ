#!/usr/bin/env sh

# https://beta.ngs.noaa.gov/NAPGD2022/data/geoid2022/GEOID2022.beta_v0.ggxf
SRC="GEOID2022.beta_v0.ggxf"
DST="us_noaa_sgeoid2022_na_beta_v0.tif"
gdal_translate -if netcdf NETCDF:"${SRC}":"/SGEOID2022/NA/geoidHeight" \
    -of gtiff sgeoid2022_na.tmp.tiff \
    -a_gt -190.00833333333333 0.016666666666667 0 90.00833333333334 0 -0.016666666666667 -a_srs EPSG:9990

gdal_calc.py -A sgeoid2022_na.tmp.tiff --outfile=sgeoid2022_na.tmp2.tiff --calc="A/0.0022" --type=Int16 --overwrite
rm sgeoid2022_na.tmp.tiff
gdal_translate -ot int16 -a_nodata -32768 -a_scale 0.0022 \
    -co compress=deflate -co predictor=2 -co tiled=yes \
    -mo "TIFFTAG_DATETIME=`date +"%Y:%m:%d 00:00:00"`" \
    -mo AREA_OR_POINT=Point -mo TYPE=VERTICAL_OFFSET_GEOGRAPHIC_TO_VERTICAL \
    -mo "TIFFTAG_COPYRIGHT=Derived from work by NOAA" \
    -mo "TIFFTAG_IMAGEDESCRIPTION=ITRF2020 (EPSG:9990) to NAPGD2022. Only SGEOID2022 component. Stored as int16 to make it smaller. Converted from ${SRC} North America" \
    -mo target_crs_epsg_code=NAPGD2022 \
    sgeoid2022_na.tmp2.tiff ${DST}
rm sgeoid2022_na.tmp2.tiff

gdalinfo ${DST}
