#!/bin/bash

# bash script to create index page for an individual orbit report

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/orbitsolver.ini > /dev/null 2>&1

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}

idxfile=${results}/${yr}/orbits/${yr}${mth}/$1/index.shtml
repf=`ls -1 ${results}/${yr}/orbits/${yr}$mth/${ym}/$yr*report.txt`
repfile=`basename $repf`
pref=${repfile:0:16}

echo "<html><head><title>Orbit Report for $ym</title>" > $idxfile
echo "<style>img {  border-radius: 5%;   border: 1px solid #555; }</style> </head>" >> $idxfile
echo "<body><h1>Orbital Analysis for matched events on $ym</h1>" >> $idxfile
echo "<pre><!--#include file=\"summary.html\" --></pre>" >>$idxfile
echo "<h3>Click on an image to see a larger view</h3>" >> $idxfile

echo "<a href=\"${pref}orbit_top.png\"><img src=\"${pref}orbit_top.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}orbit_side.png\"><img src=\"${pref}orbit_side.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}ground_track.png\"><img src=\"${pref}ground_track.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}velocities.png\"><img src=\"${pref}velocities.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile

ls -1 ${results}/${yr}/orbits/${yr}$mth/${ym}/*.jpg | while read jpg 
do
    jpgbn=`basename $jpg`
    echo "<a href=\"$jpgbn\"><img src=\"$jpgbn\" width=\"20%\"></a>" >> $idxfile
done
echo "<br>">>$idxfile

echo "<p>More graphs below the text report<br></p>" >>$idxfile
echo "<pre><!--#include file=\"$repfile\" --></pre>" >>$idxfile
echo "<a href=\"${pref}lengths.png\"><img src=\"${pref}lengths.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}lags_all.png\"><img src=\"${pref}lags_all.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag.png\"><img src=\"${pref}abs_mag.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag_ht.png\"><img src=\"${pref}abs_mag_ht.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile
echo "<a href=\"${pref}all_spatial_residuals.png\"><img src=\"${pref}all_spatial_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}total_spatial_residuals_length_grav.png\"><img src=\"${pref}total_spatial_residuals_length_grav.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_angular_residuals.png\"><img src=\"${pref}all_angular_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_spatial_total_residuals_height.png\"><img src=\"${pref}all_spatial_total_residuals_height.png\" width=\"20%\"></a>" >> $idxfile

echo "</body></html>" >> $idxfile

