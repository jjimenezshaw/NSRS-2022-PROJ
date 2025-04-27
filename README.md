# NSRS-2022-PROJ
Auxiliary DB for PROJ with alpha and beta data from NATRF2022 and friends.


## Modernized National Spatial Reference System
USA, Canada and Mexico are modernizing their spatial reference systems.
For more information, go to their webpages.
[PROJ](https://proj.org) will include that information once it is published by the [EPSG](https://epsg.org).
In the mean time this auxiliary database can be useful to test some of the funcionalities.
See that anything that needs a change in PROJ's source code cannot be tested until that feature is developed.


## Scope
This repository tries to create an auxiliary database (complementary to `proj.db`) that includes some (all?) of the reference systems and transformations from the "Modernized National Spatial Reference System", also known as `NATRF2022` (among others).

This project is done as a helper and exercise.
Not as a definitive tool for production products.
See it as a beta version that will never be released.
(PROJ may include whatever from EPSG, but not from this repository).
There is no liability from the usage of this code or data.
The code and data may be changed at any point without advise.

Hopefuly this repository will allow PROJ users to familiaize with the new system.
You can give feedback to the NGS via ngs.feedback@noaa.gov

THE SOFTWARE AND DATA IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.


## Source
Data was obtained from https://alpha.ngs.noaa.gov/


## Auxiliary database
You can use the environment variable `PROJ_AUX_DB` to specify an auxiliary database to PROJ:
https://proj.org/en/stable/usage/environmentvars.html#envvar-PROJ_AUX_DB

The db produced in this repo will define an "authority", `NSRS` (but it may change).
That will produce the CRS `NSRS:NATRF2022_2D` as something similar to `EPSG:6318`.
Yes, the ID can use letters in PROJ (not in EPSG).


## What is included
I hope I keep this list updated:
 - Geographic CRSs for `{N,P,C,M}ATRF2022` in the 3 flavours: geocentric, geographic 3D and 2D.
 - Vertical systems `NAPGD2022 height` and `NAPGD2022 height (ft)`.
 - Transformations from `ITRF2020` to `{N,P,C,M}ATRF2022` using a Helmert transformation with the `EPP`.
 - `SGEOID2022 North America` as GeoTIFF. It is stored as `int16` to make is smaller than 100MB. The max error is 1.1 mm. (no velocities included!)
 - Transformation from `ITRF2020` to `NAPGD2022 height` using that geoid model and linear interpolation.
 - All state planes from `SPCS2022` in meters and international feet.


 ## Files
 The main output files are `nsrs_proj.db` and `us_noaa_sgeoid2022_na_v1a.tif`:
  - `nsrs_proj.db`: auxiliary database to be used with PROJ
  - `us_noaa_sgeoid2022_na_v1a.tif`: geoid model file with SGEOID2022 for North America (also accesible remotely with the proper configuration)


If you want to run the scripts to generate everything yourself you will need more files, like 
 - `empty_aux_db.sql`: generate with `projinfo --dump-db-structure > empty_aux_db.sql`
 - `zoneDefinitions.json` and `GEOID2022.v1.a.ggxf`: downloand from NGS webpage.


## Examples


projinfo:
```
PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db projinfo NSRS:NATRF2022_2D
PROJ.4 string:
+proj=longlat +ellps=GRS80 +no_defs +type=crs

WKT2:2019 string:
GEOGCRS["NATRF2022",
    DYNAMIC[
        FRAMEEPOCH[2020]],
    DATUM["North American Terrestrial Reference Frame 2022",
        ELLIPSOID["GRS 1980",6378137,298.257222101,
            LENGTHUNIT["metre",1]]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["geodetic latitude (Lat)",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["geodetic longitude (Lon)",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    USAGE[
        SCOPE["Not known."],
        AREA["World."],
        BBOX[-90,-180,90,180]],
    ID["NSRS","NATRF2022_2D"],
    REMARK["NATRF2022"]]
```

Show WKT of a State Plane:
```
PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db projinfo NSRS:GULF -o WKT1_GDAL -q
PROJCS["NATRF2022 / Gulf",
    GEOGCS["NATRF2022",
        DATUM["North American Terrestrial Reference Frame 2022",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            AUTHORITY["NSRS","NATRF2022_datum"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["NSRS","NATRF2022_2D"]],
    PROJECTION["Lambert_Conformal_Conic_1SP"],
    PARAMETER["latitude_of_origin",27.75],
    PARAMETER["central_meridian",-90],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",1524000],
    PARAMETER["false_northing",457200],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH],
    AUTHORITY["NSRS","GULF"]]
```

Transform from ITRF2020 with a different epoch:
```
echo 50 -70 0 2030 | PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db cs2cs NSRS:NATRF2022_2D ITRF2020 -d 9
50.000000565	-70.000002398 0.000208146 2030
```

Use geoid model locally:
```
echo 50 -70 0 | PROJ_DATA=`projinfo --searchpaths | sed -zE 's/[\r\n]+/:/g'`:./NSRS-2022-PROJ/ PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db cs2cs NSRS:NATRF2022_2D+NAPGD2022 NSRS:NATRF2022_3D -d 9
50.000000000	-70.000000000 -26.198699954
```

Use geoid model via NETWORK (there is an issue that forces the usage of PROJ_NETWORK_ENDPOINT):
```
echo 50 -70 0 | PROJ_NETWORK_ENDPOINT=https://jjimenezshaw.github.io/NSRS-2022-PROJ/ PROJ_NETWORK=ON PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db cs2cs NSRS:NATRF2022_2D+NAPGD2022 NSRS:NATRF2022_3D -d 9
50.000000000	-70.000000000 -26.198699954
```
