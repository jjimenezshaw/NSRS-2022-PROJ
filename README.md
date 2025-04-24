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

## Examples

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

```
echo 50 -70 0 2030 | PROJ_AUX_DB=./NSRS-2022-PROJ/nsrs_proj.db cs2cs NSRS:NATRF2022_2D ITRF2020 -d 9
50.000000565	-70.000002398 0.000208146 2030
```
