#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# create reports of camera statuses
#
# Parameters
#   none
# 
# Consumes
#   stacks and allsky maps from individual cameras, plus the timestamp of upload
#
# Produces
#   a webpage showing the list of cameras, colourcoded by status
#       https://archive.ukmeteornetwork.co.uk/reports/statrep.html
#   a webpage showing the latest stack and map from each camera
#       https://archive.ukmeteornetwork.co.uk/latest/index.html
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB
logger -s -t cameraStatusReport "starting"

cp $TEMPLATES/header.html $DATADIR/reports/statrep.html
echo "<h3>Camera status report for the network.</h3> <p>This page provides a status report " >> $DATADIR/reports/statrep.html
echo "on the feed of daily data from cameras in the network. RMS cameras are reported red if more than three days " >> $DATADIR/reports/statrep.html
echo "late. UFO cameras are reported red if more than 14 days late." >> $DATADIR/reports/statrep.html
echo "The date & time are that of the start of the last data capture run recieved." >> $DATADIR/reports/statrep.html
echo "</p><p>The exact upload time of each camera is available <a href="./stationlogins.txt">here</a>". >> $DATADIR/reports/statrep.html
echo "</p><p>Note that ukmonlive data is not included in this report.</p>" >> $DATADIR/reports/statrep.html
echo "<div id=\"camrep\" class=\"table-responsive\"></div>" >> $DATADIR/reports/statrep.html
echo "<script src=\"./camrep.js\"></script>" >> $DATADIR/reports/statrep.html
cat $TEMPLATES/footer.html >> $DATADIR/reports/statrep.html

python -m reports.cameraStatusReport 

aws s3 cp $DATADIR/reports/statrep.html $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/reports/camrep.js $WEBSITEBUCKET/reports/ --quiet

logger -s -t cameraStatusReport "finished"

#$SRC/website/createLatestTable.sh