#!/usr/bin/env python3
###############################################################################
#
#  Project:  NSRS-2022-PROJ
#  Purpose:  Download needef files from NOAA/NGS to buile nsrs aux db
#  Author:   Javier Jimenez Shaw
#
###############################################################################
#  Copyright (c) 2026, Javier Jimenez Shaw
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

from urllib.request import urlretrieve

urls = [
    "https://beta.ngs.noaa.gov/SPCS/json_data/zoneBounds.json",
    "https://beta.ngs.noaa.gov/SPCS/json_data/zoneDefinitions.json",
    "https://beta.ngs.noaa.gov/NATRF2022/epp2022-beta-values.csv",
    "https://beta.ngs.noaa.gov/NAPGD2022/data/geoid2022/GEOID2022.beta_v0a.ggxf",
]

print("Generate empty_aux_db.sql with `projinfo --dump-db-structure`")
for url in urls:
    name = url.split("/")[-1]
    print(f"Downloading {url}")
    urlretrieve(url, name)

print("Done")
