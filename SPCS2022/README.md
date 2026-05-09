# SPCS2022
This folder is not to be used with PROJ. There is no need for the auxiliary database.
However it is useful data to know the area of use of the different State Planes defined in SPCS2022.

The GeoJSON files are created out of the shapefile included in the folder (provided by the NOAA/NGS).
The polygons are simplified to produce a much smaller file. Note that it may change some borders.

Explore the different zones in [spcs2022.html](https://jjimenezshaw.github.io/NSRS-2022-PROJ/SPCS2022/spcs2022.html) Click on the zones to get more detailed information.


## Classification
State planes in SPCS2022 are clasified in 4 types:
 - Statewide: selfexplanatory.
 - Multizone Complete: Subdivision of a state that covers completely the state.
 - Multizone Partial: Subdivision of a state that covers only partially its surface.
 - Spatial Use:
    - Kansas City, because it is over two states.
    - Navajo Nation, because it is over three states.
    - Gulf area (there are two GeoJSON files to be able to select the bigger zone).

Some states may have complete and partial zones.

## Why that many?
The main purpose for those many state planes is to minimize the projection distortion at the topographic surface.
That requires not very big areas of use and proper projection parameters.
They try to be "LDP" (low distortion projections).

The attribute `DesignBy` shows who designed that state plane, NGS or the respective state.
