#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# consolidate the raw RMS and UFO data. 
#
# Parameters:
#   year to process
#
# Consumes:
#   R05B25 and R91 csv files uploaded from cameras
#   csv files created by the matching engine 
#
# Produces:
#   Updated consolidated ukmon single-event CSV file in standard UFO formats
#   Updated matched data files matches-full-{yr}
#   
# The data are used for downstream processing and reporting

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/${WMPL_ENV}/bin/activate

yr=$1
if [ "$yr" == "" ] ; then
    yr=$(date +%Y)
fi 

cd ${DATADIR}
# consolidate UFO and RMS original CSVs.
logger -s -t consolidateOutput "starting"
aws s3 sync s3://ukmon-shared/consolidated/ ${DATADIR}/consolidated --exclude "temp/*" --quiet
aws s3 mv s3://ukmon-shared/consolidated/temp/ ${DATADIR}/consolidated/temp --recursive --quiet

logger -s -t consolidateOutput "Consolidating RMS and UFO CSVs"
consdir=${DATADIR}/consolidated/temp
mkdir -p ${DATADIR}/single/rawcsvs 
ls -1 $consdir/*.csv | while read csvf
do
    bn=$(basename $csvf)
    typ=${bn:0:3}
    if [ "$typ" != "M20" ] ; then 
        pref="P"
        yr=${bn:7:4}
    else
        pref="M"
        yr=${bn:1:4}
    fi 
    mrgfile=${DATADIR}/consolidated/${pref}_${yr}-unified.csv
    if [ ! -f $mrgfile ] ; then
        cat $csvf >> $mrgfile
    else
        #echo $bn $mrgfile
        sed '1d' $csvf >> $mrgfile
    fi
    mv $csvf ${DATADIR}/single/rawcsvs
done

logger -s -t consolidateOutput "pushing consolidated information back"
aws s3 sync ${DATADIR}/consolidated ${UKMONSHAREDBUCKET}/consolidated/  --exclude 'UKMON*' --quiet 
 
logger -s -t consolidateOutput "Getting latest trajectory data"

# collect the latest trajectory CSV files
# make sure target folders exist
mkdir -p ${DATADIR}/orbits/$yr/fullcsv/processed/ > /dev/null 2>&1

aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/trajectories/${yr}/plots/ $DATADIR/showerplots --exclude "*" --include "0*.png" --quiet

# copy the orbit file for consolidation and reporting
aws s3 mv ${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv/  ${DATADIR}/orbits/${yr}/fullcsv --recursive --exclude "*" --include "*.csv" --quiet

# get the latest matched data generated by WMPL
logger -s -t consolidateOutput "getting matched detections for $yr"
if [ ! -f ${DATADIR}/matched/matches-full-$yr.csv ] ; then 
    cp $SRC/analysis/templates/match_hdr_full.txt ${DATADIR}/matched/matches-full-$yr.csv
fi
logger -s -t consolidateOutput "getting new matched detections for today"
if [ ! -f ${DATADIR}/searchidx/matches-full-$yr-new.csv ] ; then 
    cp $SRC/analysis/templates/match_hdr_full.txt ${DATADIR}/searchidx/matches-full-$yr-new.csv
fi
cat ${DATADIR}/orbits/$yr/fullcsv/$yr*.csv >> ${DATADIR}/matched/matches-full-$yr.csv
cat ${DATADIR}/orbits/$yr/fullcsv/$yr*.csv >> ${DATADIR}/searchidx/matches-full-$yr-new.csv
mv ${DATADIR}/orbits/$yr/fullcsv/$yr*.csv ${DATADIR}/orbits/${yr}/fullcsv/processed

python << EOD3
import pandas as pd 
df = pd.read_csv('${DATADIR}/matched/matches-full-${yr}.csv', skipinitialspace=True)
df = df.drop_duplicates(subset=['_mjd','_sol','_ID1','_ra_o','_dc_o','_amag','_ra_t','_dc_t'])
df.to_csv('${DATADIR}/matched/matches-full-${yr}.csv', index=False)
df = pd.read_csv('${DATADIR}/searchidx/matches-full-${yr}-new.csv', skipinitialspace=True)
df = df.drop_duplicates(subset=['_mjd','_sol','_ID1','_ra_o','_dc_o','_amag','_ra_t','_dc_t'])
df = df.rename(columns={'_m_ut':'_mi_ut'})
df.to_parquet('${DATADIR}/searchidx/matches-full-${yr}-new.parquet.snap', index=False, compression='snappy')
EOD3
rm -f ${DATADIR}/searchidx/matches-full-${yr}-new.csv

python -m converters.toParquet $DATADIR/matched/matches-full-${yr}.csv

aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matched/ --include "*" --exclude "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet 
aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matchedpq/ --quiet --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip"

aws s3 sync $DATADIR/matched/ $WEBSITEBUCKET/browse/parquet/  --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet
aws s3 sync $DATADIR/single/ $WEBSITEBUCKET/browse/parquet/  --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet

logger -s -t consolidateOutput "finished"
