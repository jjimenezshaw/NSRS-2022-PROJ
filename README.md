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
